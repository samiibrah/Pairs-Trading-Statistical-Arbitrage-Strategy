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

from __future__ import annotations

from pathlib import Path
import pandas as pd

from pairs_trading.backtest import pair_returns_from_spread_position, equal_weight_portfolio
from pairs_trading.plotting import plot_equity_and_drawdown


def main() -> None:
    # ---- Paths (adjust to your repo conventions) ----
    reports_dir = Path("reports")
    figures_dir = reports_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # ---- Load inputs (YOU wire these to your actual artifacts) ----
    # Expected: prices.csv with columns: date, ticker, close  OR wide format with tickers as columns
    # Expected: signals for each pair: beta + spread_pos indexed by date
    #
    # For now, this is a template showing the exact flow.

    # Example placeholders (replace with your real loading code):
    prices = pd.read_csv("data/prices_wide.csv", index_col=0, parse_dates=True)

    beta_nvda_jpm = pd.read_csv("data/beta_NVDA_JPM.csv", index_col=0, parse_dates=True).iloc[:, 0]
    pos_nvda_jpm  = pd.read_csv("data/pos_NVDA_JPM.csv",  index_col=0, parse_dates=True).iloc[:, 0]

    beta_amzn_meta = pd.read_csv("data/beta_AMZN_META.csv", index_col=0, parse_dates=True).iloc[:, 0]
    pos_amzn_meta  = pd.read_csv("data/pos_AMZN_META.csv",  index_col=0, parse_dates=True).iloc[:, 0]

    # ---- Per-pair returns ----
    nvda_jpm = pair_returns_from_spread_position(
        price_y=prices["NVDA"],
        price_x=prices["JPM"],
        beta=beta_nvda_jpm,
        spread_pos=pos_nvda_jpm,
        fee_bps_per_leg=1.0,
        slippage_bps_per_leg=0.0,
        gross_leverage=1.0,
    )

    amzn_meta = pair_returns_from_spread_position(
        price_y=prices["AMZN"],
        price_x=prices["META"],
        beta=beta_amzn_meta,
        spread_pos=pos_amzn_meta,
        fee_bps_per_leg=1.0,
        slippage_bps_per_leg=0.0,
        gross_leverage=1.0,
    )

    # ---- Portfolio ----
    returns_by_pair = {
        "NVDA__JPM": nvda_jpm["ret_net"],
        "AMZN__META": amzn_meta["ret_net"],
    }
    portfolio_ret = equal_weight_portfolio(returns_by_pair)

    # ---- Export portfolio returns ----
    out_csv = reports_dir / "portfolio_ret.csv"
    portfolio_ret.to_frame(name="portfolio_ret").to_csv(out_csv, index_label="date")

    # ---- Plot ----
    equity, dd = plot_equity_and_drawdown(portfolio_ret, title="Pairs Trading (Net Returns)", show=False)

    # If your plotting util already saves, great; if not, save here.
    # Example (only if plot_equity_and_drawdown returns fig objects in your implementation):
    # fig1.savefig(figures_dir / "equity_curve.png", dpi=200, bbox_inches="tight")
    # fig2.savefig(figures_dir / "drawdown.png", dpi=200, bbox_inches="tight")

    print(f"Saved: {out_csv}")
    print("Done.")


if __name__ == "__main__":
    main()
