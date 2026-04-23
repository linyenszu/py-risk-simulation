from __future__ import annotations

try:
    import QuantLib as ql  # type: ignore
except Exception:  # pragma: no cover
    ql = None


class QuantLibContext:
    def __init__(self, valuation_date, settings):
        self.valuation_date = valuation_date
        self.settings = settings
        self.available = ql is not None
        self.ql = ql
        if self.available:
            ql_date = ql.Date(valuation_date.day, valuation_date.month, valuation_date.year)
            ql.Settings.instance().evaluationDate = ql_date
            self.ql_valuation_date = ql_date
            self.calendar = ql.TARGET()
            self.day_count = ql.Actual365Fixed()
            self.rate_handle = ql.YieldTermStructureHandle(ql.FlatForward(ql_date, settings.flat_usd_rate, self.day_count))
            self.dividend_handle = ql.YieldTermStructureHandle(ql.FlatForward(ql_date, settings.flat_dividend_yield, self.day_count))
        else:
            self.ql_valuation_date = None
            self.calendar = None
            self.day_count = None
            self.rate_handle = None
            self.dividend_handle = None
