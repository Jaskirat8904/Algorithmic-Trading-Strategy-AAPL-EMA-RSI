import backtrader as bt
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from strategy import download_data, PandasData

START_CASH = 10_000


def get_equity_curve(df, fast_ema=5, slow_ema=20, rsi_upper=75):
    class Recorder(bt.Strategy):
        params = (('f', fast_ema), ('s', slow_ema), ('r', rsi_upper),
                  ('am', 1.5), ('rp', 0.02))

        def __init__(self):
            self.ef = bt.ind.EMA(period=self.p.f)
            self.es = bt.ind.EMA(period=self.p.s)
            self.cr = bt.ind.CrossOver(self.ef, self.es)
            self.ri = bt.ind.RSI(period=14)
            self.at = bt.ind.ATR(period=14)
            self.st = None
            self.equity = []
            self.dates  = []

        def next(self):
            if not self.position:
                if self.cr[0] > 0 and self.ri[0] < self.p.r:
                    sd = self.p.am * self.at[0]
                    sz = max(1, int(self.broker.getvalue() * self.p.rp / sd))
                    self.st = self.data.close[0] - sd
                    self.buy(size=sz)
            else:
                if self.cr[0] < 0 or self.data.close[0] < self.st:
                    self.sell(size=self.position.size)
                    self.st = None
            self.equity.append(self.broker.getvalue())
            self.dates.append(self.data.datetime.date(0))

    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(START_CASH)
    cerebro.broker.setcommission(0.001)
    cerebro.adddata(PandasData(dataname=df))
    cerebro.addstrategy(Recorder)
    strat = cerebro.run()[0]
    return pd.Series(strat.equity, index=pd.to_datetime(strat.dates))


def plot_charts(df):
    equity = get_equity_curve(df)
    if equity.empty:
        return

    close    = df["Close"].loc[equity.index[0] : equity.index[-1]]
    bh       = (close / close.iloc[0]) * START_CASH
    drawdown = (equity - equity.cummax()) / equity.cummax() * 100

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    fig.patch.set_facecolor("#0f0f0f")
    for ax in (ax1, ax2):
        ax.set_facecolor("#141414")
        ax.tick_params(colors="#aaa")
        for sp in ax.spines.values():
            sp.set_edgecolor("#333")

    ax1.plot(equity.index, equity / START_CASH * 100 - 100,
             color="#4fc3f7", lw=1.5, label="Strategy")
    ax1.plot(bh.index, bh / START_CASH * 100 - 100,
             color="#ffb74d", lw=1.2, ls="--", label="Buy & Hold AAPL", alpha=0.8)
    ax1.axhline(0, color="#555", lw=0.8)
    ax1.set_ylabel("Return (%)", color="#ccc")
    ax1.set_title("AAPL - EMA(5,20) + RSI Strategy vs Buy & Hold (2015-2025)",
                  color="#e0e0e0", pad=12, fontsize=13)
    ax1.legend(facecolor="#1e1e1e", edgecolor="#444", labelcolor="#ccc")

    ax2.fill_between(drawdown.index, drawdown.values, 0, color="#ef5350", alpha=0.6)
    ax2.set_ylabel("Drawdown (%)", color="#ccc")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(color="#aaa")
    plt.tight_layout(pad=2)
    plt.savefig("output/equity_curve.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("Chart saved --> output/equity_curve.png")


if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    plot_charts(download_data())