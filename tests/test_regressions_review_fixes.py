"""Regression tests for defects found in the project review.

Each test is written so that it FAILS on the original code (see comments).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.data.generate_positions import generate_synthetic_positions
from src.data.market_data import ANCHOR_PRICES, simulate_market_data
from src.pricing.greeks import RATE_SENSITIVE_TYPES, calculate_instrument_risk, price_position
from src.pricing.instruments import MarketContext, price_interest_rate_swap
from src.pricing.monte_carlo import price_european_option_mc
from src.pricing.yield_curve import (
    ShiftedZeroCurve,
    ZeroCouponYieldCurve,
    bootstrap_zero_coupon_curve,
    sample_bond_market_quotes,
    validate_bond_quotes,
)
from src.risk.revaluation import portfolio_pnl_distribution
from src.risk.svar import select_stress_scenarios
from src.risk.var import build_historical_scenarios, grouped_pnl_distribution, var_from_pnl


@pytest.fixture()
def curve() -> ZeroCouponYieldCurve:
    return ZeroCouponYieldCurve.from_bond_quotes(sample_bond_market_quotes())


@pytest.fixture()
def curve_ctx(market_context: MarketContext, curve) -> MarketContext:
    return MarketContext(
        valuation_date=market_context.valuation_date,
        risk_free_rate=market_context.risk_free_rate,
        dividend_yield=market_context.dividend_yield,
        vols=market_context.vols,
        fx_foreign_rates=market_context.fx_foreign_rates,
        zero_curve=curve,
    )


# ---------------------------------------------------------------- Fix 1: rates
def _rates(positions: pd.DataFrame) -> pd.DataFrame:
    return positions[positions["InstrumentType"].isin(RATE_SENSITIVE_TYPES)]


def test_rate_positions_have_nonzero_scenario_pnl(positions, market, curve_ctx, settings):
    # Original code: rate P&L was exactly 0 in every scenario (log-return of a rate level
    # was applied as a price on instruments that ignore the spot).
    scenarios = build_historical_scenarios(market, settings.lookback_days)
    priced = calculate_instrument_risk(_rates(positions), curve_ctx)
    pnl = portfolio_pnl_distribution(priced, market, curve_ctx, scenarios)
    position_cols = [f"PositionPnL_{pid}" for pid in _rates(positions)["PositionID"]]
    assert len(position_cols) == 4
    assert (pnl[position_cols].abs() > 1e-6).all().all()


def test_rates_desk_var_is_not_zero(positions, market, curve_ctx, settings):
    scenarios = build_historical_scenarios(market, settings.lookback_days)
    priced = calculate_instrument_risk(positions, curve_ctx)
    grouped = grouped_pnl_distribution(priced, market, curve_ctx, scenarios, "TradingDesk")
    assert var_from_pnl(grouped["Rates Desk"], 0.99) < -1.0


def test_with_rate_shift_zero_returns_same_context(curve_ctx):
    assert curve_ctx.with_rate_shift(0.0) is curve_ctx


def test_shifted_curve_is_exact_parallel_shift(curve):
    s = 0.0025
    shifted = ShiftedZeroCurve(curve, s)
    for t in (0.25, 1.0, 3.7, 9.0):
        assert shifted.zero_rate(t) == pytest.approx(curve.zero_rate(t) + s, abs=1e-12)
        assert shifted.discount_factor(t) == pytest.approx(curve.discount_factor(t) * np.exp(-s * t), rel=1e-12)
    assert shifted.forward_rate(1.0, 3.0) == pytest.approx(curve.forward_rate(1.0, 3.0) + s, abs=1e-12)


@pytest.mark.parametrize("instrument_type", ["Zero Coupon Bond", "Fixed Rate Bond", "Interest Rate Swap"])
def test_scenario_rate_shift_matches_curve_shift_and_has_correct_sign(positions, curve_ctx, instrument_type):
    row = _rates(positions).loc[lambda d: d["InstrumentType"] == instrument_type].iloc[0]
    base = price_position(row, curve_ctx)["NPV"]
    up = price_position(row, curve_ctx, override_spot=float(row["CurrentPrice"]) + 0.0010)["NPV"]
    direct = price_position(row, curve_ctx.with_rate_shift(0.0010))["NPV"]
    assert up == pytest.approx(direct)
    assert up != pytest.approx(base)
    if instrument_type != "Interest Rate Swap":
        assert up < base  # long bonds lose when rates rise


@pytest.mark.parametrize("instrument_type", ["Zero Coupon Bond", "Fixed Rate Bond"])
def test_bond_dv01_matches_finite_difference(positions, curve_ctx, instrument_type):
    row = _rates(positions).loc[lambda d: d["InstrumentType"] == instrument_type].iloc[0]
    h = 1e-5
    up = price_position(row, curve_ctx.with_rate_shift(h))["NPV"]
    dn = price_position(row, curve_ctx.with_rate_shift(-h))["NPV"]
    analytic = price_position(row, curve_ctx)["Delta"]  # dNPV / d(rate)
    assert (up - dn) / (2 * h) == pytest.approx(analytic, rel=0.02)


def test_payer_and_receiver_swaps_are_opposites(curve_ctx):
    # Original sample book had a "Receiver" with quantity -1 which double-negated to a Payer.
    maturity = curve_ctx.valuation_date + pd.Timedelta(days=365 * 5)
    kw = dict(notional=1e6, fixed_rate=0.03, maturity=maturity, ctx=curve_ctx, floating_rate=None)
    payer = price_interest_rate_swap(quantity=1, pay_receive="Payer", **kw)["NPV"]
    receiver = price_interest_rate_swap(quantity=1, pay_receive="Receiver", **kw)["NPV"]
    assert payer == pytest.approx(-receiver)
    assert payer != 0.0


def test_sample_book_swaps_are_one_payer_one_receiver_with_positive_quantity():
    book = generate_synthetic_positions("2025-04-04")
    swaps = book[book["InstrumentType"] == "Interest Rate Swap"]
    assert set(swaps["PayReceive"]) == {"Payer", "Receiver"}
    assert (swaps["Quantity"] > 0).all()


# ----------------------------------------------------- Fix 2: spot/strike anchor
def test_synthetic_market_ends_at_anchor_prices(settings):
    m = simulate_market_data(settings.tickers, settings.valuation_date, seed=settings.random_seed)
    for ticker in settings.tickers:
        assert m[ticker].iloc[-1] == pytest.approx(ANCHOR_PRICES[ticker], rel=1e-5)


@pytest.mark.parametrize("seed", [1, 42, 123, 999])
def test_strikes_are_near_spot_for_any_seed(seed, settings):
    market = simulate_market_data(settings.tickers, settings.valuation_date, seed=seed)
    spots = market.iloc[-1].to_dict()
    book = generate_synthetic_positions(settings.valuation_date, spots=spots)
    book = book.dropna(subset=["Strike"])
    ratio = book["Strike"] / book["Ticker"].map(spots)
    # Original code: GOOG spot/strike was 0.23 because history drifted away from hard-coded strikes.
    assert ratio.between(0.95, 1.06).all()


def test_main_run_uses_valuation_date_spot_for_strikes(positions):
    opts = positions[positions["InstrumentType"].isin(["European Option", "Equity Future", "FX Forward"])]
    ratio = opts["Strike"] / opts["CurrentPrice"]
    assert ratio.between(0.95, 1.06).all()


# ---------------------------------------------------------- Fix 3a: bootstrap
def test_bootstrap_reprices_every_input_bond_exactly(curve):
    quotes = validate_bond_quotes(sample_bond_market_quotes())
    for _, b in quotes.iterrows():
        freq = int(b["Frequency"])
        n = max(int(round(b["MaturityYears"] * freq)), 1)
        cpn = b["FaceValue"] * b["CouponRate"] / freq
        pv = sum((cpn + (b["FaceValue"] if i == n else 0.0)) * curve.discount_factor(i / freq) for i in range(1, n + 1))
        assert pv == pytest.approx(b["MarketPrice"], abs=1e-8)  # was off by up to 0.07


def test_bootstrap_rejects_unbracketed_price():
    bad = sample_bond_market_quotes()
    bad.loc[0, "MarketPrice"] = 1e6
    with pytest.raises(ValueError):
        bootstrap_zero_coupon_curve(bad)


# ----------------------------------------------------------- Fix 3b: MC std error
MC_ARGS = dict(spot=100.0, strike=100.0, maturity_years=1.0, rate=0.03, volatility=0.2, option_type="Call", num_paths=10_000)


def test_antithetic_standard_error_matches_empirical_spread():
    results = [price_european_option_mc(**MC_ARGS, seed=s) for s in range(150)]
    prices = np.array([r.price for r in results])
    reported = np.mean([r.standard_error for r in results])
    # Original code overstated SE by ~35-40%.
    assert reported == pytest.approx(prices.std(ddof=1), rel=0.15)


def test_antithetic_se_is_smaller_than_naive_se():
    anti = np.mean([price_european_option_mc(**MC_ARGS, seed=s).standard_error for s in range(20)])
    naive = np.mean([price_european_option_mc(**MC_ARGS, seed=s, antithetic=False).standard_error for s in range(20)])
    assert anti < naive


def test_mc_confidence_interval_coverage_is_near_nominal():
    from src.pricing.instruments import black_scholes_price_greeks

    truth = black_scholes_price_greeks(100.0, 100.0, 1.0, 0.03, 0.0, 0.2, "Call")["NPV"]
    hits = [
        (lambda r: r.confidence_interval_low <= truth <= r.confidence_interval_high)(price_european_option_mc(**MC_ARGS, seed=s))
        for s in range(200)
    ]
    assert 0.90 <= np.mean(hits) <= 0.99  # original: ~99-100% (too wide)


@pytest.mark.parametrize("n", [5_001, 5_000])
def test_mc_se_handles_odd_and_even_path_counts(n):
    r = price_european_option_mc(**{**MC_ARGS, "num_paths": n}, seed=3)
    assert 0 < r.standard_error < 1


# ---------------------------------------------------- Fix 3c: stress window
def _synthetic_returns_market(worst_pos: int, n: int = 400) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    dates = pd.bdate_range("2023-01-02", periods=n)
    log_ret = rng.normal(0, 0.005, n)
    log_ret[worst_pos] = -0.5
    prices = 100 * np.exp(np.cumsum(log_ret))
    return pd.DataFrame({"AAPL": prices, "GOOG": prices * 1.1}, index=dates)


@pytest.mark.parametrize("worst_pos", [1, 5, 120, 200, 380, 398])
def test_stress_window_has_requested_length_and_contains_worst_day(worst_pos):
    market = _synthetic_returns_market(worst_pos)
    window = select_stress_scenarios(market, 100)
    returns = np.log(market / market.shift(1)).dropna()
    assert len(window) == 100  # original returned a truncated window when the worst day was near the end
    assert returns["AAPL"].idxmin() in window.index


def test_stress_window_longer_than_sample_returns_all_returns():
    market = _synthetic_returns_market(50, n=60)
    assert len(select_stress_scenarios(market, 500)) == 59
