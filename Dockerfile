# Dockerfile
FROM python:3.11-slim

# Sätt arbetskatalog
WORKDIR /app

# Installera beroenden
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera koden
COPY . .

# Eksponera port
EXPOSE 8000

# Starta FastAPI med Uvicorn och Celery Worker
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload & celery -A celery_worker.celery_app worker --loglevel=info"]