export const PLAYGROUND_API_KEY = "cli_market_api_key";
export const PLAYGROUND_DEMO_SEEN = "cli_market_playground_demo_seen";

export type PlaygroundMode = "demo" | "live";

export function readPlaygroundKey(): string {
  if (typeof window === "undefined") return "";
  try {
    return window.localStorage.getItem(PLAYGROUND_API_KEY) ?? "";
  } catch {
    return "";
  }
}

export function persistPlaygroundKey(key: string) {
  if (typeof window === "undefined") return;
  try {
    if (key.startsWith("sk-")) window.localStorage.setItem(PLAYGROUND_API_KEY, key);
    else window.localStorage.removeItem(PLAYGROUND_API_KEY);
  } catch {
    /* ignore */
  }
}

export function hasSeenPlaygroundDemo(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return window.localStorage.getItem(PLAYGROUND_DEMO_SEEN) === "1";
  } catch {
    return false;
  }
}

export function markPlaygroundDemoSeen() {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(PLAYGROUND_DEMO_SEEN, "1");
  } catch {
    /* ignore */
  }
}

export function scrollToPlayground(mode: PlaygroundMode = "live") {
  if (typeof window === "undefined") return;
  const target =
    document.getElementById("hero-playground-mobile") ??
    document.getElementById("hero-playground");
  if (target) {
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  } else {
    window.location.hash = "hero";
  }
  window.dispatchEvent(new CustomEvent("playground-focus", { detail: { mode } }));
}
