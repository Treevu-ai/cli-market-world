/** H1 A/B variants — see docs/landing/h1-ab-variants.md */

export const HERO_VARIANT_IDS = ["a", "b", "c", "d", "e", "f"] as const;
export type HeroVariantId = (typeof HERO_VARIANT_IDS)[number];

const H1_COPY: Record<HeroVariantId, { es: string; en: string }> = {
  a: {
    es: "La capa programable del retail físico de LatAm.",
    en: "The programmable layer for physical retail in LatAm.",
  },
  b: {
    es: "Una API. 30 retailers verificados. 8 países.",
    en: "One API. 30 verified retailers. 8 countries.",
  },
  c: {
    es: "Los agentes ya compran solos. Conéctalos al retail de LatAm.",
    en: "Agents already buy on their own. Connect them to LatAm retail.",
  },
  d: {
    es: "La API para agentes. El canal para tu tienda. Gratis.",
    en: "The API for agents. The channel for your store. Free.",
  },
  e: {
    es: "{priceChip} precios de góndola. Una API. Cero scraping.",
    en: "{priceChip} shelf prices. One API. Zero scraping.",
  },
  f: {
    es: "Del search al checkout autónomo en retail físico.",
    en: "From search to autonomous checkout in physical retail.",
  },
};

export function resolveHeroVariant(raw?: string): HeroVariantId {
  const v = raw?.trim().toLowerCase();
  if (v && HERO_VARIANT_IDS.includes(v as HeroVariantId)) {
    return v as HeroVariantId;
  }
  return "a";
}

export function getHeroH1(
  variant: HeroVariantId,
  lang: "es" | "en",
  priceChip = "43K+",
): string {
  const copy = H1_COPY[variant][lang];
  return copy.replace("{priceChip}", priceChip);
}

/** Build-time variant from NEXT_PUBLIC_HERO_VARIANT (defaults to a). */
export const ACTIVE_HERO_VARIANT = resolveHeroVariant(
  process.env.NEXT_PUBLIC_HERO_VARIANT,
);
