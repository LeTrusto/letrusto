FROM python:3.11-slim

# System libs required by cryptography, bcrypt, and python-jose
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# PORT is injected by Railway; run migrations and production DB sync before serving traffic
CMD alembic upgrade head && python -m scripts.init_production_db && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
