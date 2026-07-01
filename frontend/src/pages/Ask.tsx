import { FormEvent, useState } from "react";
import { api, Citation, QueryResponse } from "../api/client";

export function AskPage() {
  const [question, setQuestion] = useState("Why do free users hate playlist recommendations?");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setResult(await api.ask(question));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className="page-title">Ask (RAG)</h1>
      <p className="page-sub">Citation-backed answers from real Play Store reviews</p>
      <form className="form-row" onSubmit={onSubmit}>
        <input value={question} onChange={(e) => setQuestion(e.target.value)} />
        <button type="submit" disabled={loading}>{loading ? "Thinking…" : "Ask"}</button>
      </form>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="panel">
          <p className="meta">Confidence {(result.confidence * 100).toFixed(0)}% · {result.took_ms.toFixed(0)} ms</p>
          <div className="result-box">{result.answer}</div>
          {result.citations.map((c: Citation) => (
            <div className="citation" key={c.id}>
              <div className="meta">
                ★ {c.rating} · {c.subscription_type} · {c.primary_issue}
              </div>
              {c.excerpt}
            </div>
          ))}
        </div>
      )}
    </>
  );
}
