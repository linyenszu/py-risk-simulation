PyRiskSimulation - Simulating Risk Pipelines in Python: Greeks, VaR, SVaR and Aggregation
===============================

The library involves not just calculating risk for individual trades but understanding how these risks interact and accumulate 
across the entire firm/organization. We need to know our Delta exposure to market movements, the Gamma risk associated with sharp price changes, 
the Vega sensitivity to volatility shifts and ultimately, the potential loss we might face under adverse market conditions (VaR) 
or specific historical stress events (Stressed VaR or SVaR). Aggregating these figures correctly, respecting diversification effects, 
up through the hierarchy — from specific portfolios, grouped into trading desks and finally consolidated at the unit level — is 
crucial for effective capital allocation and limit monitoring.

This library simulates exactly that complex data circuit. We will build a Python pipeline that mirrors 
the journey of data from a Murex-like operational source through to the calculation and hierarchical 
reporting of key risk figures. 

Prerequisites
-------------

* [QuantLib](http://www.quantlib.org) (version 1.5 or higher)

Documentation
-------------
Documentation is pretty rough. 
