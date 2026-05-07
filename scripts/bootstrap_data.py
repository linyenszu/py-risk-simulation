"""Bootstrap synthetic raw and processed data for local development.

Run from the repository root with either:

    python scripts/bootstrap_data.py
    python -m scripts.bootstrap_data

The script creates the same input artifacts used by the pricing and risk
pipeline: positions, hierarchy, market history, and an enriched master position
file.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Allow direct execution via `python scripts/bootstrap_data.py` from repo root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config.settings import RiskSettings
from src.data.generate_positions import generate_synthetic_positions
from src.data.generate_structure import generate_structure
from src.data.market_data import enrich_positions_with_market, load_market_data
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap local data for the risk simulation.")
    parser.add_argument("--valuation-date", default="2025-04-04")
    parser.add_argument("--use-yfinance", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = RiskSettings(valuation_date=args.valuation_date)
    cfg.validate()

    log = get_logger()
    raw_dir = ensure_dir(cfg.raw_data_dir)
    processed_dir = ensure_dir(cfg.processed_data_dir)

    log.info("Generating synthetic positions and organizational hierarchy")
    positions = generate_synthetic_positions(cfg.valuation_date)
    structure = generate_structure()

    log.info("Loading market data for %s", ", ".join(cfg.tickers))
    market = load_market_data(
        cfg.tickers,
        cfg.valuation_date,
        seed=cfg.random_seed,
        use_yfinance=args.use_yfinance,
    )

    log.info("Creating enriched master positions dataset")
    enriched = enrich_positions_with_market(positions, structure, market, cfg.valuation_date)

    positions.to_csv(raw_dir / "positions.csv", index=False)
    structure.to_csv(raw_dir / "structure.csv", index=False)
    market.to_csv(raw_dir / "historical_market_data.csv")
    enriched.to_csv(processed_dir / "positions_enriched.csv", index=False)

    log.info("Bootstrapped raw data under %s", raw_dir.resolve())
    log.info("Bootstrapped processed data under %s", processed_dir.resolve())


if __name__ == "__main__":
    main()
