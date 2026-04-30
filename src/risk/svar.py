from __future__ import annotations

import pandas as pd
from src.risk.var import historical_log_returns


def select_stress_scenarios(market_data: pd.DataFrame, stress_window_days: int, anchor_ticker: str = "AAPL") -> pd.DataFrame:
    returns = historical_log_returns(market_data)
    if anchor_ticker not in returns.columns:
        anchor_ticker = returns.columns[0]
    worst_date = returns[anchor_ticker].idxmin()
    loc = returns.index.get_loc(worst_date)
    start = max(0, loc - stress_window_days // 2)
    end = min(len(returns), start + stress_window_days)
    return returns.iloc[start:end]
