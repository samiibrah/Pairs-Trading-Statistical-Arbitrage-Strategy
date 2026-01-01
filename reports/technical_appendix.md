# Technical Appendix — Pairs Trading Statistical Arbitrage

## 1. Data Preparation

Price data is sourced using standard market data APIs and stored as adjusted close prices.

```python
import yfinance as yf

prices = yf.download(
    ["NVDA", "JPM"],
    start="2018-01-01",
    end="2024-01-01"
)["Adj Close"].dropna()
````

---

## 2. Cointegration Testing

Pair selection uses the Engle–Granger two-step method.

```python
from statsmodels.tsa.stattools import coint

score, pvalue, _ = coint(prices["NVDA"], prices["JPM"])

print(f"Cointegration p-value: {pvalue:.4f}")
```

Pairs with low p-values are candidates for trading, but this alone is not sufficient.

---

## 3. Hedge Ratio Estimation

The hedge ratio β is estimated using linear regression.

```python
import statsmodels.api as sm

X = sm.add_constant(prices["JPM"])
model = sm.OLS(prices["NVDA"], X).fit()
beta = model.params[1]
```

---

## 4. Spread and Z-Score Calculation

```python
spread = prices["NVDA"] - beta * prices["JPM"]

rolling_mean = spread.rolling(window=60).mean()
rolling_std = spread.rolling(window=60).std()

z_score = (spread - rolling_mean) / rolling_std
```

---

## 5. Trading Signal Logic

```python
entry_long = z_score < -2
entry_short = z_score > 2
exit_signal = abs(z_score) < 0.5
```

Positions are long the spread when undervalued and short when overvalued.

---

## 6. Backtesting Engine

```python
positions = pd.Series(0, index=z_score.index)
positions[entry_long] = 1
positions[entry_short] = -1
positions[exit_signal] = 0
positions = positions.ffill()
```

Returns are calculated using spread changes and position direction.

---

## 7. Performance Metrics

```python
import numpy as np

returns = positions.shift(1) * spread.diff()
equity_curve = (1 + returns.fillna(0)).cumprod()

sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
max_drawdown = (equity_curve / equity_curve.cummax() - 1).min()
```

---

## 8. Visualizations

### Spread and Z-Score

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12,4))
plt.plot(z_score)
plt.axhline(2, linestyle="--")
plt.axhline(-2, linestyle="--")
plt.title("Spread Z-Score")
plt.show()
```

### Equity Curve

```python
plt.figure(figsize=(12,4))
plt.plot(equity_curve)
plt.title("Equity Curve")
plt.show()
```

---

## 9. Failure Analysis

Key reasons for underperformance:

* Weak spread stationarity
* Static hedge ratios
* Extended non-mean-reverting regimes
* Lack of volatility or regime filters

---

## 10. Future Enhancements

* Rolling or Kalman-filter hedge ratios
* Walk-forward backtesting
* Volatility-adjusted position sizing
* Portfolio-level risk constraints
* Regime detection and filtering

---

## Final Notes

This appendix is intended to demonstrate **implementation depth** and is a learning exercise for me. The project emphasizes critical thinking around quantitative finance assumptions and highlights common pitfalls in statistical arbitrage strategies.

```
