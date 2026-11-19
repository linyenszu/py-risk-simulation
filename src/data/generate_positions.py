from __future__ import annotations

from datetime import timedelta
from typing import Mapping

import numpy as np
import pandas as pd

from src.data.market_data import ANCHOR_PRICES


def generate_synthetic_positions(
    valuation_date: str | pd.Timestamp,
    spots: Mapping[str, float] | None = None,
) -> pd.DataFrame:
    """Build the sample book. Strikes are defined relative to valuation-date spot.

    ``spots`` maps ticker -> spot on the valuation date; it defaults to the
    synthetic-data anchors.
    """
    vd = pd.Timestamp(valuation_date)
    spot_map = {**ANCHOR_PRICES, **(dict(spots) if spots else {})}

    def strike(ticker: str, moneyness: float) -> float:
        return round(float(spot_map[ticker]) * moneyness, 4)

    df = pd.DataFrame(
        {
            "PositionID": [f"POS{i:03d}" for i in range(1, 17)],
            "InstrumentType": [
                "Stock", "Stock", "FX Forward", "FX Forward", "European Option", "European Option",
                "Stock", "European Option", "FX Forward", "Stock", "Equity Future", "Equity Future",
                "Zero Coupon Bond", "Fixed Rate Bond", "Interest Rate Swap", "Interest Rate Swap",
            ],
            "Ticker": [
                "AAPL", "GOOG", "EURUSD=X", "GBPUSD=X", "AAPL", "GOOG", "GOOG", "AAPL",
                "EURUSD=X", "AAPL", "AAPL", "GOOG", "US10Y", "US10Y", "SOFR", "SOFR",
            ],
            "Quantity": [1000, 500, 1_000_000, -500_000, 50, -30, -200, 100, -200_000, 400, 10, -5, 250, 150, 1, 1],
            "Portfolio": [
                "P1_EqUS", "P1_EqUS", "P2_FXMaj", "P2_FXMaj", "P3_OptEq", "P3_OptEq",
                "P1_EqUS", "P4_OptSpec", "P2_FXMaj", "P4_OptSpec", "P5_Futures", "P5_Futures",
                "P6_Rates", "P6_Rates", "P7_Swaps", "P7_Swaps",
            ],
            "Maturity": [
                pd.NaT, pd.NaT, vd + timedelta(days=90), vd + timedelta(days=180),
                vd + timedelta(days=60), vd + timedelta(days=120), pd.NaT, vd + timedelta(days=90),
                vd + timedelta(days=30), pd.NaT, vd + timedelta(days=90), vd + timedelta(days=180),
                vd + timedelta(days=365 * 2), vd + timedelta(days=365 * 5), vd + timedelta(days=365 * 3), vd + timedelta(days=365 * 7),
            ],
            "Strike": [
                np.nan, np.nan, strike("EURUSD=X", 1.00), strike("GBPUSD=X", 1.00),
                strike("AAPL", 1.00), strike("GOOG", 1.05), np.nan, strike("AAPL", 1.03),
                strike("EURUSD=X", 0.99), np.nan,
                strike("AAPL", 1.02), strike("GOOG", 0.98), np.nan, np.nan, np.nan, np.nan,
            ],
            "OptionType": [np.nan, np.nan, np.nan, np.nan, "Call", "Put", np.nan, "Call", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            "ContractMultiplier": [np.nan] * 10 + [100.0, 100.0] + [np.nan] * 4,
            "FaceValue": [np.nan] * 12 + [1000.0, 1000.0] + [np.nan] * 2,
            "CouponRate": [np.nan] * 13 + [0.045] + [np.nan] * 2,
            "Notional": [np.nan] * 14 + [5_000_000.0, 3_000_000.0],
            "FixedRate": [np.nan] * 14 + [0.035, 0.032],
            "PayReceive": [np.nan] * 14 + ["Payer", "Receiver"],
            "PaymentFrequency": [np.nan] * 13 + [2.0, 2.0, 2.0],
        }
    )
    df["Maturity"] = pd.to_datetime(df["Maturity"])
    return df
