FROM python:3.12-slim AS builder

WORKDIR /app

# First install system dependencies for building
RUN apt-get update && apt-get install -y \
    git \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    netcat-openbsd \
    default-mysql-client \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .
COPY --chown=appuser:appuser infra/wait-for-db.sh /usr/local/bin/wait-for-db.sh

RUN chmod +x /usr/local/bin/wait-for-db.sh

USER appuser

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
EXPOSE 8501

# Function to detect database type and start services
CMD ["sh", "-c", "if [ -n \"$DATABASE_URL\" ] && echo \"$DATABASE_URL\" | grep -q \"mysql\"; then DB_PORT=3306; else DB_PORT=5432; fi; wait-for-db.sh db $DB_PORT && uvicorn src.main:app --host 0.0.0.0 --port 8000 & streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]