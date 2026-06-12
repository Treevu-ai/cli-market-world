import { API_URL } from "@/lib/api";

export const PLAYGROUND_DEMO_TOKEN = "cli_market_demo_token";

export type DemoSession = {
  demo_token: string;
  expires_at?: string;
  max_requests?: number;
  requests_remaining?: number;
};

export function readDemoToken(): string {
  if (typeof window === "undefined") return "";
  try {
    return window.localStorage.getItem(PLAYGROUND_DEMO_TOKEN) ?? "";
  } catch {
    return "";
  }
}

export function persistDemoToken(token: string) {
  if (typeof window === "undefined") return;
  try {
    if (token.startsWith("demo-")) window.localStorage.setItem(PLAYGROUND_DEMO_TOKEN, token);
    else window.localStorage.removeItem(PLAYGROUND_DEMO_TOKEN);
  } catch {
    /* ignore */
  }
}

export async function ensureDemoSession(fingerprint = ""): Promise<DemoSession | null> {
  const cached = readDemoToken();
  if (cached.startsWith("demo-")) {
    return { demo_token: cached };
  }
  try {
    const res = await fetch(`${API_URL}/public/demo/session`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(fingerprint ? { "X-Demo-Fingerprint": fingerprint } : {}),
      },
      body: JSON.stringify({ fingerprint }),
    });
    if (!res.ok) return null;
    const data = (await res.json()) as DemoSession;
    if (data.demo_token) persistDemoToken(data.demo_token);
    return data;
  } catch {
    return null;
  }
}
