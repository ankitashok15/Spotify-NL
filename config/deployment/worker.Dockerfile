FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt celery[redis]

COPY phases ./phases

ENV PYTHONPATH=/app/phases/phase-01-data-foundation:/app/phases/phase-02-ai-understanding:/app/phases/phase-03-semantic-search:/app/phases/phase-04-rag-qa:/app/phases/phase-05-clustering-insights:/app/phases/phase-06-agentic-scale

CMD ["celery", "-A", "phase06.orchestration.celery_app:celery_app", "worker", "--loglevel=INFO"]
