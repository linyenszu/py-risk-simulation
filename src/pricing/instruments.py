from __future__ import annotations

from dataclasses import dataclass
from math import erf, exp, log, pi, sqrt
import pandas as pd


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return exp(-0.5 * x * x) / sqrt(2.0 * pi)


@dataclass(frozen=True)
class MarketContext:
    valuation_date: pd.Timestamp
    risk_free_rate: float
    dividend_yield: float
    vols: dict[str, float]
    fx_foreign_rates: dict[str, float]

    def time_to_maturity(self, maturity: pd.Timestamp) -> float:
        return max((pd.Timestamp(maturity) - self.valuation_date).days / 365.0, 0.0)


def black_scholes_price_greeks(
    spot: float,
    strike: float,
    maturity_years: float,
    rate: float,
    dividend: float,
    vol: float,
    option_type: str,
) -> dict[str, float]:
    if maturity_years <= 0 or vol <= 0 or spot <= 0 or strike <= 0:
        intrinsic = max(spot - strike, 0.0) if option_type == "Call" else max(strike - spot, 0.0)
        return {"NPV": intrinsic, "Delta": 0.0, "Gamma": 0.0, "Vega": 0.0, "Theta": 0.0, "Rho": 0.0}

    d1 = (log(spot / strike) + (rate - dividend + 0.5 * vol * vol) * maturity_years) / (vol * sqrt(maturity_years))
    d2 = d1 - vol * sqrt(maturity_years)
    disc_r = exp(-rate * maturity_years)
    disc_q = exp(-dividend * maturity_years)

    if option_type == "Call":
        price = spot * disc_q * _norm_cdf(d1) - strike * disc_r * _norm_cdf(d2)
        delta = disc_q * _norm_cdf(d1)
        theta = (-(spot * disc_q * _norm_pdf(d1) * vol) / (2 * sqrt(maturity_years)) - rate * strike * disc_r * _norm_cdf(d2) + dividend * spot * disc_q * _norm_cdf(d1)) / 365.0
        rho = strike * maturity_years * disc_r * _norm_cdf(d2)
    else:
        price = strike * disc_r * _norm_cdf(-d2) - spot * disc_q * _norm_cdf(-d1)
        delta = -disc_q * _norm_cdf(-d1)
        theta = (-(spot * disc_q * _norm_pdf(d1) * vol) / (2 * sqrt(maturity_years)) + rate * strike * disc_r * _norm_cdf(-d2) - dividend * spot * disc_q * _norm_cdf(-d1)) / 365.0
        rho = -strike * maturity_years * disc_r * _norm_cdf(-d2)

    gamma = disc_q * _norm_pdf(d1) / (spot * vol * sqrt(maturity_years))
    vega = spot * disc_q * _norm_pdf(d1) * sqrt(maturity_years) / 100.0
    return {"NPV": price, "Delta": delta, "Gamma": gamma, "Vega": vega, "Theta": theta, "Rho": rho / 100.0}


def price_stock(quantity: float, spot: float) -> dict[str, float]:
    return {"NPV": quantity * spot, "Delta": quantity, "Gamma": 0.0, "Vega": 0.0, "Theta": 0.0, "Rho": 0.0}


def price_fx_forward(quantity: float, spot: float, strike: float, maturity: pd.Timestamp, ticker: str, ctx: MarketContext) -> dict[str, float]:
    t = ctx.time_to_maturity(maturity)
    foreign_rate = ctx.fx_foreign_rates.get(ticker, 0.0)
    domestic_df = exp(-ctx.risk_free_rate * t)
    foreign_df = exp(-foreign_rate * t)
    fwd = spot * foreign_df / domestic_df
    npv = quantity * (fwd - strike) * domestic_df
    delta = quantity * foreign_df
    return {"NPV": npv, "Delta": delta, "Gamma": 0.0, "Vega": 0.0, "Theta": 0.0, "Rho": 0.0}
