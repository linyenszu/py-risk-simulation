import pandas as pd
import numpy as np
from datetime import timedelta
from config.settings import VALUATION_DATE

def generate_positions():
    data = {
        'PositionID': [f'POS{i:03d}' for i in range(1, 11)],
        'InstrumentType': ['Stock','Stock','FX Forward','FX Forward',
                           'European Option','European Option','Stock',
                           'European Option','FX Forward','Stock'],
        'Ticker': ['AAPL','GOOG','EURUSD=X','GBPUSD=X',
                   'AAPL','GOOG','GOOG','AAPL','EURUSD=X','AAPL'],
        'Quantity': [1000,500,1000000,-500000,50,-30,-200,100,-200000,400],
        'Portfolio': ['P1_EqUS','P1_EqUS','P2_FXMaj','P2_FXMaj',
                      'P3_OptEq','P3_OptEq','P1_EqUS','P4_OptSpec',
                      'P2_FXMaj','P4_OptSpec'],
        'Maturity': [pd.NaT, pd.NaT,
                     VALUATION_DATE + timedelta(days=90),
                     VALUATION_DATE + timedelta(days=180),
                     VALUATION_DATE + timedelta(days=60),
                     VALUATION_DATE + timedelta(days=120),
                     pd.NaT,
                     VALUATION_DATE + timedelta(days=90),
                     VALUATION_DATE + timedelta(days=30),
                     pd.NaT],
        'Strike': [np.nan,np.nan,1.08,1.25,170,180,np.nan,175,1.07,np.nan],
        'OptionType': [np.nan,np.nan,np.nan,np.nan,'Call','Put',np.nan,'Call',np.nan,np.nan]
    }
    return pd.DataFrame(data)