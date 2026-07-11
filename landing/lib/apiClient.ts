/** Thin typed fetch wrapper for new console code. Extends lib/api.ts (API_URL
 *  stays there) — existing components keep their own inline fetches unchanged. */
import { API_URL } from "@/lib/api";

export class ApiError extends Error {
  status: number;
  detail?: string;
  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

type ApiFetchOpts = {
  apiKey?: string | null;
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  params?: Record<string, string | number | undefined>;
};

export async function apiFetch<T>(path: string, opts: ApiFetchOpts = {}): Promise<T> {
  const { apiKey, method = "GET", body, params } = opts;

  let url = `${API_URL}${path}`;
  if (params) {
    const qs = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined) qs.set(k, String(v));
    }
    const qsStr = qs.toString();
    if (qsStr) url += (path.includes("?") ? "&" : "?") + qsStr;
  }

  const headers: Record<string, string> = {};
  if (apiKey) headers.Authorization = `Bearer ${apiKey}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  const r = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const responseBody = await r.json().catch(() => ({}));
  if (!r.ok) {
    const detail = responseBody?.detail || responseBody?.error;
    throw new ApiError(r.status, detail || `HTTP ${r.status}`, detail);
  }
  return (responseBody?.data ?? responseBody) as T;
}
