const API_BASE = import.meta.env.VITE_API_URL ?? "";

function parseApiError(status: number, body: string): string {
  try {
    const parsed = JSON.parse(body) as { detail?: string | { msg?: string }[] };
    if (typeof parsed.detail === "string") return parsed.detail;
    if (Array.isArray(parsed.detail)) {
      return parsed.detail.map((d) => d.msg ?? String(d)).join("; ");
    }
  } catch {
    /* not JSON */
  }
  if (body.includes("<!doctype") || body.includes("<html")) {
    return `API unreachable (${status}). Start the backend: python scripts/serve_api.py — or set VITE_API_URL for production.`;
  }
  return body || `Request failed (${status})`;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) },
      ...options,
    });
  } catch {
    throw new Error(
      "Cannot reach API. Run python scripts/serve_api.py (port 8080) or configure VITE_API_URL."
    );
  }
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(parseApiError(res.status, detail));
  }
  return res.json() as Promise<T>;
}

export interface DashboardStats {
  reviews_total: number;
  structured_total: number;
  vectors_indexed: number;
  clusters_total: number;
  insights_total: number;
  scrape_status: string | null;
  scrape_reviews_new: number;
  top_issues: { primary_issue: string; count: number }[];
}

export interface SearchHit {
  review_id: string;
  score: number;
  rating?: number;
  subscription_type?: string;
  device_type?: string;
  primary_issue?: string;
  text_en?: string;
}

export interface SearchResponse {
  query: string;
  results: SearchHit[];
  took_ms: number;
}

export interface Citation {
  id: number;
  document_id: string;
  excerpt?: string;
  rating?: number;
  subscription_type?: string;
  primary_issue?: string;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  confidence: number;
  took_ms: number;
}

export interface ClusterSummary {
  id: string;
  label: string;
  description?: string;
  member_count: number;
  avg_rating?: number;
  taxonomy_theme_id?: string;
}

export interface InsightItem {
  id: string;
  insight_type: string;
  title: string;
  summary: string;
  confidence?: number;
}

export interface AgentResponse {
  answer: string;
  citations: { review_id?: string; quote?: string; rating?: number }[];
  confidence: number;
  steps: number;
  took_ms: number;
  tool_trace?: { tool: string; result_summary: string }[];
}

export const api = {
  getStats: () => request<DashboardStats>("/api/v1/dashboard/stats"),
  search: (query: string, top_k = 10) =>
    request<SearchResponse>("/api/v1/search", {
      method: "POST",
      body: JSON.stringify({ query, top_k }),
    }),
  ask: (question: string) =>
    request<QueryResponse>("/api/v1/query", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
  agent: (question: string, debug = false) =>
    request<AgentResponse>("/api/v1/agent/query", {
      method: "POST",
      body: JSON.stringify({ question, debug, use_cache: true }),
    }),
  clusters: () => request<{ items: ClusterSummary[] }>("/api/v1/clusters"),
  cluster: (id: string) =>
    request<ClusterSummary & { member_review_ids: string[] }>(`/api/v1/clusters/${id}`),
  insights: () => request<{ items: InsightItem[] }>("/api/v1/insights"),
  trends: (months = 6) => request<unknown>(`/api/v1/trends?months=${months}`),
  reviews: (limit = 20) => request<{ items: unknown[]; total: number }>(`/api/v1/reviews?limit=${limit}`),
};
