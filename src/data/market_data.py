import yfinance as yf
import pandas as pd
from config.settings import TICKERS, VALUATION_DATE

def fetch_market_data(start_date):
    data = yf.download(
        TICKERS,
        start=start_date,
        end=VALUATION_DATE,
        auto_adjust=False,
        progress=False
    )['Close']

    data.ffill(inplace=True)
    data.bfill(inplace=True)
    return data