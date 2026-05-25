import backtrader as bt
import yfinance as yf
import pandas as pd


class PandasData(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('open',     'Open'),
        ('high',     'High'),
        ('low',      'Low'),
        ('close',    'Close'),
        ('volume',   'Volume'),
        ('openinterest', None),
    )


class EMARSIStrategy(bt.Strategy):
    params = (
        ('fast_ema',   5),
        ('slow_ema',  20),
        ('rsi_period',14),
        ('rsi_upper', 75),
        ('atr_period',14),
        ('atr_mult',  1.5),
        ('risk_pct',  0.02),
    )

    def __init__(self):
        self.fast  = bt.ind.EMA(period=self.p.fast_ema)
        self.slow  = bt.ind.EMA(period=self.p.slow_ema)
        self.cross = bt.ind.CrossOver(self.fast, self.slow)
        self.rsi   = bt.ind.RSI(period=self.p.rsi_period)
        self.atr   = bt.ind.ATR(period=self.p.atr_period)
        self.stop_price = None

    def next(self):
        if not self.position:
            if self.cross[0] > 0 and self.rsi[0] < self.p.rsi_upper:
                risk_amount = self.broker.getvalue() * self.p.risk_pct
                stop_dist   = self.p.atr_mult * self.atr[0]
                size        = max(1, int(risk_amount / stop_dist))
                self.stop_price = self.data.close[0] - stop_dist
                self.buy(size=size)
        else:
            if self.cross[0] < 0 or self.data.close[0] < self.stop_price:
                self.sell(size=self.position.size)
                self.stop_price = None


def download_data(symbol="AAPL", start="2015-01-01", end="2025-12-31"):
    df = yf.download(symbol, start=start, end=end, auto_adjust=True, progress=False)
    df.dropna(inplace=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def run_backtest(df, fast_ema=5, slow_ema=20, rsi_period=14,
                 rsi_upper=75, start_cash=10_000.0):
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(start_cash)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.adddata(PandasData(dataname=df))
    cerebro.addstrategy(
        EMARSIStrategy,
        fast_ema=fast_ema,
        slow_ema=slow_ema,
        rsi_period=rsi_period,
        rsi_upper=rsi_upper,
    )
    cerebro.addanalyzer(bt.analyzers.Returns,      _name="returns")
    cerebro.addanalyzer(bt.analyzers.DrawDown,     _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio,  _name="sharpe",
                        timeframe=bt.TimeFrame.Days,
                        annualize=True, riskfreerate=0.04)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

    strat      = cerebro.run()[0]
    ret_pct    = strat.analyzers.returns.get_analysis().get("rtot", 0) * 100
    dd_pct     = strat.analyzers.drawdown.get_analysis().get("max", {}).get("drawdown", 0)
    sharpe     = strat.analyzers.sharpe.get_analysis().get("sharperatio", 0) or 0
    num_trades = strat.analyzers.trades.get_analysis().get("total", {}).get("total", 0)

    return {
        "return_pct":  ret_pct,
        "max_dd_pct":  dd_pct,
        "sharpe":      sharpe,
        "num_trades":  num_trades,
        "final_value": cerebro.broker.getvalue(),
    }


if __name__ == "__main__":
    df  = download_data()
    res = run_backtest(df, start_cash=10_000)
    print(f"Return      : {res['return_pct']:+.1f} %")
    print(f"Max Drawdown: {res['max_dd_pct']:.1f} %")
    print(f"Sharpe      : {res['sharpe']:.2f}")
    print(f"Trades      : {res['num_trades']}")
    print(f"Final Value : ${res['final_value']:,.2f}")