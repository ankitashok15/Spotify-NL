import { useEffect, useState } from "react";
import { api, InsightItem } from "../api/client";

export function InsightsPage() {
  const [items, setItems] = useState<InsightItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .insights()
      .then((r) => setItems(r.items))
      .catch((e) => setError(e.message));
  }, []);

  return (
    <>
      <h1 className="page-title">Insights</h1>
      <p className="page-sub">Generated product intelligence reports</p>
      {error && <div className="error">{error}</div>}
      {items.length === 0 && !error && (
        <p className="meta">No insights yet — run Phase 5 insights pipeline.</p>
      )}
      {items.map((item) => (
        <div className="insight-card" key={item.id}>
          <span className="badge">{item.insight_type}</span>
          <strong style={{ display: "block", margin: "0.5rem 0 0.25rem" }}>{item.title}</strong>
          <p style={{ margin: 0, fontSize: "0.9rem", color: "var(--muted)" }}>{item.summary}</p>
        </div>
      ))}
    </>
  );
}
