## `config/settings.py`

from datetime import datetime, timedelta

VALUATION_DATE = datetime(2025, 4, 4)
LOOKBACK_DAYS = 252

TICKERS = ['AAPL', 'GOOG', 'EURUSD=X', 'GBPUSD=X']

RISK_FREE_RATE = 0.02
DIVIDEND_YIELD = 0.0