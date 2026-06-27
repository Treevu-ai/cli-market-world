"use client";

import { useEffect } from "react";
import { PROCURE_LANDING_URL } from "@/lib/procurePlans";
import { BUILD_PAGE, INTELLIGENCE_PAGE } from "@/lib/siteNav";

const LEGACY_HASH_TARGETS: Record<string, string> = {
  pricing: `${BUILD_PAGE}#pricing`,
  "pro-checkout": `${BUILD_PAGE}#pro-checkout`,
  "pricing-build": `${BUILD_PAGE}#pricing`,
  intelligence: INTELLIGENCE_PAGE,
  procure: PROCURE_LANDING_URL,
  "who-its-for": "/",
  faq: `${BUILD_PAGE}#faq`,
  "use-cases": BUILD_PAGE,
};

/** Redirect legacy homepage hash anchors after hub split (Phase 1). */
export default function LegacyHashRedirect() {
  useEffect(() => {
    const hash = window.location.hash.replace(/^#/, "");
    if (!hash) return;
    const target = LEGACY_HASH_TARGETS[hash];
    if (!target) return;

    if (target.startsWith("http")) {
      window.location.replace(target);
      return;
    }

    const onHome = window.location.pathname === "/" || window.location.pathname === "";
    if (onHome || hash === "pricing" || hash === "faq" || hash === "pro-checkout") {
      window.location.replace(target);
    }
  }, []);

  return null;
}
