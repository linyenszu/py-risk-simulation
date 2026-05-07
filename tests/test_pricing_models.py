from __future__ import annotations

import math

import pandas as pd
import pytest

from src.pricing.fallback_bs import black_scholes_greeks
from src.pricing.greeks import GREEK_COLUMNS, calculate_instrument_risk, price_position
from src.pricing.instruments import MarketContext, black_scholes_price_greeks, price_fx_forward, price_stock


def test_black_scholes_call_put_parity_holds() -> None:
    spot = 100.0
    strike = 95.0
    t = 0.75
    rate = 0.03
    dividend = 0.01
    vol = 0.22
    call = black_scholes_price_greeks(spot, strike, t, rate, dividend, vol, "Call")
    put = black_scholes_price_greeks(spot, strike, t, rate, dividend, vol, "Put")
    lhs = call["NPV"] - put["NPV"]
    rhs = spot * math.exp(-dividend * t) - strike * math.exp(-rate * t)
    assert lhs == pytest.approx(rhs, rel=1e-10)


def test_fallback_black_scholes_rejects_invalid_option_type() -> None:
    with pytest.raises(ValueError, match="option_type"):
        black_scholes_greeks(100, 100, 1, 0.02, 0.20, "Digital")


def test_price_stock_has_linear_delta() -> None:
    result = price_stock(quantity=25, spot=101.5)
    assert result["NPV"] == pytest.approx(2537.5)
    assert result["Delta"] == 25
    assert result["Gamma"] == 0.0


def test_price_fx_forward_zero_when_strike_equals_theoretical_forward() -> None:
    ctx = MarketContext(pd.Timestamp("2025-04-04"), 0.02, 0.0, {}, {"EURUSD=X": 0.015})
    maturity = pd.Timestamp("2025-07-04")
    t = ctx.time_to_maturity(maturity)
    spot = 1.10
    theoretical_forward = spot * math.exp(-0.015 * t) / math.exp(-0.02 * t)
    result = price_fx_forward(1_000_000, spot, theoretical_forward, maturity, "EURUSD=X", ctx)
    assert result["NPV"] == pytest.approx(0.0, abs=1e-8)
    assert result["Delta"] > 0


def test_price_position_rejects_unknown_instrument_with_nans(market_context: MarketContext) -> None:
    row = pd.Series({"InstrumentType": "Unknown", "CurrentPrice": 100.0, "Quantity": 1})
    result = price_position(row, market_context)
    assert all(math.isnan(result[col]) for col in GREEK_COLUMNS)


def test_calculate_instrument_risk_preserves_row_count(positions: pd.DataFrame, market_context: MarketContext) -> None:
    priced = calculate_instrument_risk(positions, market_context)
    assert len(priced) == len(positions)
    assert set(GREEK_COLUMNS).issubset(priced.columns)
    assert priced[GREEK_COLUMNS].notna().all().all()
