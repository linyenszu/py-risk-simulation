from __future__ import annotations

import pytest

from src.config.settings import AppConfig, RiskSettings


def test_risk_settings_default_vols_include_core_tickers() -> None:
    vols = RiskSettings().vols()
    assert vols["AAPL"] == 0.20
    assert vols["GOOG"] == 0.25
    assert "EURUSD=X" in vols


def test_risk_settings_accepts_custom_vols() -> None:
    settings = RiskSettings(ticker_vols={"AAPL": 0.31})
    assert settings.vols() == {"AAPL": 0.31}


@pytest.mark.parametrize(
    "settings",
    [RiskSettings(confidence_level=1.0), RiskSettings(confidence_level=0.89), RiskSettings(lookback_days=29)],
)
def test_risk_settings_validation_rejects_invalid_inputs(settings: RiskSettings) -> None:
    with pytest.raises(ValueError):
        settings.validate()


def test_app_config_backwards_compatible_aliases() -> None:
    cfg = AppConfig(valuation_date="2025-04-04")
    assert cfg.market_tickers == cfg.tickers
    assert cfg.historical_start_date == "2020-04-05"
