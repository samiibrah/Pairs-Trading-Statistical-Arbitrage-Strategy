# Pairs Trading Statistical Arbitrage Strategy

## Overview

This project implements and evaluates a **mean-reversion statistical arbitrage strategy** using pairs trading. The objective is to identify pairs of equities with stable long-term relationships, exploit short-term deviations from equilibrium, and assess whether cointegration-based strategies generate sustainable risk-adjusted returns.

The system includes:
- Pair selection using econometric tests
- Signal generation via normalized spread deviations
- A fully vectorized backtesting engine
- Performance evaluation with risk metrics

The results demonstrate that **cointegration alone is insufficient for profitable trading**, highlighting the importance of robustness checks, adaptive modeling, and risk management.

---

## Strategy Motivation

Pairs trading seeks to exploit **relative mispricing** between two historically related assets rather than predicting absolute market direction. By maintaining a market-neutral long/short posture, the strategy aims to reduce exposure to broad market movements.

However, real-world performance depends on:
- Stability of the price relationship
- Persistence of mean-reversion
- Robust execution under changing market regimes

This project evaluates these assumptions empirically.

---

## Methodology

### 1. Data Collection
- Historical adjusted close prices are used
- Prices are aligned and cleaned to remove missing observations

### 2. Pair Selection
- Candidate pairs are tested using the **Engle–Granger cointegration test**
- Pairs with statistically significant cointegration are selected

### 3. Spread Construction
For a pair of assets A and B:

spread = price_A − β × price_B 

where β is estimated via linear regression.

### 4. Signal Generation
- Spread is normalized using a rolling z-score
- Entry: |z| > 2
- Exit: |z| < 0.5

### 5. Backtesting
- Long/short positions are simulated
- Portfolio equity, returns, and risk metrics are tracked
- Transaction costs can be optionally modeled

---

## Results Summary

Backtests on cointegrated pairs (e.g., NVDA–JPM, AMZN–META) showed:

- Negative annualized returns
- Low or negative Sharpe ratios
- Large drawdowns
- Win rates below 50%

Despite passing cointegration tests, many spreads failed stationarity checks, leading to weak or nonexistent mean-reversion.

---

## Key Findings

- Cointegration does not guarantee tradable mean-reversion
- Static hedge ratios degrade performance over time
- Regime shifts significantly impact spread dynamics
- Risk management is critical for statistical arbitrage

---

## Limitations

- No walk-forward validation
- Static hedge ratios
- Limited universe of assets
- Simplified transaction cost assumptions

---

## Conclusion

This project demonstrates both the **appeal and fragility** of classical pairs trading strategies. While theoretically grounded, naive implementations often fail under realistic market conditions. The findings emphasize the need for adaptive modeling, rigorous validation, and strong risk controls when deploying statistical arbitrage systems.

---

## Repository Structure

.
├── data/
├── notebooks/
├── src/
├── backtests/
├── plots/
├── REPORT.md
└── TECHNICAL_APPENDIX.md
