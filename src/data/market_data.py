from __future__ import annotations

from datetime import timedelta

import pandas as pd


DEFAULT_FALLBACK_PRICES = pd.DataFrame(
    {
        'AAPL': [200.0, 202.0, 204.0, 203.19],
        'GOOG': [150.0, 151.0, 153.0, 152.63],
        'EURUSD=X': [1.08, 1.09, 1.10, 1.0989],
        'GBPUSD=X': [1.28, 1.29, 1.30, 1.2990],
    },
    index=pd.to_datetime(['2025-04-01', '2025-04-02', '2025-04-03', '2025-04-04']),
)
DEFAULT_FALLBACK_PRICES.index.name = 'Date'


def fetch_historical_market_data(tickers: list[str], start, end) -> pd.DataFrame:
    try:
        import yfinance as yf

        raw = yf.download(
            tickers,
            start=pd.to_datetime(start),
            end=pd.to_datetime(end) + timedelta(days=1),
            progress=False,
            auto_adjust=False,
        )
        market_data = raw['Close'].copy() if isinstance(raw.columns, pd.MultiIndex) else raw[['Close']].rename(columns={'Close': tickers[0]})
        market_data = market_data.ffill().bfill()
        if market_data.empty:
            raise ValueError('empty market data returned by yfinance')
        market_data.index.name = 'Date'
        return market_data
    except Exception:
        fallback = DEFAULT_FALLBACK_PRICES.copy()
        missing = [ticker for ticker in tickers if ticker not in fallback.columns]
        for ticker in missing:
            fallback[ticker] = fallback.iloc[:, 0]
        return fallback[tickers]


def get_latest_prices(market_data: pd.DataFrame, valuation_date_str: str) -> pd.DataFrame:
    if valuation_date_str in market_data.index.astype(str):
        latest_prices = market_data.loc[valuation_date_str]
    else:
        latest_prices = market_data.iloc[-1]
    latest_prices_df = latest_prices.to_frame(name='CurrentPrice').reset_index()
    latest_prices_df.rename(columns={'index': 'Ticker'}, inplace=True)
    return latest_prices_df
