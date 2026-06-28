"use client";

import { useEffect } from "react";
import { resolveLegacyHashRedirect, urlsMatch } from "@/lib/legacyHashTargets";

/** Redirect legacy homepage hash anchors after hub split (Phase 1). */
export default function LegacyHashRedirect() {
  useEffect(() => {
    const target = resolveLegacyHashRedirect(
      window.location.pathname,
      window.location.search,
      window.location.hash,
    );
    if (!target) return;

    if (target.startsWith("http")) {
      window.location.replace(target);
      return;
    }

    const absolute = new URL(target, window.location.origin).href;
    if (urlsMatch(window.location.href, absolute)) return;

    window.location.replace(target);
  }, []);

  return null;
}
