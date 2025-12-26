from __future__ import annotations

import argparse
from dataclasses import asdict
from itertools import combinations

import pandas as pd
from tqdm import tqdm

from .config import StrategyConfig
from .data import fetch_adj_close, align_prices
from .stats import engle_granger_coint_pvalue, rolling_ols_beta, adf_pvalue
from .signals import compute_spread, rolling_zscore, positions_from_z
from .backtest import pair_returns_from_spread_position, equal_weight_portfolio
from .metrics import summarize, equity_curve

def select_pairs(prices: pd.DataFrame, cfg: StrategyConfig) -> pd.DataFrame:
    tickers = list(prices.columns)
    rows = []
    for a, b in tqdm(list(combinations(tickers, 2)), desc="Cointegration tests"):
        y = prices[a]
        x = prices[b]
        both = y.notna() & x.notna()
        if both.sum() < cfg.min_overlap_days:
            continue
        p = engle_granger_coint_pvalue(y, x)
        rows.append((a, b, p))
    out = pd.DataFrame(rows, columns=["A", "B", "coint_pvalue"]).dropna()
    out = out.sort_values("coint_pvalue")
    out = out[out["coint_pvalue"] <= cfg.coint_pvalue_max]
    return out.head(cfg.max_pairs)

def run(cfg: StrategyConfig, tickers: list[str]) -> None:
    print("Config:", asdict(cfg))
    prices = fetch_adj_close(tickers, start=cfg.start, end=cfg.end)
    prices = align_prices(prices, min_overlap_days=cfg.min_overlap_days)

    if prices.shape[1] < 2:
        raise SystemExit("Not enough tickers with sufficient data after cleaning.")

    pairs = select_pairs(prices, cfg)
    if pairs.empty:
        raise SystemExit("No cointegrated pairs found under the p-value threshold.")

    pair_rets_net: dict[str, pd.Series] = {}
    diagnostics = []

    for _, row in pairs.iterrows():
        A, B = row["A"], row["B"]
        y = prices[A]
        x = prices[B]

        beta = rolling_ols_beta(y, x, lookback=cfg.beta_lookback)
        spread = compute_spread(y, x, beta)
        z = rolling_zscore(spread, lookback=cfg.z_lookback)
        pos = positions_from_z(z, entry_z=cfg.entry_z, exit_z=cfg.exit_z)

        bt = pair_returns_from_spread_position(
            price_y=y,
            price_x=x,
            beta=beta,
            spread_pos=pos,
            fee_bps_per_leg=cfg.fee_bps_per_leg,
            slippage_bps_per_leg=cfg.slippage_bps_per_leg,
            gross_leverage=cfg.gross_leverage,
        )

        # Stationarity check on spread (whole-sample)
        adf_p = adf_pvalue(spread)

        key = f"{A}__{B}"
        pair_rets_net[key] = bt["ret_net"]

        diagnostics.append(
            {
                "pair": key,
                "coint_pvalue": float(row["coint_pvalue"]),
                "adf_pvalue_spread": float(adf_p) if pd.notna(adf_p) else None,
                "n_days": int(bt["ret_net"].dropna().shape[0]),
            }
        )

    portfolio = equal_weight_portfolio(pair_rets_net)
    stats = summarize(portfolio)
    eq = equity_curve(portfolio)

    print("\nSelected pairs:")
    print(pairs.to_string(index=False))

    print("\nDiagnostics (per pair):")
    print(pd.DataFrame(diagnostics).sort_values(["coint_pvalue"]).to_string(index=False))

    print("\nPortfolio metrics:")
    for k, v in stats.items():
        print(f"- {k}: {v:.4f}")

    print(f"\nEquity curve: start={eq.iloc[0]:.4f} end={eq.iloc[-1]:.4f}")

def main():
    ap = argparse.ArgumentParser(description="Pairs Trading Statistical Arbitrage")
    ap.add_argument("--tickers", type=str, required=True, help="Comma-separated tickers, e.g. MSFT,AAPL,GOOG,AMZN")
    ap.add_argument("--start", type=str, default="2018-01-01")
    ap.add_argument("--end", type=str, default=None)
    ap.add_argument("--max_pairs", type=int, default=10)
    args = ap.parse_args()

    cfg = StrategyConfig(start=args.start, end=args.end, max_pairs=args.max_pairs)
    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    run(cfg, tickers)
