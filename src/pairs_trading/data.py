from __future__ import annotations

import pandas as pd
import yfinance as yf

def fetch_adj_close(tickers: list[str], start: str, end: str | None = None) -> pd.DataFrame:
    """
    Returns a DataFrame indexed by date with columns=tickers containing Adjusted Close.
    """
    df = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
        group_by="ticker",
        threads=True,
    )

    # yfinance returns different shapes for 1 vs many tickers; normalize.
    if isinstance(df.columns, pd.MultiIndex):
        # MultiIndex: (Ticker, OHLCV)
        adj = pd.DataFrame({t: df[(t, "Adj Close")] for t in tickers})
    else:
        # Single ticker
        adj = df[["Adj Close"]].rename(columns={"Adj Close": tickers[0]})

    adj = adj.sort_index()
    adj = adj.dropna(how="all")
    return adj

def align_prices(prices: pd.DataFrame, min_overlap_days: int = 252) -> pd.DataFrame:
    """
    Ensures:
      - Datetime index
      - Forward-fill small gaps (optional policy)
      - Drops tickers with insufficient data
    """
    p = prices.copy()
    p.index = pd.to_datetime(p.index)
    p = p.sort_index()
    p = p.ffill()

    valid = p.notna().sum(axis=0) >= min_overlap_days
    p = p.loc[:, valid]
    return p

