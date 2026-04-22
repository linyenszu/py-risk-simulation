from src.data.generate_positions import generate_positions
from src.data.market_data import fetch_market_data
from src.risk.var import historical_var
import numpy as np

def main():
    positions = generate_positions()
    market_data = fetch_market_data("2020-01-01")

    returns = np.log(market_data / market_data.shift(1)).dropna()

    portfolio_returns = returns.sum(axis=1)

    var_99 = historical_var(portfolio_returns)

    print("=== Portfolio VaR (99%) ===")
    print(var_99)

if __name__ == "__main__":
    main()
