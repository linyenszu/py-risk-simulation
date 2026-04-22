import numpy as np

def apply_scenario(prices, returns):
    return prices * np.exp(returns)
