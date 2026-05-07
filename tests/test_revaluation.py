from __future__ import annotations

import pandas as pd

from src.risk.revaluation import revalue_portfolio_under_scenario


def test_revalue_portfolio_under_flat_scenario_returns_float() -> None:
    positions = pd.DataFrame(
        {
            "PositionID": ["P1"],
            "InstrumentType": ["Stock"],
            "Ticker": ["AAPL"],
            "Quantity": [10],
            "CurrentPrice": [100.0],
        }
    )
    base_prices = pd.Series({"AAPL": 100.0})
    scenario = pd.Series({"AAPL": 0.0})
    value = revalue_portfolio_under_scenario(positions, scenario, base_prices)
    assert isinstance(value, float)
    assert value == 1000.0
