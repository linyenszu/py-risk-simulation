from __future__ import annotations

import pandas as pd
from src.config.settings import RiskSettings
from src.data.generate_positions import generate_synthetic_positions
from src.data.generate_structure import generate_structure
from src.data.market_data import enrich_positions_with_market, load_market_data
from src.pricing.greeks import calculate_instrument_risk
from src.pricing.instruments import MarketContext
from src.risk.var import calculate_var


def test_calculate_var_returns_loss_quantile_and_distribution():
    settings = RiskSettings(lookback_days=30)
    market = load_market_data(settings.tickers, settings.valuation_date, seed=7)
    positions = enrich_positions_with_market(generate_synthetic_positions(settings.valuation_date), generate_structure(), market, settings.valuation_date)
    ctx = MarketContext(pd.Timestamp(settings.valuation_date), 0.02, 0.0, settings.vols(), {"EURUSD=X": 0.015, "GBPUSD=X": 0.018})
    risk = calculate_instrument_risk(positions, ctx)
    value, pnl = calculate_var(risk, market, ctx, 0.99, 30)
    assert len(pnl) == 30
    assert "PortfolioPnL" in pnl.columns
    assert isinstance(value, float)
