import {
  HERO_VARIANT_COOKIE,
  HERO_VARIANT_COOKIE_MAX_AGE,
  HERO_VARIANT_IDS,
  type HeroVariantId,
  pickRandomHeroVariant,
  resolveHeroVariant,
} from "@/lib/heroVariants";

function readCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function writeCookie(name: string, value: string): void {
  if (typeof document === "undefined") return;
  document.cookie = `${name}=${encodeURIComponent(value)};path=/;max-age=${HERO_VARIANT_COOKIE_MAX_AGE};SameSite=Lax`;
}

export function readUrlHeroOverride(): HeroVariantId | null {
  if (typeof window === "undefined") return null;
  const v = new URLSearchParams(window.location.search).get("hero");
  return v ? resolveHeroVariant(v) : null;
}

function persistVariant(variant: HeroVariantId): void {
  writeCookie(HERO_VARIANT_COOKIE, variant);
  if (typeof document !== "undefined") {
    document.documentElement.dataset.heroVariant = variant;
  }
}

function readStickyVariant(): HeroVariantId | null {
  if (typeof document !== "undefined") {
    const fromDom = document.documentElement.dataset.heroVariant;
    if (fromDom) {
      const v = resolveHeroVariant(fromDom);
      if (HERO_VARIANT_IDS.includes(v)) return v;
    }
  }
  const fromCookie = readCookie(HERO_VARIANT_COOKIE);
  if (fromCookie && HERO_VARIANT_IDS.includes(fromCookie as HeroVariantId)) {
    return fromCookie as HeroVariantId;
  }
  return null;
}

/**
 * Resolve active variant:
 * 1. ?hero= always wins (QA / share links) — works with or without AB
 * 2. AB on: sticky cookie → random
 * 3. AB off: NEXT_PUBLIC_HERO_VARIANT (default a)
 */
export function resolveHeroVariantForSession(
  abEnabled: boolean,
  fixedVariant: HeroVariantId,
): HeroVariantId {
  const fromUrl = readUrlHeroOverride();
  if (fromUrl) {
    persistVariant(fromUrl);
    return fromUrl;
  }

  if (abEnabled) {
    const sticky = readStickyVariant();
    if (sticky) return sticky;
    const picked = pickRandomHeroVariant();
    persistVariant(picked);
    return picked;
  }

  return fixedVariant;
}

/** @deprecated use resolveHeroVariantForSession */
export function assignHeroVariant(): HeroVariantId {
  const fromUrl = readUrlHeroOverride();
  if (fromUrl) {
    persistVariant(fromUrl);
    return fromUrl;
  }
  const sticky = readStickyVariant();
  if (sticky) return sticky;
  const picked = pickRandomHeroVariant();
  persistVariant(picked);
  return picked;
}

export function readAssignedHeroVariant(): HeroVariantId | null {
  const fromUrl = readUrlHeroOverride();
  if (fromUrl) return fromUrl;
  return readStickyVariant();
}
