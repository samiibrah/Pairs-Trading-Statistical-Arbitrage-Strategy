## **Pairs Trading Statistical Arbitrage Strategy**

### **Overview**

This project implements a mean-reversion statistical arbitrage strategy using pairs trading. It identifies cointegrated stock pairs, generates long/short trading signals, and evaluates performance using a fully vectorized backtesting engine.

### **Methodology**

### **1. Data Collection**

- Equity pricing data (Yahoo Finance / Polygon / Quandl)
- Adjusted close used for analysis

### **2. Pair Selection**

- Engle-Granger cointegration test
- Rolling spread calculation
- Stationarity check via ADF test

### **3. Signal Generation**

- Compute spread:
    
    `spread = price_A – beta * price_B`
    
- Normalize using rolling z-score
- Entry: |z| > 2
- Exit: |z| < 0.5

### **4. Backtesting**

- Long/short position rules
- Transaction costs modeled
- Portfolio-level metrics calculated:
    - Sharpe ratio
    - Max drawdown
    - Win rate
    - Annualized return

### **Results**

*(You’ll add charts and metrics once you run your model.)*

### **Technologies**

Python, pandas, NumPy, statsmodels, Matplotlib
