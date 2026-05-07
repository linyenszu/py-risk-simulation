from __future__ import annotations

import pandas as pd
from src.config.settings import RiskSettings
from src.data.generate_positions import generate_synthetic_positions
from src.data.generate_structure import generate_structure
from src.data.market_data import enrich_positions_with_market, load_market_data
from src.pricing.greeks import calculate_instrument_risk
from src.pricing.instruments import MarketContext


def test_calculate_instrument_risk_has_expected_columns():
    settings = RiskSettings()
    market = load_market_data(settings.tickers, settings.valuation_date, seed=1)
    positions = enrich_positions_with_market(generate_synthetic_positions(settings.valuation_date), generate_structure(), market, settings.valuation_date)
    ctx = MarketContext(pd.Timestamp(settings.valuation_date), 0.02, 0.0, settings.vols(), {"EURUSD=X": 0.015, "GBPUSD=X": 0.018})
    out = calculate_instrument_risk(positions, ctx)
    for col in ["NPV", "Delta", "Gamma", "Vega", "Theta", "Rho"]:
        assert col in out.columns
    assert out["NPV"].notna().all()
    assert out.loc[out["InstrumentType"].eq("Stock"), "Delta"].abs().sum() > 0
