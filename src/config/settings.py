from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


@dataclass(slots=True)
class Settings:
    valuation_date_str: str = "2025-04-04"
    historical_lookback_days: int = 5 * 365
    market_tickers: list[str] = field(
        default_factory=lambda: ["GOOG", "AAPL", "EURUSD=X", "GBPUSD=X"]
    )
    positions_filename: Path = RAW_DIR / "positions.csv"
    structure_filename: Path = RAW_DIR / "structure.csv"
    market_data_filename: Path = RAW_DIR / "historical_market_data.csv"
    greeks_output_filename: Path = PROCESSED_DIR / "position_greeks.csv"
    portfolio_var_filename: Path = PROCESSED_DIR / "portfolio_var.csv"
    report_by_desk_filename: Path = PROCESSED_DIR / "report_by_desk.csv"
    report_by_unit_filename: Path = PROCESSED_DIR / "report_by_unit.csv"
    confidence_level: float = 0.99
    var_lookback_days: int = 252
    flat_usd_rate: float = 0.02
    flat_dividend_yield: float = 0.00
    eur_rate: float = 0.015
    gbp_rate: float = 0.018
    ticker_vols: dict[str, float] = field(
        default_factory=lambda: {
            "AAPL": 0.20,
            "GOOG": 0.25,
            "EURUSD=X": 0.15,
            "GBPUSD=X": 0.12,
        }
    )

    @property
    def valuation_date(self):
        import pandas as pd
        return pd.to_datetime(self.valuation_date_str)

    @property
    def historical_start_date(self):
        return self.valuation_date - timedelta(days=self.historical_lookback_days)

    @property
    def historical_end_date(self):
        return self.valuation_date
