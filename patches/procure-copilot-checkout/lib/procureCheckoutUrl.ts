import type { ProcurePlanSlug } from "@/lib/procurePlans";

const VALID_PLANS = new Set<ProcurePlanSlug>(["starter", "pro", "builder"]);

/** On-site subscribe route — no audience=procure query needed. */
export function buildProcureSubscribeUrl(plan: ProcurePlanSlug): string {
  const params = new URLSearchParams({ plan, checkout: "open" });
  return `/subscribe?${params.toString()}`;
}

export function readProcureCheckoutDeepLink(): {
  plan: ProcurePlanSlug;
  open: boolean;
} | null {
  if (typeof window === "undefined") return null;
  const params = new URLSearchParams(window.location.search);
  const raw = (params.get("plan") || "").trim().toLowerCase();
  if (!VALID_PLANS.has(raw as ProcurePlanSlug)) return null;
  const open =
    params.get("checkout") === "open" ||
    params.get("checkout") === "1" ||
    params.get("checkout") === "true";
  return { plan: raw as ProcurePlanSlug, open };
}

export function clearProcureCheckoutQuery(): void {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  for (const key of ["checkout", "plan", "sub", "mp", "ref", "audience", "payment"]) {
    url.searchParams.delete(key);
  }
  window.history.replaceState(null, "", url.pathname + url.search + url.hash);
}
