import os
os.makedirs("output", exist_ok=True)

from strategy   import download_data, run_backtest
from wfa        import run_wfa, compute_wfa_score
from robustness import compute_robustness
from charts     import plot_charts

SYMBOL      = "AAPL"
START_CASH  = 10_000
BASE_PARAMS = {"fast_ema": 5, "slow_ema": 20, "rsi_upper": 75}


def main():
    print("=" * 60)
    print("  Algorithmic Trading Strategy - Full Pipeline")
    print("=" * 60)

    print("\n[1/5] Downloading AAPL data (2015-2025) ...")
    df = download_data(symbol=SYMBOL, start="2015-01-01", end="2025-12-31")
    print(f"      {len(df)} days  |  {df.index[0].date()} to {df.index[-1].date()}")

    print("\n[2/5] Running full-period backtest ...")
    full = run_backtest(df, **BASE_PARAMS, start_cash=START_CASH)
    print(f"      Return : {full['return_pct']:+.1f} %")
    print(f"      Max DD : {full['max_dd_pct']:.1f} %")
    print(f"      Sharpe : {full['sharpe']:.2f}")
    print(f"      Trades : {full['num_trades']}")

    print("\n[3/5] Running Walk-Forward Analysis (takes 5-10 min) ...")
    wfa_df    = run_wfa(df)
    wfa_score = compute_wfa_score(wfa_df)
    wfa_df.to_csv("output/wfa_results.csv", index=False)
    print(f"\n      WFA Score : {wfa_score:.1f}")

    print("\n[4/5] Computing Robustness Score ...")
    rob = compute_robustness(df, wfa_df)
    print(f"      WFA Efficiency (35%) : {rob['score_wfa_eff']:.1f}")
    print(f"      Consistency    (25%) : {rob['score_consistency']:.1f}")
    print(f"      Sensitivity    (25%) : {rob['score_sensitivity']:.1f}")
    print(f"      Drawdown Ctrl  (15%) : {rob['score_drawdown']:.1f}")
    print(f"      ROBUSTNESS SCORE     : {rob['robustness_score']:.1f}  (must be > 75)")

    print("\n[5/5] Generating charts ...")
    try:
        plot_charts(df)
    except Exception as e:
        print(f"      Chart skipped: {e}")

    print()
    print("=" * 52)
    print("  RESULTS SUMMARY")
    print("=" * 52)
    for metric, value in [
        ("Stock Symbol",                 SYMBOL),
        ("Backtest Period",              "2015 - 2025"),
        ("Starting Capital",             f"${START_CASH:,}"),
        ("Percentage Return on Capital", f"{full['return_pct']:+.1f} %"),
        ("Maximum Drawdown",             f"{full['max_dd_pct']:.1f} %"),
        ("Sharpe Ratio",                 f"{full['sharpe']:.2f}"),
        ("Total Trades",                 str(full['num_trades'])),
        ("Walk-Forward Analysis Score",  f"{wfa_score:.1f}"),
        ("Robustness Score",             f"{rob['robustness_score']:.1f}  (> 75)"),
    ]:
        print(f"  {metric:<35} {value}")
    print("=" * 52)

    if rob["robustness_score"] > 75:
        print("\n  PASS - Strategy meets the robustness requirement.")
    else:
        print("\n  FAIL - Paste output here for further help.")


if __name__ == "__main__":
    main()