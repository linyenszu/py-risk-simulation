from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from src.aggregation.hierarchy import hierarchy_report
from src.config.settings import RiskSettings
from src.data.generate_positions import generate_synthetic_positions
from src.data.generate_structure import generate_structure
from src.data.market_data import enrich_positions_with_market, load_market_data
from src.pricing.greeks import calculate_instrument_risk
from src.pricing.instruments import MarketContext
from src.risk.var import calculate_var
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Murex-like risk simulation pipeline")
    parser.add_argument("--valuation-date", default="2025-04-04")
    parser.add_argument("--confidence", type=float, default=0.99)
    parser.add_argument("--lookback-days", type=int, default=252)
    parser.add_argument("--use-yfinance", action="store_true")
    return parser.parse_args()


def run(settings: RiskSettings) -> dict[str, pd.DataFrame | float]:
    settings.validate()
    log = get_logger()
    output_dir = ensure_dir(settings.processed_data_dir)

    log.info("Generating positions and hierarchy")
    positions = generate_synthetic_positions(settings.valuation_date)
    structure = generate_structure()

    log.info("Loading market data")
    market = load_market_data(settings.tickers, settings.valuation_date, seed=settings.random_seed)
    enriched = enrich_positions_with_market(positions, structure, market, settings.valuation_date)

    ctx = MarketContext(
        valuation_date=pd.Timestamp(settings.valuation_date),
        risk_free_rate=settings.risk_free_rate,
        dividend_yield=settings.dividend_yield,
        vols=settings.vols(),
        fx_foreign_rates={"EURUSD=X": 0.015, "GBPUSD=X": 0.018},
    )

    log.info("Pricing instruments and calculating Greeks")
    instrument_risk = calculate_instrument_risk(enriched, ctx)

    log.info("Calculating portfolio Historical VaR")
    portfolio_var, pnl = calculate_var(
        instrument_risk,
        market,
        ctx,
        confidence_level=settings.confidence_level,
        lookback_days=settings.lookback_days,
    )

    log.info("Building hierarchy reports")
    desk_report = hierarchy_report(
        instrument_risk,
        market,
        ctx,
        settings.confidence_level,
        settings.lookback_days,
        settings.stress_window_days,
        group_col="TradingDesk",
    )
    unit_report = hierarchy_report(
        instrument_risk,
        market,
        ctx,
        settings.confidence_level,
        settings.lookback_days,
        settings.stress_window_days,
        group_col="Unit",
    )

    enriched.to_csv(output_dir / "positions_enriched.csv", index=False)
    instrument_risk.to_csv(output_dir / "instrument_risk.csv", index=False)
    pnl.to_csv(output_dir / "portfolio_pnl.csv")
    desk_report.to_csv(output_dir / "risk_report_by_desk.csv", index=False)
    unit_report.to_csv(output_dir / "risk_report_by_unit.csv", index=False)

    log.info("Portfolio VaR %.2f", portfolio_var)
    log.info("Wrote outputs to %s", Path(output_dir).resolve())
    return {
        "portfolio_var": portfolio_var,
        "instrument_risk": instrument_risk,
        "portfolio_pnl": pnl,
        "desk_report": desk_report,
        "unit_report": unit_report,
    }


if __name__ == "__main__":
    args = parse_args()
    run(
        RiskSettings(
            valuation_date=args.valuation_date,
            confidence_level=args.confidence,
            lookback_days=args.lookback_days,
        )
    )
