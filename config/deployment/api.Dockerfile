FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY phases ./phases
COPY scripts ./scripts
COPY config ./config

ENV PYTHONPATH=/app/phases/phase-01-data-foundation:/app/phases/phase-02-ai-understanding:/app/phases/phase-03-semantic-search:/app/phases/phase-04-rag-qa:/app/phases/phase-05-clustering-insights:/app/phases/phase-06-agentic-scale

EXPOSE 8004
CMD ["python", "phases/phase-06-agentic-scale/cli/serve.py"]
