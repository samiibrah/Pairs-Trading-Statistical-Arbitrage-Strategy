returns_by_pair = {}

# Example for one pair
out_nvda_jpm = pair_returns_from_spread_position(
    price_y=prices["NVDA"],
    price_x=prices["JPM"],
    beta=beta_nvda_jpm,
    spread_pos=signal_nvda_jpm,
)

returns_by_pair["NVDA__JPM"] = out_nvda_jpm["ret_net"]

# Another pair
out_amzn_meta = pair_returns_from_spread_position(
    price_y=prices["AMZN"],
    price_x=prices["META"],
    beta=beta_amzn_meta,
    spread_pos=signal_amzn_meta,
)

returns_by_pair["AMZN__META"] = out_amzn_meta["ret_net"]

# Portfolio aggregation
portfolio_ret = equal_weight_portfolio(returns_by_pair)

# Plot
equity, dd = plot_equity_and_drawdown(
    portfolio_ret,
    title="Pairs Trading (Net Returns)",
    show=False
)

