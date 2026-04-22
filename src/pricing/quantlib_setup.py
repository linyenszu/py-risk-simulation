import QuantLib as ql
from config.settings import VALUATION_DATE

def setup_environment():
    ql_date = ql.Date(VALUATION_DATE.day, VALUATION_DATE.month, VALUATION_DATE.year)
    ql.Settings.instance().evaluationDate = ql_date

    day_count = ql.Actual365Fixed()
    calendar = ql.TARGET()

    return ql_date, calendar, day_count
