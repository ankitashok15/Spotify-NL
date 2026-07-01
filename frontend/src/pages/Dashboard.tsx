import { useEffect, useState } from "react";
import { api, DashboardStats } from "../api/client";

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getStats()
      .then(setStats)
      .catch((e) => setError(e.message));
  }, []);

  const maxCount = Math.max(...(stats?.top_issues.map((i) => i.count) ?? [1]), 1);

  return (
    <>
      <h1 className="page-title">Discovery Dashboard</h1>
      <p className="page-sub">Google Play review intelligence for Spotify music discovery</p>
      {error && <div className="error">{error}</div>}
      {stats && (
        <>
          <div className="grid-stats">
            <Stat label="Reviews" value={stats.reviews_total} />
            <Stat label="Structured" value={stats.structured_total} />
            <Stat label="Vectors" value={stats.vectors_indexed} />
            <Stat label="Clusters" value={stats.clusters_total} />
            <Stat label="Insights" value={stats.insights_total} />
            <Stat label="Last scrape" value={stats.scrape_status ?? "—"} />
          </div>
          <div className="panel">
            <h2>Top discovery issues</h2>
            {stats.top_issues.length === 0 && (
              <p className="meta">Run Phase 2 extraction to populate structured issues.</p>
            )}
            {stats.top_issues.map((issue) => (
              <div className="bar-row" key={issue.primary_issue}>
                <span className="bar-label">{issue.primary_issue}</span>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{ width: `${(issue.count / maxCount) * 100}%` }}
                  />
                </div>
                <span className="bar-count">{issue.count}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}
