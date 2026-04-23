from __future__ import annotations

import pandas as pd


def generate_structure() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'Portfolio': ['P1_EqUS', 'P2_FXMaj', 'P3_OptEq', 'P4_OptSpec'],
            'TradingDesk': ['Equity Desk', 'FX Desk', 'Options Desk', 'Options Desk'],
            'Unit': ['Trading Unit A', 'Trading Unit A', 'Trading Unit B', 'Trading Unit B'],
        }
    )
