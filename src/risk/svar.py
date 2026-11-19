from __future__ import annotations

import pandas as pd
from src.risk.var import historical_log_returns


def select_stress_scenarios(market_data: pd.DataFrame, stress_window_days: int, anchor_ticker: str = "AAPL") -> pd.DataFrame:
    returns = historical_log_returns(market_data)
    if anchor_ticker not in returns.columns:
        anchor_ticker = returns.columns[0]
    worst_date = returns[anchor_ticker].idxmin()
    loc = returns.index.get_loc(worst_date)
    # Keep the window the requested length: centre on the worst day, then slide
    # it inside the sample if the worst day is near either end.
    n = len(returns)
    window = min(stress_window_days, n)
    start = max(0, min(loc - window // 2, n - window))
    return returns.iloc[start:start + window]
