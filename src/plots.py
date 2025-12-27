from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


@dataclass
class EquityDrawdown:
    equity: pd.Series
    drawdown: pd.Series
    drawdown_pct: pd.Series
    running_max: pd.Series


def compute_equity_and_drawdown(
    returns: pd.Series,
    start_equity: float = 1.0,
) -> EquityDrawdown:
    """
    Compute equity curve and drawdown series from a returns series.

    Parameters:
    returns : pd.Series
        Period returns (e.g., daily). Index should be datetime-like.
    start_equity : float
        Starting equity value.

    Returns:
    EquityDrawdown
        equity: cumulative equity curve
        drawdown: equity - running_max
        drawdown_pct: (equity / running_max) - 1
        running_max: running maximum of equity
    """
    if not isinstance(returns, pd.Series):
        raise TypeError("returns must be a pandas Series")

    r = returns.dropna().copy()
    if len(r) == 0:
        raise ValueError("returns series is empty after dropping NaNs")

    # Ensure sorted index for plotting / cumprod
    r = r.sort_index()

    equity = start_equity * (1.0 + r).cumprod()
    running_max = equity.cummax()
    drawdown = equity - running_max
    drawdown_pct = (equity / running_max) - 1.0

    return EquityDrawdown(
        equity=equity,
        drawdown=drawdown,
        drawdown_pct=drawdown_pct,
        running_max=running_max,
    )


def plot_equity_and_drawdown(
    returns: pd.Series,
    title: str = "Equity Curve & Drawdown",
    start_equity: float = 1.0,
    benchmark_returns: Optional[pd.Series] = None,
    benchmark_label: str = "Benchmark",
    trade_dates: Optional[Iterable[pd.Timestamp]] = None,
    figsize: tuple[int, int] = (12, 7),
    show: bool = True,
    save_path: Optional[str] = None,
) -> EquityDrawdown:
    """
    Plot equity curve and drawdown (percent) from a returns series.

    Optional:
    - benchmark_returns: overlay benchmark equity curve for comparison
    - trade_dates: vertical markers for entry/exit dates (timestamps)

    Returns EquityDrawdown for further reporting/testing.
    """
    ed = compute_equity_and_drawdown(returns, start_equity=start_equity)

    # Benchmark
    bench_ed = None
    if benchmark_returns is not None:
        # Align to strategy dates
        b = benchmark_returns.dropna().sort_index()
        b = b.reindex(ed.equity.index).fillna(0.0)
        bench_ed = compute_equity_and_drawdown(b, start_equity=start_equity)

    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        sharex=True,
        figsize=figsize,
        gridspec_kw={"height_ratios": [2, 1]}
    )

    # --- Equity curve ---
    ax1.plot(ed.equity.index, ed.equity.values, label="Strategy")
    ax1.plot(ed.running_max.index, ed.running_max.values, label="Running Max", linestyle="--")

    if bench_ed is not None:
        ax1.plot(bench_ed.equity.index, bench_ed.equity.values, label=benchmark_label, linestyle=":")

    # Optional trade markers
    if trade_dates is not None:
        for dt in trade_dates:
            try:
                ax1.axvline(pd.to_datetime(dt), linewidth=0.8, alpha=0.25)
            except Exception:
                pass

    ax1.set_ylabel("Equity")
    ax1.set_title(title)
    ax1.legend(loc="best")
    ax1.grid(True)

    # --- Drawdown (%), displayed as negative values ---
    ax2.plot(ed.drawdown_pct.index, ed.drawdown_pct.values)
    ax2.axhline(0.0, linewidth=1)
    ax2.set_ylabel("Drawdown")
    ax2.set_xlabel("Date")
    ax2.grid(True)

    # Format y-axis as %
    y = ax2.get_yticks()
    ax2.set_yticklabels([f"{v*100:.0f}%" for v in y])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return ed
