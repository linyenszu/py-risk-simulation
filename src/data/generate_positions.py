from __future__ import annotations

from datetime import timedelta
import numpy as np
import pandas as pd


def generate_synthetic_positions(valuation_date: str | pd.Timestamp) -> pd.DataFrame:
    vd = pd.Timestamp(valuation_date)
    df = pd.DataFrame(
        {
            "PositionID": [f"POS{i:03d}" for i in range(1, 11)],
            "InstrumentType": [
                "Stock", "Stock", "FX Forward", "FX Forward", "European Option",
                "European Option", "Stock", "European Option", "FX Forward", "Stock",
            ],
            "Ticker": ["AAPL", "GOOG", "EURUSD=X", "GBPUSD=X", "AAPL", "GOOG", "GOOG", "AAPL", "EURUSD=X", "AAPL"],
            "Quantity": [1000, 500, 1_000_000, -500_000, 50, -30, -200, 100, -200_000, 400],
            "Portfolio": ["P1_EqUS", "P1_EqUS", "P2_FXMaj", "P2_FXMaj", "P3_OptEq", "P3_OptEq", "P1_EqUS", "P4_OptSpec", "P2_FXMaj", "P4_OptSpec"],
            "Maturity": [pd.NaT, pd.NaT, vd + timedelta(days=90), vd + timedelta(days=180), vd + timedelta(days=60), vd + timedelta(days=120), pd.NaT, vd + timedelta(days=90), vd + timedelta(days=30), pd.NaT],
            "Strike": [np.nan, np.nan, 1.08, 1.25, 170.0, 180.0, np.nan, 175.0, 1.07, np.nan],
            "OptionType": [np.nan, np.nan, np.nan, np.nan, "Call", "Put", np.nan, "Call", np.nan, np.nan],
        }
    )
    df["Maturity"] = pd.to_datetime(df["Maturity"])
    return df
