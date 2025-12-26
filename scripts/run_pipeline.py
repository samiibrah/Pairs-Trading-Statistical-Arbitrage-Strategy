from pairs_trading.config import StrategyConfig
from pairs_trading.cli import run

if __name__ == "__main__":
    cfg = StrategyConfig(start="2018-01-01", end=None, max_pairs=10)
    tickers = ["MSFT", "AAPL", "GOOG", "AMZN", "META", "NVDA", "JPM", "BAC"]
    run(cfg, tickers)
