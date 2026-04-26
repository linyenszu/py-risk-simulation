from __future__ import annotations

from math import erf, exp, log, pi, sqrt
from typing import Iterable

import numpy as np
import pandas as pd


def ensure_parent(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def normal_pdf(x: float) -> float:
    return exp(-0.5 * x * x) / sqrt(2.0 * pi)


def bs_price_greeks(spot: float, strike: float, rate: float, dividend: float, vol: float, t: float, option_type: str):
    if spot <= 0 or strike <= 0 or vol <= 0 or t <= 0:
        intrinsic = max(0.0, spot - strike) if option_type.lower() == 'call' else max(0.0, strike - spot)
        delta = 1.0 if option_type.lower() == 'call' and spot > strike else 0.0
        if option_type.lower() == 'put':
            delta -= 1.0
        return {
            'npv': intrinsic,
            'delta': delta,
            'gamma': 0.0,
            'vega': 0.0,
            'theta': 0.0,
            'rho': 0.0,
        }

    sqrt_t = sqrt(t)
    d1 = (log(spot / strike) + (rate - dividend + 0.5 * vol * vol) * t) / (vol * sqrt_t)
    d2 = d1 - vol * sqrt_t
    disc_r = exp(-rate * t)
    disc_q = exp(-dividend * t)

    if option_type.lower() == 'call':
        npv = spot * disc_q * normal_cdf(d1) - strike * disc_r * normal_cdf(d2)
        delta = disc_q * normal_cdf(d1)
        theta = (-(spot * disc_q * normal_pdf(d1) * vol) / (2 * sqrt_t) - rate * strike * disc_r * normal_cdf(d2) + dividend * spot * disc_q * normal_cdf(d1)) / 365.0
        rho = strike * t * disc_r * normal_cdf(d2)
    else:
        npv = strike * disc_r * normal_cdf(-d2) - spot * disc_q * normal_cdf(-d1)
        delta = disc_q * (normal_cdf(d1) - 1.0)
        theta = (-(spot * disc_q * normal_pdf(d1) * vol) / (2 * sqrt_t) + rate * strike * disc_r * normal_cdf(-d2) - dividend * spot * disc_q * normal_cdf(-d1)) / 365.0
        rho = -strike * t * disc_r * normal_cdf(-d2)

    gamma = disc_q * normal_pdf(d1) / (spot * vol * sqrt_t)
    vega = spot * disc_q * normal_pdf(d1) * sqrt_t
    return {'npv': npv, 'delta': delta, 'gamma': gamma, 'vega': vega / 100.0, 'theta': theta, 'rho': rho / 100.0}


def year_fraction(start, end) -> float:
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    return max((end - start).days / 365.0, 0.0)


def percentile_var(pnl: Iterable[float], confidence_level: float) -> float:
    pnl_arr = np.asarray(list(pnl), dtype=float)
    return float(np.quantile(pnl_arr, 1.0 - confidence_level))
