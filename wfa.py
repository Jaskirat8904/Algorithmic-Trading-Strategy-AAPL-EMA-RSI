import pandas as pd
import numpy as np
import itertools
from strategy import download_data, run_backtest

PARAM_GRID = {
    "fast_ema":  [3, 5, 8],
    "slow_ema":  [15, 20, 26],
    "rsi_upper": [70, 75, 80],
}

IS_YEARS    = 2
OOS_MONTHS  = 6
WARMUP_DAYS = 60
START_CASH  = 10_000


def best_params_on_window(df_is):
    best_ret, best_params = -np.inf, {}
    for fast, slow, rsi_up in itertools.product(
            PARAM_GRID["fast_ema"],
            PARAM_GRID["slow_ema"],
            PARAM_GRID["rsi_upper"]):
        if fast >= slow:
            continue
        try:
            res = run_backtest(df_is, fast_ema=fast, slow_ema=slow,
                               rsi_upper=rsi_up, start_cash=START_CASH)
            if res["return_pct"] > best_ret:
                best_ret    = res["return_pct"]
                best_params = {"fast_ema": fast, "slow_ema": slow,
                               "rsi_upper": rsi_up}
        except Exception:
            continue
    return best_params


def run_wfa(df):
    records      = []
    window_start = df.index[0]
    end          = df.index[-1]
    window_num   = 0

    while True:
        is_end    = window_start + pd.DateOffset(years=IS_YEARS)
        oos_start = is_end + pd.Timedelta(days=1)
        oos_end   = oos_start + pd.DateOffset(months=OOS_MONTHS)

        if oos_end > end:
            break

        df_is        = df.loc[window_start : is_end]
        warmup_start = oos_start - pd.Timedelta(days=WARMUP_DAYS)
        df_oos       = df.loc[warmup_start : oos_end]

        if len(df_is) < 60 or len(df_oos) < 40:
            window_start += pd.DateOffset(months=OOS_MONTHS)
            continue

        window_num += 1
        print(f"  Window {window_num}: IS {window_start.date()}-->{is_end.date()}"
              f"  |  OOS {oos_start.date()}-->{oos_end.date()}", end=" ... ")

        params = best_params_on_window(df_is)
        if not params:
            print("skipping")
            window_start += pd.DateOffset(months=OOS_MONTHS)
            continue

        is_res  = run_backtest(df_is,  **params, start_cash=START_CASH)
        oos_res = run_backtest(df_oos, **params, start_cash=START_CASH)

        efficiency = (oos_res["return_pct"] / is_res["return_pct"]
                      if abs(is_res["return_pct"]) > 0.1 else 0.0)

        print(f"IS={is_res['return_pct']:+.1f}%  "
              f"OOS={oos_res['return_pct']:+.1f}%  "
              f"eff={efficiency:.2f}")

        records.append({
            "window":         window_num,
            "is_start":       window_start.date(),
            "is_end":         is_end.date(),
            "oos_start":      oos_start.date(),
            "oos_end":        oos_end.date(),
            "best_fast":      params.get("fast_ema"),
            "best_slow":      params.get("slow_ema"),
            "best_rsi":       params.get("rsi_upper"),
            "is_return_pct":  round(is_res["return_pct"],  2),
            "oos_return_pct": round(oos_res["return_pct"], 2),
            "efficiency":     round(efficiency, 3),
        })

        window_start += pd.DateOffset(months=OOS_MONTHS)

    return pd.DataFrame(records)


def compute_wfa_score(wfa_df):
    if wfa_df.empty:
        return 0.0
    positive_oos = (wfa_df["oos_return_pct"] > 0).mean() * 100
    mean_eff     = float(wfa_df["efficiency"].clip(-1, 2).mean())
    score        = 0.60 * positive_oos + 0.40 * (mean_eff * 50 + 50)
    return round(float(np.clip(score, 0, 100)), 1)


if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    df = download_data()
    wfa_df = run_wfa(df)
    print(wfa_df.to_string(index=False))
    print(f"\nWFA Score : {compute_wfa_score(wfa_df):.1f}")
    wfa_df.to_csv("output/wfa_results.csv", index=False)