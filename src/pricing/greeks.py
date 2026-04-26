from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.helpers import bs_price_greeks, year_fraction


def _price_fx_forward(quantity: float, spot: float, strike: float, maturity, valuation_date, domestic_rate: float, foreign_rate: float):
    t = year_fraction(valuation_date, maturity)
    if t <= 0:
        return {'npv': 0.0, 'delta': 0.0, 'gamma': 0.0, 'vega': 0.0, 'theta': 0.0, 'rho': 0.0}
    domestic_df = np.exp(-domestic_rate * t)
    foreign_df = np.exp(-foreign_rate * t)
    forward = spot * foreign_df / domestic_df
    npv = quantity * (forward - strike) * domestic_df
    delta = quantity * (foreign_df / domestic_df) * domestic_df
    return {'npv': npv, 'delta': delta, 'gamma': 0.0, 'vega': 0.0, 'theta': 0.0, 'rho': 0.0}


def calculate_position_greeks(positions_df: pd.DataFrame, valuation_date, settings) -> pd.DataFrame:
    result = positions_df.copy()
    for greek in ['NPV', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho']:
        result[greek] = 0.0

    for index, row in result.iterrows():
        instrument_type = row['InstrumentType']
        quantity = float(row['Quantity'])
        spot = float(row['CurrentPrice'])

        if instrument_type == 'Stock':
            metrics = {'npv': quantity * spot, 'delta': quantity, 'gamma': 0.0, 'vega': 0.0, 'theta': 0.0, 'rho': 0.0}
        elif instrument_type == 'FX Forward' and pd.notna(row['Maturity']) and pd.notna(row['Strike']):
            foreign_rate = settings.eur_rate if row['Ticker'] == 'EURUSD=X' else settings.gbp_rate
            metrics = _price_fx_forward(quantity, spot, float(row['Strike']), row['Maturity'], valuation_date, settings.flat_usd_rate, foreign_rate)
        elif instrument_type == 'European Option' and pd.notna(row['Maturity']) and pd.notna(row['Strike']) and pd.notna(row['OptionType']):
            t = year_fraction(valuation_date, row['Maturity'])
            greeks = bs_price_greeks(
                spot=spot,
                strike=float(row['Strike']),
                rate=settings.flat_usd_rate,
                dividend=settings.flat_dividend_yield,
                vol=settings.ticker_vols.get(row['Ticker'], 0.20),
                t=t,
                option_type=str(row['OptionType']),
            )
            metrics = {k: v * quantity for k, v in greeks.items()}
        else:
            metrics = {'npv': np.nan, 'delta': np.nan, 'gamma': np.nan, 'vega': np.nan, 'theta': np.nan, 'rho': np.nan}

        result.loc[index, 'NPV'] = metrics['npv']
        result.loc[index, 'Delta'] = metrics['delta']
        result.loc[index, 'Gamma'] = metrics['gamma']
        result.loc[index, 'Vega'] = metrics['vega']
        result.loc[index, 'Theta'] = metrics['theta']
        result.loc[index, 'Rho'] = metrics['rho']

    return result
