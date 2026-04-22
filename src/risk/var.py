import numpy as np

def historical_var(pnl, confidence=0.99):
    return np.percentile(pnl, (1 - confidence) * 100)
