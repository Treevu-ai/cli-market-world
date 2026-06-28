import type { ProcurePlanSlug } from "@/lib/procurePlans";
import { PROCURE_SITE_URL } from "@/lib/procurePlans";

const VALID_PLANS = new Set<ProcurePlanSlug>(["starter", "pro", "builder"]);

/** Procure SaaS checkout lives on the sister site (Phase 2). */
const PROCURE_SUBSCRIBE_PATH = "/subscribe";

/** CTA: procurecopilot.com/subscribe with plan preselected + modal open. */
export function buildProcureSubscribeUrl(plan: ProcurePlanSlug): string {
  const params = new URLSearchParams({
    plan,
    checkout: "open",
  });
  return `${PROCURE_SUBSCRIBE_PATH}?${params.toString()}`;
}

export function buildProcureSubscribeAbsoluteUrl(
  plan: ProcurePlanSlug,
  origin: string = PROCURE_SITE_URL,
): string {
  return `${origin.replace(/\/$/, "")}${buildProcureSubscribeUrl(plan)}`;
}

/** Legacy deep link on cli-market.dev — used only to redirect to procurecopilot.com. */
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
  url.searchParams.delete("audience");
  window.history.replaceState(null, "", url.pathname + url.search + url.hash);
}

/** Redirect legacy cli-market.dev/?audience=procure links to procurecopilot.com/subscribe. */
export function redirectLegacyProcureCheckout(): boolean {
  if (typeof window === "undefined") return false;
  const link = readProcureCheckoutDeepLink();
  if (!link) return false;
  const target = buildProcureSubscribeAbsoluteUrl(link.plan);
  const url = new URL(target);
  if (link.open) url.searchParams.set("checkout", "open");
  window.location.replace(url.toString());
  return true;
}
