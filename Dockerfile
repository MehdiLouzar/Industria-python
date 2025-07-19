FROM python:3.10-slim

# Install utilities required by the application and health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run.py"]
