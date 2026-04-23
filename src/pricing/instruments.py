from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InstrumentResult:
    npv: float
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
