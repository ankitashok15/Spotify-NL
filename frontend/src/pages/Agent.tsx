import { FormEvent, useState } from "react";
import { api, AgentResponse } from "../api/client";

export function AgentPage() {
  const [question, setQuestion] = useState(
    "What discovery issues do free phone users report most, and how has that changed in 2026?"
  );
  const [result, setResult] = useState<AgentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setResult(await api.agent(question, true));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Agent failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className="page-title">Agent</h1>
      <p className="page-sub">Multi-step analysis with tool trace</p>
      <form onSubmit={onSubmit}>
        <textarea
          rows={3}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={{ marginBottom: "1rem" }}
        />
        <button type="submit" disabled={loading}>{loading ? "Running…" : "Run agent"}</button>
      </form>
      {error && <div className="error">{error}</div>}
      {result && (
        <>
          <div className="panel" style={{ marginTop: "1.5rem" }}>
            <p className="meta">
              {result.steps} steps · confidence {(result.confidence * 100).toFixed(0)}% · {result.took_ms.toFixed(0)} ms
            </p>
            <div className="result-box">{result.answer}</div>
          </div>
          {result.tool_trace && result.tool_trace.length > 0 && (
            <div className="panel">
              <h2>Tool trace</h2>
              {result.tool_trace.map((step, i) => (
                <div className="trace-step" key={i}>
                  <strong>{step.tool}</strong> — {step.result_summary}
                </div>
              ))}
            </div>
          )}
          {result.citations?.map((c, i) => (
            <div className="citation" key={i}>
              <div className="meta">★ {c.rating}</div>
              {c.quote}
            </div>
          ))}
        </>
      )}
    </>
  );
}
