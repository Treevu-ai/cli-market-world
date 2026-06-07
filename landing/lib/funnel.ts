import { API_URL } from "@/lib/api";

const SESSION_KEY = "cm-funnel-session";

export type FunnelEvent =
  | "install"
  | "login"
  | "register"
  | "first_search"
  | "starter_subscribe"
  | "starter_request"
  | "request_pro"
  | "activated";

function newSessionId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `sess-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

/** Persistent anonymous session for landing funnel (first-party, no PII). */
export function getFunnelSessionId(): string {
  if (typeof window === "undefined") return "ssr";
  try {
    let sid = window.localStorage.getItem(SESSION_KEY);
    if (!sid) {
      sid = newSessionId();
      window.localStorage.setItem(SESSION_KEY, sid);
    }
    return sid;
  } catch {
    return newSessionId();
  }
}

export function recordFunnelEvent(
  event: FunnelEvent,
  opts?: {
    username?: string;
    meta?: Record<string, unknown>;
    dedupe?: boolean;
  },
): void {
  if (typeof window === "undefined") return;

  const body: Record<string, unknown> = {
    event,
    session_id: getFunnelSessionId(),
  };
  if (opts?.username) body.username = opts.username;
  if (opts?.meta) body.meta = opts.meta;
  if (opts?.dedupe != null) body.dedupe = opts.dedupe;

  fetch(`${API_URL}/v1/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    keepalive: true,
  }).catch(() => {});
}

export function scrollToStarterCheckout(): void {
  document.getElementById("starter-checkout")?.scrollIntoView({ behavior: "smooth", block: "start" });
}