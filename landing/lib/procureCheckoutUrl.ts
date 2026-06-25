import type { ProcurePlanSlug } from "@/lib/procurePlans";

const VALID_PLANS = new Set<ProcurePlanSlug>(["starter", "pro", "builder"]);

/** Deep link: ?audience=procure&plan=pro&checkout=open#pricing */
export function readProcureCheckoutDeepLink(): {
  plan: ProcurePlanSlug;
  open: boolean;
} | null {
  if (typeof window === "undefined") return null;
  const params = new URLSearchParams(window.location.search);
  if (params.get("audience") !== "procure") return null;
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
  url.searchParams.delete("checkout");
  url.searchParams.delete("plan");
  window.history.replaceState(null, "", url.pathname + url.search + url.hash);
}
