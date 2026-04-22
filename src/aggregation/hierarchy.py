def aggregate(df):
    return df.groupby(['Unit','TradingDesk']).sum(numeric_only=True)
