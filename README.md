pip# Pairs Trading Statistical Arbitrage Strategy

## Overview
This project implements a mean-reversion statistical arbitrage strategy using pairs trading. It identifies cointegrated stock pairs, generates long/short trading signals, and evaluates performance using a fully vectorized backtesting engine.

## Methodology

### 1. Data Collection
- Equity pricing data (Yahoo Finance / Polygon / Quandl)
- Adjusted close used for analysis

### 2. Pair Selection
- Engle-Granger cointegration test
- Rolling spread calculation
- Stationarity check via ADF test

### 3. Signal Generation
Compute spread:

`spread = price_A – beta * price_B`

Normalize using rolling z-score

- Entry: `|z| > 2`
- Exit: `|z| < 0.5`

### 4. Backtesting
- Long/short position rules
- Transaction costs modeled
- Portfolio-level metrics calculated:
  - Sharpe ratio
  - Max drawdown
  - Win rate
  - Annualized return

## Results
_TODO: add results (tickers, dates, costs, metrics, equity curve chart)._

## Technologies
Python, pandas, NumPy, statsmodels, Matplotlib

## Quickstart

### Install
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
pip install -e .

