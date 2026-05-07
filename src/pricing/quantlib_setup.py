"""Optional QuantLib integration boundary.

The production project keeps native QuantLib dependency behind this module so the
core tests and CI can run in a pure-Python environment. A real deployment can add
curve bootstrapping, volatility surfaces, calendars, and QuantLib pricing engines
here without changing the risk aggregation API.
"""
from __future__ import annotations


def quantlib_available() -> bool:
    try:
        import QuantLib  # noqa: F401
        return True
    except Exception:
        return False
