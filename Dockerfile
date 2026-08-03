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

# PYTHONPATH ensures 'from app.xxx import ...' resolves when alembic/uvicorn run as console scripts
ENV PYTHONPATH=/app

# Install dependencies first (layer cache)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all backend application code
COPY backend/ .

# Make startup script executable
RUN chmod +x start.sh

CMD ["sh", "start.sh"]
