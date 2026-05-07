from __future__ import annotations

import pandas as pd
import pytest

from src.config.settings import RiskSettings
from src.data.generate_positions import generate_synthetic_positions
from src.data.generate_structure import generate_structure
from src.data.market_data import enrich_positions_with_market, load_market_data
from src.pricing.greeks import calculate_instrument_risk
from src.pricing.instruments import MarketContext


@pytest.fixture()
def settings() -> RiskSettings:
    return RiskSettings(lookback_days=30, stress_window_days=30, random_seed=123)


@pytest.fixture()
def market(settings: RiskSettings) -> pd.DataFrame:
    return load_market_data(settings.tickers, settings.valuation_date, seed=settings.random_seed)


@pytest.fixture()
def positions(settings: RiskSettings, market: pd.DataFrame) -> pd.DataFrame:
    return enrich_positions_with_market(
        generate_synthetic_positions(settings.valuation_date),
        generate_structure(),
        market,
        settings.valuation_date,
    )


@pytest.fixture()
def market_context(settings: RiskSettings) -> MarketContext:
    return MarketContext(
        valuation_date=pd.Timestamp(settings.valuation_date),
        risk_free_rate=settings.risk_free_rate,
        dividend_yield=settings.dividend_yield,
        vols=settings.vols(),
        fx_foreign_rates={"EURUSD=X": 0.015, "GBPUSD=X": 0.018},
    )


@pytest.fixture()
def priced_positions(positions: pd.DataFrame, market_context: MarketContext) -> pd.DataFrame:
    return calculate_instrument_risk(positions, market_context)
