from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.risk.revaluation import portfolio_pnl_distribution, revalue_portfolio_under_scenario, revalue_positions, scenario_prices
from src.risk.svar import select_stress_scenarios
from src.risk.var import build_historical_scenarios, calculate_var, grouped_pnl_distribution, historical_log_returns, var_from_pnl


def test_historical_log_returns_matches_numpy_log() -> None:
    market = pd.DataFrame({"AAPL": [100.0, 105.0, 102.0]}, index=pd.date_range("2025-01-01", periods=3))
    returns = historical_log_returns(market)
    assert returns.iloc[0, 0] == pytest.approx(np.log(105.0 / 100.0))
    assert returns.iloc[1, 0] == pytest.approx(np.log(102.0 / 105.0))


def test_var_from_pnl_uses_left_tail_quantile() -> None:
    pnl = pd.Series([-10.0, -5.0, 0.0, 5.0, 10.0])
    assert var_from_pnl(pnl, 0.80) == pytest.approx(-6.0)


def test_scenario_prices_applies_log_returns_and_fills_missing() -> None:
    base = pd.Series({"AAPL": 100.0, "GOOG": 50.0})
    returns = pd.Series({"AAPL": np.log(1.1)})
    shocked = scenario_prices(base, returns)
    assert shocked["AAPL"] == pytest.approx(110.0)
    assert shocked["GOOG"] == pytest.approx(50.0)


def test_revalue_positions_creates_position_level_pnl(priced_positions: pd.DataFrame, market_context) -> None:
    scenario = priced_positions.drop_duplicates("Ticker").set_index("Ticker")["CurrentPrice"] * 1.01
    revalued = revalue_positions(priced_positions, market_context, scenario)
    assert {"ScenarioNPV", "PnL"}.issubset(revalued.columns)
    assert revalued["ScenarioNPV"].notna().all()


def test_revalue_portfolio_under_scenario_requires_context_for_derivatives(priced_positions: pd.DataFrame, market: pd.DataFrame) -> None:
    scenario = pd.Series(0.0, index=market.columns)
    base_prices = market.iloc[-1]
    with pytest.raises(ValueError, match="ctx is required"):
        revalue_portfolio_under_scenario(priced_positions, scenario, base_prices, ctx=None)


def test_build_historical_scenarios_and_calculate_var(priced_positions: pd.DataFrame, market: pd.DataFrame, market_context) -> None:
    scenarios = build_historical_scenarios(market, lookback_days=20)
    assert len(scenarios) == 20
    value, pnl = calculate_var(priced_positions, market, market_context, confidence_level=0.99, lookback_days=20)
    assert isinstance(value, float)
    assert len(pnl) == 20
    assert "PortfolioPnL" in pnl


def test_portfolio_and_grouped_pnl_distributions(priced_positions: pd.DataFrame, market: pd.DataFrame, market_context) -> None:
    scenarios = build_historical_scenarios(market, lookback_days=10)
    portfolio = portfolio_pnl_distribution(priced_positions, market, market_context, scenarios)
    grouped = grouped_pnl_distribution(priced_positions, market, market_context, scenarios, "TradingDesk")
    assert len(portfolio) == 10
    assert len(grouped) == 10
    assert set(grouped.columns) == set(priced_positions["TradingDesk"].unique())


def test_select_stress_scenarios_handles_missing_anchor_ticker() -> None:
    market = pd.DataFrame({"ONLY": [100, 101, 90, 91, 92, 93, 94]}, index=pd.date_range("2025-01-01", periods=7))
    stress = select_stress_scenarios(market, stress_window_days=4, anchor_ticker="AAPL")
    assert 1 <= len(stress) <= 4
    assert list(stress.columns) == ["ONLY"]
