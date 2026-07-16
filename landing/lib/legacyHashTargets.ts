import { ADVISOR_PAGE, BUILD_PAGE } from "@/lib/siteNav";
import { PROCURE_LANDING_URL } from "@/lib/procurePlans";

/** Legacy homepage hash anchors → spoke paths (Phase 1 hub split). */
export const LEGACY_HASH_TARGETS: Record<string, string> = {
  pricing: `${BUILD_PAGE}#pricing`,
  "pro-checkout": `${BUILD_PAGE}#pro-checkout`,
  "pricing-build": `${BUILD_PAGE}#pricing`,
  intelligence: ADVISOR_PAGE,
  procure: PROCURE_LANDING_URL,
  "who-its-for": "/",
  faq: `${BUILD_PAGE}#faq`,
  "use-cases": BUILD_PAGE,
};

const PRICING_HASHES = new Set(["pricing", "pricing-build", "pro-checkout"]);

/** Preserve query string when redirecting pricing hashes (Procure checkout deep links). */
export function withPreservedSearch(pathWithHash: string, search: string): string {
  if (!search) return pathWithHash;
  const q = search.startsWith("?") ? search : `?${search}`;
  const hashIdx = pathWithHash.indexOf("#");
  if (hashIdx === -1) return `${pathWithHash}${q}`;
  return `${pathWithHash.slice(0, hashIdx)}${q}${pathWithHash.slice(hashIdx)}`;
}

export function resolveLegacyHashRedirect(
  pathname: string,
  search: string,
  hash: string,
): string | null {
  const bare = hash.replace(/^#/, "");
  if (!bare) return null;

  const baseTarget = LEGACY_HASH_TARGETS[bare];
  if (!baseTarget) return null;

  if (baseTarget.startsWith("http")) {
    return baseTarget;
  }

  const onHome = pathname === "/" || pathname === "";
  const isPricingHash = PRICING_HASHES.has(bare);
  if (!onHome && !isPricingHash && bare !== "faq") {
    return null;
  }

  const target = isPricingHash ? withPreservedSearch(baseTarget, search) : baseTarget;
  return target;
}

export function urlsMatch(currentHref: string, targetPath: string): boolean {
  try {
    const current = new URL(currentHref);
    const target = new URL(targetPath, current.origin);
    return (
      current.pathname === target.pathname &&
      current.search === target.search &&
      current.hash === target.hash
    );
  } catch {
    return false;
  }
}
