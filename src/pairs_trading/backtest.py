from __future__ import annotations

import numpy as np
import pandas as pd

def pair_returns_from_spread_position(
    price_y: pd.Series,
    price_x: pd.Series,
    beta: pd.Series,
    spread_pos: pd.Series,
    fee_bps_per_leg: float = 1.0,
    slippage_bps_per_leg: float = 0.0,
    gross_leverage: float = 1.0,
) -> pd.DataFrame:
    """
    Constructs a dollar-neutral pair:
      - If spread_pos = +1 (long spread): long Y, short beta*X
      - If spread_pos = -1 (short spread): short Y, long beta*X

    We trade returns on next day (position shifted by 1).
    Costs applied on changes in leg positions (turnover proxy).

    Notes:
      - This uses *simple returns* and a normalized notional exposure:
        y_weight = spread_pos
        x_weight = -spread_pos * beta
      - Then weights are scaled to meet gross leverage target using
        |y| + |x| per day.
    """
    y, x = price_y.align(price_x, join="inner")
    b = beta.reindex(y.index)
    p = spread_pos.reindex(y.index)

    rety = y.pct_change()
    retx = x.pct_change()

    # Raw (unscaled) weights
    wy = p
    wx = -p * b

    gross = (wy.abs() + wx.abs()).replace(0.0, np.nan)
    scale = gross_leverage / gross
    wy_s = wy * scale
    wx_s = wx * scale

    # Use yesterday's weights for today's returns
    wy_lag = wy_s.shift(1)
    wx_lag = wx_s.shift(1)

    gross_ret = (wy_lag * rety) + (wx_lag * retx)

    # Transaction costs based on weight changes (turnover)
    dwy = (wy_s - wy_s.shift(1)).abs()
    dwx = (wx_s - wx_s.shift(1)).abs()

    bps_total = fee_bps_per_leg + slippage_bps_per_leg
    cost = (dwy + dwx) * (bps_total / 10_000.0)

    net_ret = gross_ret - cost

    out = pd.DataFrame(
        {
            "ret_gross": gross_ret,
            "ret_net": net_ret,
            "wy": wy_s,
            "wx": wx_s,
            "turnover": dwy + dwx,
            "cost": cost,
        }
    )
    return out

def equal_weight_portfolio(returns_by_pair: dict[str, pd.Series]) -> pd.Series:
    """
    Equal-weight across pairs each day, ignoring NaNs.
    """
    df = pd.DataFrame(returns_by_pair)
    port = df.mean(axis=1, skipna=True)
    port.name = "portfolio_ret"
    return port
