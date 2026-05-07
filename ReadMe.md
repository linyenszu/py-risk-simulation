# Py Risk Simulation

Production-style Python repository that simulates a Murex-like front-office risk pipeline for positions, market data, Greeks, Historical Simulation VaR, stressed VaR, and desk/unit aggregation.

## Capabilities

- Generate synthetic stock, FX forward, and European option positions
- Generate portfolio-to-desk-to-unit hierarchy data
- Load market data with a deterministic fallback for offline execution
- Price instruments and calculate Greeks
- Revalue positions under historical scenarios
- Compute VaR and stressed VaR
- Aggregate risk by portfolio, trading desk, and business unit
- Run tests and pipeline from CLI, Makefile, Docker, or notebooks

## Repository Layout

See `Repository_Structure.txt` for the requested structure this implementation follows.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
pytest
```

## Pipeline

```bash
python scripts/bootstrap_data.py
python main.py
```

Outputs are written to `data/processed/` and `data/outputs/`.

## Notes

QuantLib-Python is optional. If it is unavailable, the project uses a pure-Python Black-Scholes fallback for European options so the repo remains runnable in lightweight environments.
