"""Data loading and enrichment utilities for the risk simulation pipeline."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def load_positions(path: str | Path) -> pd.DataFrame:
    """Load positions and parse maturity dates."""
    return pd.read_csv(path, parse_dates=["Maturity"])


def load_structure(path: str | Path) -> pd.DataFrame:
    """Load portfolio-to-desk/unit hierarchy."""
    return pd.read_csv(path)


def load_market_data(path: str | Path) -> pd.DataFrame:
    """Load historical market data indexed by date."""
    return pd.read_csv(path, index_col="Date", parse_dates=True)


def enrich_positions(
    positions: pd.DataFrame,
    structure: pd.DataFrame,
    market_data: pd.DataFrame,
    valuation_date: str,
) -> pd.DataFrame:
    """Join positions with hierarchy and current market prices."""
    merged = positions.merge(structure, on="Portfolio", how="left")
    latest = market_data.loc[valuation_date].rename("CurrentPrice").reset_index()
    latest = latest.rename(columns={latest.columns[0]: "Ticker"})
    enriched = merged.merge(latest, on="Ticker", how="left")
    enriched["MarketValue_Initial"] = enriched["Quantity"] * enriched["CurrentPrice"]
    enriched.loc[enriched["InstrumentType"] != "Stock", "MarketValue_Initial"] = pd.NA
    return enriched
