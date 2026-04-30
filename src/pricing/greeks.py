from __future__ import annotations

import numpy as np
import pandas as pd
from src.pricing.instruments import MarketContext, black_scholes_price_greeks, price_fx_forward, price_stock

GREEK_COLUMNS = ["NPV", "Delta", "Gamma", "Vega", "Theta", "Rho"]


def price_position(row: pd.Series, ctx: MarketContext, override_spot: float | None = None) -> dict[str, float]:
    spot = float(row["CurrentPrice"] if override_spot is None else override_spot)
    quantity = float(row["Quantity"])
    instrument_type = row["InstrumentType"]

    if instrument_type == "Stock":
        return price_stock(quantity, spot)

    if instrument_type == "FX Forward":
        return price_fx_forward(quantity, spot, float(row["Strike"]), row["Maturity"], row["Ticker"], ctx)

    if instrument_type == "European Option":
        unit = black_scholes_price_greeks(
            spot=spot,
            strike=float(row["Strike"]),
            maturity_years=ctx.time_to_maturity(row["Maturity"]),
            rate=ctx.risk_free_rate,
            dividend=ctx.dividend_yield,
            vol=ctx.vols.get(row["Ticker"], 0.20),
            option_type=str(row["OptionType"]),
        )
        return {k: v * quantity for k, v in unit.items()}

    return {k: np.nan for k in GREEK_COLUMNS}


def calculate_instrument_risk(positions: pd.DataFrame, ctx: MarketContext) -> pd.DataFrame:
    priced = positions.copy()
    rows = [price_position(row, ctx) for _, row in priced.iterrows()]
    risk = pd.DataFrame(rows, index=priced.index)
    for col in GREEK_COLUMNS:
        priced[col] = risk[col]
    return priced
