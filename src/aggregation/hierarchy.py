from __future__ import annotations

import pandas as pd
from src.pricing.greeks import GREEK_COLUMNS
from src.pricing.instruments import MarketContext
from src.risk.svar import select_stress_scenarios
from src.risk.var import build_historical_scenarios, grouped_pnl_distribution, var_from_pnl


def aggregate_greeks(positions: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    cols = [c for c in GREEK_COLUMNS if c in positions.columns]
    return positions.groupby(group_cols)[cols].sum().reset_index()


def hierarchy_report(positions: pd.DataFrame, market_data: pd.DataFrame, ctx: MarketContext, confidence_level: float, lookback_days: int, stress_window_days: int, group_col: str) -> pd.DataFrame:
    greek_report = aggregate_greeks(positions, [group_col]).set_index(group_col)
    hist_scenarios = build_historical_scenarios(market_data, lookback_days)
    stress_scenarios = select_stress_scenarios(market_data, stress_window_days)
    hist_pnl = grouped_pnl_distribution(positions, market_data, ctx, hist_scenarios, group_col)
    stress_pnl = grouped_pnl_distribution(positions, market_data, ctx, stress_scenarios, group_col)
    greek_report[f"VaR_{int(confidence_level * 100)}"] = hist_pnl.apply(lambda s: var_from_pnl(s, confidence_level), axis=0)
    greek_report[f"sVaR_{int(confidence_level * 100)}"] = stress_pnl.apply(lambda s: var_from_pnl(s, confidence_level), axis=0)
    return greek_report.reset_index()
