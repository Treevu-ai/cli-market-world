import { API_URL } from "@/lib/api";

const SESSION_KEY = "cm-funnel-session";
const INSTALL_REPORTED_KEY = "cm-funnel-install-reported";

export type FunnelEvent =
  | "install"
  | "login"
  | "register"
  | "first_search"
  | "starter_subscribe"
  | "starter_request"
  | "request_pro"
  | "procure_subscribe"
  | "use_case_demo"
  | "icp_door_click"
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

/** Record pip install intent once per browser (Hero, docs, how-it-works). */
export function recordPipInstallIntent(source: string): void {
  if (typeof window === "undefined") return;
  try {
    if (window.localStorage.getItem(INSTALL_REPORTED_KEY)) return;
    recordFunnelEvent("install", {
      meta: { source },
      dedupe: true,
    });
    window.localStorage.setItem(INSTALL_REPORTED_KEY, source);
  } catch {
    recordFunnelEvent("install", { meta: { source }, dedupe: true });
  }
}

export function scrollToProCheckout(): void {
  document.getElementById("pro-checkout")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

export function scrollToPricing(): void {
  document.getElementById("pricing")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

/** Funnel: user opened a terminalizer use-case demo modal. */
export function recordUseCaseDemoOpen(useCaseId: string): void {
  recordFunnelEvent("use_case_demo", {
    meta: { use_case_id: useCaseId, source: "landing_casos" },
    dedupe: false,
  });
}

export type IcpDoorId = "build" | "procure" | "advisor" | "retailers";

/** Hub router: user selected an ICP door on the landing home. */
export function recordIcpDoorClick(door: IcpDoorId, source = "hub"): void {
  recordFunnelEvent("icp_door_click", {
    meta: { door, source },
    dedupe: false,
  });
}
