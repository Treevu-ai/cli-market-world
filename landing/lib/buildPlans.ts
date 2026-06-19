/** Build (API) tier labels — distinct from Procure Compare/Ops/Scale. */

export type BuildPlanSlug = "starter" | "pro" | "pro_founding" | "pro_annual";

export const BUILD_PLAN_LABELS: Record<BuildPlanSlug, { es: string; en: string }> = {
  starter: { es: "Build Starter", en: "Build Starter" },
  pro: { es: "Build Pro", en: "Build Pro" },
  pro_founding: { es: "Build Pro Founding", en: "Build Pro Founding" },
  pro_annual: { es: "Build Pro (anual)", en: "Build Pro (annual)" },
};

export function normalizeBuildPlanSlug(raw: string | null | undefined): BuildPlanSlug | null {
  if (!raw) return null;
  const slug = raw.trim().toLowerCase().replace(/-/g, "_");
  if (slug in BUILD_PLAN_LABELS) return slug as BuildPlanSlug;
  if (slug === "founding") return "pro_founding";
  if (slug === "annual") return "pro_annual";
  return null;
}

export function buildPlanLabel(slug: BuildPlanSlug | null, isES: boolean): string | null {
  if (!slug) return null;
  return isES ? BUILD_PLAN_LABELS[slug].es : BUILD_PLAN_LABELS[slug].en;
}
