# Model Methodology

## Greeks

Stocks are valued as `quantity * spot`. FX forwards use interest-rate parity with flat domestic and foreign curves. European options use Black-Scholes-Merton with flat rates, flat dividends, and flat implied volatilities.

## Historical Simulation VaR

The engine computes historical log returns for each market factor, applies each historical move to current market levels, fully revalues the current portfolio, and estimates VaR as the lower-tail P&L quantile.

## Stressed VaR

The stress window is selected around the worst observed return for the anchor ticker. The same full-revaluation engine is applied to the stress scenarios.

## Aggregation

Greeks are additive and are summed by hierarchy. VaR and sVaR are non-additive and are recalculated from grouped scenario P&L distributions.
