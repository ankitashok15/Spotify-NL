import { useEffect, useState } from "react";
import { api, ClusterSummary } from "../api/client";

export function ThemesPage() {
  const [clusters, setClusters] = useState<ClusterSummary[]>([]);
  const [selected, setSelected] = useState<(ClusterSummary & { member_review_ids?: string[] }) | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .clusters()
      .then((r) => setClusters(r.items))
      .catch((e) => setError(e.message));
  }, []);

  async function openCluster(id: string) {
    try {
      setSelected(await api.cluster(id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load cluster");
    }
  }

  return (
    <>
      <h1 className="page-title">Discovery Themes</h1>
      <p className="page-sub">Clustered pain points from review embeddings</p>
      {error && <div className="error">{error}</div>}
      {clusters.length === 0 && !error && (
        <p className="meta">No clusters yet — run Phase 5 clustering first.</p>
      )}
      {clusters.map((c) => (
        <div className="cluster-card" key={c.id} onClick={() => openCluster(c.id)} style={{ cursor: "pointer" }}>
          <strong>{c.label}</strong>
          <div className="meta">
            {c.member_count} reviews · avg ★ {c.avg_rating ?? "—"}
            {c.taxonomy_theme_id && ` · ${c.taxonomy_theme_id}`}
          </div>
          {c.description && <p style={{ margin: "0.5rem 0 0", fontSize: "0.9rem" }}>{c.description}</p>}
        </div>
      ))}
      {selected && (
        <div className="panel" style={{ marginTop: "1.5rem" }}>
          <h2>{selected.label}</h2>
          <p>{selected.description}</p>
          <p className="meta">Sample review IDs: {(selected.member_review_ids ?? []).slice(0, 5).join(", ")}</p>
          <button className="secondary" onClick={() => setSelected(null)} style={{ marginTop: "0.5rem" }}>
            Close
          </button>
        </div>
      )}
    </>
  );
}
