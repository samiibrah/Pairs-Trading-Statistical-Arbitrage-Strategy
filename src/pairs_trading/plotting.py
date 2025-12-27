from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def equity_curve_from_returns(returns: pd.Series, start: float = 1.0) -> pd.Series:
    """
    Convert simple returns into an equity curve.

    Parameters
    ----------
    returns : pd.Series
        Period returns (e.g., daily). Should be simple returns, not log returns.
    start : float
        Starting equity value.

    Returns
    -------
    pd.Series
        Equity curve indexed like returns.
    """
    r = returns.fillna(0.0).astype(float)
    eq = (1.0 + r).cumprod() * float(start)
    eq.name = "equity"
    return eq


def drawdown_from_equity(equity: pd.Series) -> pd.Series:
    """
    Compute drawdown series from an equity curve.

    Drawdown is defined as (equity / running_max) - 1, so it's <= 0.
    """
    eq = equity.astype(float)
    peak = eq.cummax()
    dd = (eq / peak) - 1.0
    dd.name = "drawdown"
    return dd


def plot_equity_and_drawdown(
    returns: pd.Series,
    title: str = "Equity curve & drawdown",
    start: float = 1.0,
    show: bool = True,
):
    """
    Plot equity curve and drawdown (two separate figures).

    Notes
    -----
    - Uses matplotlib only (no seaborn).
    - Does not set any custom colors.
    """
    equity = equity_curve_from_returns(returns, start=start)
    drawdown = drawdown_from_equity(equity)

    # Equity curve plot
    plt.figure()
    plt.plot(equity.index, equity.values)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Equity")
    plt.tight_layout()

    # Drawdown plot
    plt.figure()
    plt.plot(drawdown.index, drawdown.values)
    plt.title("Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.tight_layout()

    if show:
        plt.show()

    return equity, drawdown
