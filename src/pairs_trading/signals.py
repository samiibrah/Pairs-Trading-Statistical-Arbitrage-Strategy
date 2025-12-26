from __future__ import annotations

import numpy as np
import pandas as pd

def compute_spread(y: pd.Series, x: pd.Series, beta: pd.Series) -> pd.Series:
    y2, x2 = y.align(x, join="inner")
    b2 = beta.reindex(y2.index)
    spread = y2 - b2 * x2
    spread.name = "spread"
    return spread

def rolling_zscore(series: pd.Series, lookback: int) -> pd.Series:
    s = series.copy()
    m = s.rolling(lookback).mean()
    sd = s.rolling(lookback).std(ddof=0)
    z = (s - m) / sd
    z.name = "z"
    return z

def positions_from_z(
    z: pd.Series,
    entry_z: float = 2.0,
    exit_z: float = 0.5,
) -> pd.Series:
    """
    Vector-friendly state machine:
      - when z > entry => short spread (-1)
      - when z < -entry => long spread (+1)
      - exit when |z| < exit => flat (0)
    Returns spread position: +1=long spread, -1=short spread
    """
    z = z.copy()

    enter_long = z <= -entry_z
    enter_short = z >= entry_z
    exit_flat = z.abs() <= exit_z

    pos = pd.Series(index=z.index, data=0.0)

    # Build position by iterating once (fast enough for daily data).
    state = 0.0
    for i, dt in enumerate(z.index):
        if np.isnan(z.iloc[i]):
            pos.iloc[i] = np.nan
            continue

        if state == 0.0:
            if enter_long.iloc[i]:
                state = 1.0
            elif enter_short.iloc[i]:
                state = -1.0
        else:
            if exit_flat.iloc[i]:
                state = 0.0

        pos.iloc[i] = state

    pos.name = "spread_pos"
    return pos
