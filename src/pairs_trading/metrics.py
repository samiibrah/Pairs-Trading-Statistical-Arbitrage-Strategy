from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252

def equity_curve(returns: pd.Series, start: float = 1.0) -> pd.Series:
    r = returns.fillna(0.0)
    curve = (1.0 + r).cumprod() * start
    curve.name = "equity"
    return curve

def annualized_return(returns: pd.Series) -> float:
    r = returns.dropna()
    if len(r) == 0:
        return np.nan
    curve = (1.0 + r).prod()
    years = len(r) / TRADING_DAYS
    return float(curve ** (1 / years) - 1)

def sharpe_ratio(returns: pd.Series) -> float:
    r = returns.dropna()
    if len(r) < 2:
        return np.nan
    mu = r.mean() * TRADING_DAYS
    sd = r.std(ddof=1) * np.sqrt(TRADING_DAYS)
    return float(mu / sd) if sd != 0 else np.nan

def max_drawdown(returns: pd.Series) -> float:
    eq = equity_curve(returns)
    peak = eq.cummax()
    dd = (eq / peak) - 1.0
    return float(dd.min())

def win_rate(returns: pd.Series) -> float:
    r = returns.dropna()
    if len(r) == 0:
        return np.nan
    return float((r > 0).mean())

def summarize(returns: pd.Series) -> dict[str, float]:
    return {
        "annualized_return": annualized_return(returns),
        "sharpe": sharpe_ratio(returns),
        "max_drawdown": max_drawdown(returns),
        "win_rate": win_rate(returns),
    }
