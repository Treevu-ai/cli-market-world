"use client";

import { useMemo } from "react";
import type { Lang } from "@/lib/i18n";
import { useLang } from "@/lib/LanguageContext";
import { getProcureCopy } from "@/lib/procureLocale";
import { PROCURE_ES_PARTIAL, PROCURE_ES_TO_EN } from "@/lib/procureEnStrings";

function translateString(value: string, lang: Lang): string {
  if (lang === "es") return value;
  if (PROCURE_ES_TO_EN[value]) return PROCURE_ES_TO_EN[value];
  let out = value;
  for (const [pattern, replacement] of PROCURE_ES_PARTIAL) {
    out = out.replace(pattern, replacement);
  }
  return out;
}

/** Deep-clone data and translate string leaves for EN. */
export function overlayEnStrings<T>(value: T, lang: Lang): T {
  if (lang === "es") return value;
  if (typeof value === "string") return translateString(value, lang) as T;
  if (Array.isArray(value)) {
    return value.map((item) => overlayEnStrings(item, lang)) as T;
  }
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [key, child] of Object.entries(value as Record<string, unknown>)) {
      out[key] = overlayEnStrings(child, lang);
    }
    return out as T;
  }
  return value;
}

/** Merge procureLocale hero/finalCta over overlay (exact marketing copy). */
export function mergeProcureCopy<T extends Record<string, unknown>>(base: T, lang: Lang): T {
  if (lang === "es") return base;
  const copy = getProcureCopy(lang);
  const out = { ...base } as T & { hero?: unknown; finalCta?: unknown };
  if (out.hero && typeof out.hero === "object") {
    out.hero = { ...(out.hero as object), ...copy.hero, title: copy.hero.title };
  }
  if (out.finalCta && typeof out.finalCta === "object") {
    out.finalCta = { ...(out.finalCta as object), ...copy.finalCta };
  }
  return out as T;
}

export function localizeProcureData<T>(data: T, lang: Lang): T {
  return mergeProcureCopy(overlayEnStrings(data, lang), lang);
}

export function useProcureLocalized<T>(data: T): T {
  const { lang } = useLang();
  return useMemo(() => localizeProcureData(data, lang), [data, lang]);
}
