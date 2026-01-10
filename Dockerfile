FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/logs && \
    mkdir -p /app/data

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser

CMD ["python", "main.py"]