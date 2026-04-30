from __future__ import annotations

import numpy as np
import pandas as pd
from src.pricing.greeks import price_position
from src.pricing.instruments import MarketContext


def scenario_prices(base_prices: pd.Series, log_return_scenario: pd.Series) -> pd.Series:
    aligned = log_return_scenario.reindex(base_prices.index).fillna(0.0)
    return base_prices * np.exp(aligned)


def revalue_positions(positions: pd.DataFrame, ctx: MarketContext, scenario_price_row: pd.Series) -> pd.DataFrame:
    out = positions.copy()
    npvs: list[float] = []
    for _, row in out.iterrows():
        spot = float(scenario_price_row[row["Ticker"]])
        npvs.append(price_position(row, ctx, override_spot=spot)["NPV"])
    out["ScenarioNPV"] = npvs
    out["PnL"] = out["ScenarioNPV"] - out["NPV"]
    return out


def portfolio_pnl_distribution(positions: pd.DataFrame, market_data: pd.DataFrame, ctx: MarketContext, scenarios: pd.DataFrame) -> pd.DataFrame:
    base_prices = market_data.loc[: ctx.valuation_date].iloc[-1]
    rows = []
    for scenario_date, returns in scenarios.iterrows():
        shocked = scenario_prices(base_prices, returns)
        revalued = revalue_positions(positions, ctx, shocked)
        rows.append({
            "ScenarioDate": scenario_date,
            "PortfolioPnL": revalued["PnL"].sum(),
            **{f"PositionPnL_{pid}": pnl for pid, pnl in zip(revalued["PositionID"], revalued["PnL"])}
        })
    return pd.DataFrame(rows).set_index("ScenarioDate")
