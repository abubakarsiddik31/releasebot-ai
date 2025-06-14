FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

RUN mkdir -p logs

EXPOSE 8000 8501

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"] 