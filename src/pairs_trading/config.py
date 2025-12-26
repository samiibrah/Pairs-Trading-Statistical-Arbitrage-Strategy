from dataclasses import dataclass

@dataclass(frozen=True)
class StrategyConfig:
    # Data
    start: str = "2018-01-01"
    end: str | None = None

    # Pair selection
    coint_pvalue_max: float = 0.05
    min_overlap_days: int = 252  # ~1 trading year

    # Hedge ratio / spread
    beta_lookback: int = 252
    z_lookback: int = 60

    # Signals
    entry_z: float = 2.0
    exit_z: float = 0.5

    # Backtest
    fee_bps_per_leg: float = 1.0  # 1bp per leg per trade (entry/exit)
    slippage_bps_per_leg: float = 0.0
    gross_leverage: float = 1.0   # 1.0 => $1 long + $1 short notionally / 2? (see backtest notes)

    # Portfolio
    max_pairs: int = 10           # trade top-N pairs by cointegration p-value

