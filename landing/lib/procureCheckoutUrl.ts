import type { ProcurePlanSlug } from "@/lib/procurePlans";
import { BUILD_PAGE } from "@/lib/siteNav";

const VALID_PLANS = new Set<ProcurePlanSlug>(["starter", "pro", "builder"]);

/** Build spoke hosts pricing; avoids home /#pricing legacy redirect stripping query params. */
const PROCURE_CHECKOUT_PATH = BUILD_PAGE;

/** Worker CTA: deep link to cli-market.dev/build with plan preselected + modal open. */
export function buildProcureSubscribeUrl(plan: ProcurePlanSlug): string {
  const params = new URLSearchParams({
    audience: "procure",
    plan,
    checkout: "open",
  });
  return `${PROCURE_CHECKOUT_PATH}?${params.toString()}#pricing`;
}

/** Absolute URL for external sites (procurecopilot.com CTAs). */
export function buildProcureSubscribeAbsoluteUrl(
  plan: ProcurePlanSlug,
  origin = "https://cli-market.dev",
): string {
  return `${origin.replace(/\/$/, "")}${buildProcureSubscribeUrl(plan)}`;
}

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
