FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml setup.py README.md ./
COPY src ./src
COPY main.py ./main.py
RUN pip install --no-cache-dir -e .
CMD ["python", "main.py", "--valuation-date", "2025-04-04"]
