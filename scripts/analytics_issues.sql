-- Phase 2 analytics: top primary_issue by rating and subscription

SELECT
    r.rating,
    s.subscription_type,
    s.primary_issue,
    COUNT(*) AS review_count,
    ROUND(AVG(s.confidence)::numeric, 2) AS avg_confidence,
    SUM(CASE WHEN s.is_discovery_related THEN 1 ELSE 0 END) AS discovery_related_count
FROM structured_reviews s
JOIN reviews r ON r.id = s.review_id
WHERE s.primary_issue IS NOT NULL
GROUP BY r.rating, s.subscription_type, s.primary_issue
ORDER BY review_count DESC
LIMIT 50;

-- Discovery-related issues by device type

SELECT
    r.device_type,
    s.primary_issue,
    COUNT(*) AS review_count
FROM structured_reviews s
JOIN reviews r ON r.id = s.review_id
WHERE s.is_discovery_related = TRUE
GROUP BY r.device_type, s.primary_issue
ORDER BY review_count DESC
LIMIT 30;
