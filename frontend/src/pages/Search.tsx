import { FormEvent, useState } from "react";
import { api, SearchHit } from "../api/client";

export function SearchPage() {
  const [query, setQuery] = useState("free users hate playlist recommendations");
  const [hits, setHits] = useState<SearchHit[]>([]);
  const [took, setTook] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.search(query);
      setHits(res.results);
      setTook(res.took_ms);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className="page-title">Semantic Search</h1>
      <p className="page-sub">Find reviews by meaning, not keywords</p>
      <form className="form-row" onSubmit={onSubmit}>
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search query…" />
        <button type="submit" disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
      </form>
      {error && <div className="error">{error}</div>}
      {took !== null && <p className="meta">{hits.length} results · {took.toFixed(0)} ms</p>}
      {hits.map((h) => (
        <div className="hit-card" key={h.review_id}>
          <div className="hit-meta">
            <span className="badge">★ {h.rating ?? "?"}</span>
            {h.subscription_type && <span className="badge">{h.subscription_type}</span>}
            {h.primary_issue && <span className="badge">{h.primary_issue}</span>}
            <span>score {h.score.toFixed(3)}</span>
          </div>
          <p>{h.text_en || "No text"}</p>
        </div>
      ))}
    </>
  );
}
