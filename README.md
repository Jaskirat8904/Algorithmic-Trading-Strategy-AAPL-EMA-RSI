# Algorithmic Trading Strategy Development & Backtesting

## Overview

This project implements a complete algorithmic trading research pipeline using Python and Backtrader for the stock AAPL (Apple Inc.).

The strategy combines:

- EMA crossover momentum signals
- RSI confirmation filter
- ATR-based dynamic stop-loss
- Walk-Forward Analysis (WFA)
- Robustness scoring framework

The objective was not only to generate returns, but to create a strategy that remains stable and explainable across multiple market conditions without overfitting.

---

# Results Summary

| Metric | Value |
|---|---|
| Stock Symbol | AAPL |
| Backtest Period | 2015 – 2025 |
| Starting Capital | $10,000 |
| Percentage Return on Capital | +119.6 % |
| Maximum Drawdown | 15.1 % |
| Sharpe Ratio | 0.70 |
| Total Trades | 62 |
| Walk-Forward Analysis Score | 73.4 |
| Robustness Score | 76.2 (>75) |

---

# Strategy Logic

## Core Idea

The strategy is based on trend-following momentum using exponential moving averages while filtering low-quality entries with RSI confirmation.

### Entry Conditions

A long position is opened when:

1. Fast EMA crosses above Slow EMA
2. RSI is below the overbought threshold

This attempts to capture bullish momentum while avoiding extended overbought rallies.

### Exit Conditions

The position is closed when:

1. Fast EMA crosses below Slow EMA
2. OR price hits ATR-based stop-loss

### Risk Management

Risk is controlled using:

- ATR volatility-adjusted stop-loss
- Fixed percentage portfolio risk per trade
- Dynamic position sizing

This ensures that position size automatically adapts to market volatility.

---

# Indicators Used

| Indicator | Purpose |
|---|---|
| EMA(12) | Short-term momentum |
| EMA(26) | Long-term momentum |
| RSI(14) | Overbought filter |
| ATR(14) | Volatility-adjusted stop-loss |

---

# Project Structure

```text
trading_strategy/
│
├── strategy.py
├── wfa.py
├── robustness.py
├── charts.py
├── main.py
├── requirements.txt
├── README.md
│
└── output/
    ├── equity_curve.png
    └── wfa_results.csv
```

---

# Installation & Setup

## 1. Clone Repository

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd trading_strategy
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Requirements

```text
backtrader==1.9.78.123
yfinance>=0.2.18
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
```

---

# Running the Project

## Run Full Pipeline

```bash
python main.py
```

This command:

1. Downloads historical AAPL data
2. Runs full-period backtest
3. Performs Walk-Forward Analysis
4. Computes Robustness Score
5. Generates charts

---

# Expected Console Output

```text
============================================================
  Algorithmic Trading Strategy - Full Pipeline
============================================================

[1/5] Downloading AAPL data (2015-2025) ...

[2/5] Running full-period backtest ...
      Return : +119.6 %
      Max DD : 15.1 %

[3/5] Running Walk-Forward Analysis ...
      WFA Score : 73.4

[4/5] Computing Robustness Score ...
      ROBUSTNESS SCORE : 76.2

[5/5] Generating charts ...
      Chart saved --> output/equity_curve.png
```

---

# Walk-Forward Analysis (WFA)

## Why WFA Matters

A normal backtest alone is not enough because strategies can become overfitted to historical data.

Walk-Forward Analysis solves this problem by repeatedly:

1. Optimizing on an in-sample period
2. Testing on unseen out-of-sample data
3. Rolling forward through history

This simulates how the strategy would behave in real-world deployment.

---

# WFA Configuration

| Parameter | Value |
|---|---|
| In-Sample Window | 2 Years |
| Out-of-Sample Window | 6 Months |
| Window Step | 6 Months |
| Total WFA Windows | 17 |

---

# WFA Scoring Methodology

The Walk-Forward Analysis Score is computed using:

```text
WFA Score =
60% × (% profitable OOS windows)
+
40% × (mean efficiency mapped to 0-100)
```

Where:

```text
Efficiency = OOS Return / IS Return
```

Final WFA Score:

```text
73.4 / 100
```

---

# Robustness Score Methodology

The robustness score combines four independent stability metrics.

## Formula

```text
Robustness Score =
0.35 × WFA Efficiency
+
0.25 × Consistency
+
0.25 × Sensitivity
+
0.15 × Drawdown Control
```

---

## Components

### 1. WFA Efficiency (35%)

Measures how well performance holds up out-of-sample compared to in-sample.

Higher degradation = lower score.

---

### 2. Consistency (25%)

Measures percentage of profitable out-of-sample windows.

Consistent profitability across windows is rewarded.

---

### 3. Parameter Sensitivity (25%)

Tests whether small parameter changes destroy strategy performance.

Stable strategies should behave similarly under nearby parameter values.

---

### 4. Drawdown Control (15%)

Rewards strategies with controlled losses.

Lower drawdown = higher score.

---

# Robustness Breakdown

| Component | Score |
|---|---|
| WFA Efficiency | 68.7 |
| Consistency | 76.5 |
| Sensitivity | 94.7 |
| Drawdown Control | 62.1 |
| Final Robustness Score | 76.2 |

The strategy successfully exceeded the assignment requirement of robustness > 75.

---

# Output Files

After running the pipeline:

| File | Description |
|---|---|
| output/equity_curve.png | Equity curve + drawdown chart |
| output/wfa_results.csv | Detailed WFA results |

---

# Key Learnings

This assignment helped me learn:

- Backtrader framework architecture
- Walk-Forward Analysis methodology
- Parameter robustness testing
- Risk-adjusted strategy evaluation
- Importance of avoiding overfitting
- Building reproducible research pipelines

One major insight was that a strategy with moderate but stable returns is significantly more valuable than an overfitted strategy showing unrealistic performance.

---

# Notes

- Historical data source: Yahoo Finance via yfinance
- Commission model: 0.1% per trade
- Timeframe: Daily candles
- Instrument: AAPL

---

# Repository Access

After creating the private GitHub repository:

1. Add collaborator:
   `markheris34-svg`

2. Submit:
   - Percentage Return on Capital
   - Maximum Drawdown
   - Walk-Forward Analysis Score
   - GitHub Repository URL

---

# Disclaimer

This project is for educational and research purposes only and does not constitute financial advice.
