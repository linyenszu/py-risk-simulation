install:
	pip install -e .[dev]

test:
	pytest -q

lint:
	ruff check .

run:
	python main.py --valuation-date 2025-04-04 --confidence 0.99
