const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

function ensureApiConfigured(): void {
  if (import.meta.env.PROD && !API_BASE) {
    throw new Error(
      "VITE_API_URL is not set. In Vercel → Project Settings → Environment Variables, add VITE_API_URL=https://your-render-api.onrender.com (no trailing slash), then redeploy. Do not use the Streamlit URL here."
    );
  }
}

function parseApiError(status: number, body: string): string {
  if (status === 405) {
    return (
      "HTTP 405 — API calls are hitting the Vercel static site, not your backend. " +
      "Set VITE_API_URL to your Render/FastAPI URL (e.g. https://spotify-nl-api.onrender.com) in Vercel environment variables and redeploy."
    );
  }
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
    return `API unreachable (${status}). Set VITE_API_URL to your Render API URL, or run python scripts/serve_api.py locally.`;
  }
  return body || `Request failed (${status})`;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  ensureApiConfigured();
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) },
      ...options,
    });
  } catch {
    throw new Error(
      API_BASE
        ? `Cannot reach API at ${API_BASE}. Check that Render is running and CORS allows your Vercel domain.`
        : "Cannot reach API. Run python scripts/serve_api.py (port 8080) or set VITE_API_URL on Vercel."
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
