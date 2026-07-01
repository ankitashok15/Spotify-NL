# Insights Requirements

**Phase:** 5  
**Source:** `src/insights/`

## Modules

| Module | Responsibility |
|--------|----------------|
| `aggregator.py` | Top complaints by frequency, severity, recency |
| `emerging.py` | Cluster growth rate vs prior window |
| `trends.py` | Time-series per theme, rating, subscription |
| `root_cause.py` | LLM synthesis across cluster evidence |
| `opportunities.py` | Unmet needs, feature request co-occurrence |
| `reporter.py` | Scheduled weekly report generation |

## Insight types

| Type | Output |
|------|--------|
| `top_complaint` | Ranked issues with counts |
| `emerging_issue` | Growing clusters (>20% in 30d) |
| `feature_request` | Frequency-ranked requests |
| `root_cause` | Pattern synthesis with evidence IDs |
| `segment_analysis` | Free vs Premium, device breakdown |

## Insight record schema

`insight_id`, `type`, `title`, `summary`, `confidence`, `evidence_document_ids[]`, `affected_personas[]`, `generated_at`

## Dashboard (optional frontend)

- `src/dashboard/` or separate `frontend/` package
- Top 10 themes, sentiment charts, timeline, drill-down to reviews

## Storage

- Table: `insights`
- Insights embedded for RAG retrieval ("top emerging complaints this month")
