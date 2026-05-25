import numpy as np
from strategy import download_data, run_backtest
from wfa import run_wfa

WEIGHTS = {
    "wfa_efficiency": 0.35,
    "consistency":    0.25,
    "sensitivity":    0.25,
    "drawdown":       0.15,
}

BASE_PARAMS = {"fast_ema": 5, "slow_ema": 20, "rsi_upper": 75}
START_CASH  = 10_000


def score_wfa_efficiency(wfa_df):
    if wfa_df.empty:
        return 0.0
    mean_eff = float(wfa_df["efficiency"].clip(-1, 2).mean())
    return float(np.clip(mean_eff * 50 + 50, 0, 100))


def score_consistency(wfa_df):
    if wfa_df.empty:
        return 0.0
    return float((wfa_df["oos_return_pct"] > 0).mean() * 100)


def score_sensitivity(df, base_ret):
    perturbations = [
        {"fast_ema": 3,  "slow_ema": 20, "rsi_upper": 75},
        {"fast_ema": 8,  "slow_ema": 20, "rsi_upper": 75},
        {"fast_ema": 5,  "slow_ema": 15, "rsi_upper": 75},
        {"fast_ema": 5,  "slow_ema": 26, "rsi_upper": 75},
        {"fast_ema": 5,  "slow_ema": 20, "rsi_upper": 70},
        {"fast_ema": 5,  "slow_ema": 20, "rsi_upper": 80},
    ]
    degradations = []
    for p in perturbations:
        try:
            res = run_backtest(df, **p, start_cash=START_CASH)
            deg = abs(base_ret - res["return_pct"]) / abs(base_ret) if abs(base_ret) > 0.1 else 0.0
            degradations.append(min(deg, 1.0))
        except Exception:
            degradations.append(1.0)
    return float(np.clip((1 - float(np.mean(degradations))) * 100, 0, 100))


def score_drawdown(max_dd_pct):
    return float(np.clip(100 - max_dd_pct * 2.5, 0, 100))


def compute_robustness(df, wfa_df):
    base     = run_backtest(df, **BASE_PARAMS, start_cash=START_CASH)
    base_ret = base["return_pct"]
    base_dd  = base["max_dd_pct"]

    s_wfa  = score_wfa_efficiency(wfa_df)
    s_con  = score_consistency(wfa_df)
    s_sens = score_sensitivity(df, base_ret)
    s_dd   = score_drawdown(base_dd)

    final = (WEIGHTS["wfa_efficiency"] * s_wfa  +
             WEIGHTS["consistency"]    * s_con  +
             WEIGHTS["sensitivity"]    * s_sens +
             WEIGHTS["drawdown"]       * s_dd)

    return {
        "base_return_pct":   round(base_ret, 2),
        "base_max_dd_pct":   round(base_dd,  2),
        "score_wfa_eff":     round(s_wfa,    1),
        "score_consistency": round(s_con,    1),
        "score_sensitivity": round(s_sens,   1),
        "score_drawdown":    round(s_dd,     1),
        "robustness_score":  round(final,    1),
    }


if __name__ == "__main__":
    df = download_data()
    wfa_df = run_wfa(df)
    r = compute_robustness(df, wfa_df)
    print(f"WFA Efficiency (35%) : {r['score_wfa_eff']:.1f}")
    print(f"Consistency    (25%) : {r['score_consistency']:.1f}")
    print(f"Sensitivity    (25%) : {r['score_sensitivity']:.1f}")
    print(f"Drawdown Ctrl  (15%) : {r['score_drawdown']:.1f}")
    print(f"ROBUSTNESS SCORE     : {r['robustness_score']:.1f}")