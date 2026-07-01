# Phase 2 Requirements — AI Understanding

## Scope

Transform every scraped Google Play review into structured, queryable fields for discovery and recommendation analysis.

## Functional requirements

### FR-2.1 Language detection & translation

- [ ] Detect language per review
- [ ] Translate non-English to `text_en`; keep `text_original`
- [ ] Support multilingual Play Store corpus

### FR-2.2 Structured LLM extraction

- [ ] Extract: summary, primary_issue, secondary_issues, emotions, sentiment, recommendation_quality, user_intent, listening_context, mentioned_features, feature_requests, pain_points, behaviors, severity, urgency, subscription_type, user_persona_signals, is_discovery_related, confidence
- [ ] Batch 20–50 reviews per LLM call with JSON schema output
- [ ] Pydantic validation; retry on malformed output
- [ ] Post-process feature name normalization (`DW` → `discover_weekly`)

### FR-2.3 Play Store metadata enrichment

- [ ] Cross-check sentiment with star rating
- [ ] Weight by `thumbs_up`
- [ ] Segment by `device_type`, `app_version`
- [ ] Track `developer_reply` for resolved/unresolved flag

### FR-2.4 Persistence

- [ ] `structured_reviews` table linked to `reviews.id`
- [ ] Update `processing_state` to `EXTRACTED`

## Exit criteria

- 90%+ schema validity on 500-review sample
- `is_discovery_related` correctly tagged
- SQL filters work: `subscription_type`, `primary_issue`, `device_type`
