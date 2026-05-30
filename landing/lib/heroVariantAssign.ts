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

function readUrlOverride(): HeroVariantId | null {
  if (typeof window === "undefined") return null;
  const v = new URLSearchParams(window.location.search).get("hero");
  return v ? resolveHeroVariant(v) : null;
}

/** Assign or read sticky variant (URL ?hero= > cookie > random). */
export function assignHeroVariant(): HeroVariantId {
  const fromUrl = readUrlOverride();
  if (fromUrl) {
    writeCookie(HERO_VARIANT_COOKIE, fromUrl);
    if (typeof document !== "undefined") {
      document.documentElement.dataset.heroVariant = fromUrl;
    }
    return fromUrl;
  }

  const fromCookie = readCookie(HERO_VARIANT_COOKIE);
  if (fromCookie && HERO_VARIANT_IDS.includes(fromCookie as HeroVariantId)) {
    const v = fromCookie as HeroVariantId;
    if (typeof document !== "undefined") {
      document.documentElement.dataset.heroVariant = v;
    }
    return v;
  }

  const picked = pickRandomHeroVariant();
  writeCookie(HERO_VARIANT_COOKIE, picked);
  if (typeof document !== "undefined") {
    document.documentElement.dataset.heroVariant = picked;
  }
  return picked;
}

export function readAssignedHeroVariant(): HeroVariantId | null {
  if (typeof document === "undefined") return null;
  const fromDom = document.documentElement.dataset.heroVariant;
  if (fromDom) return resolveHeroVariant(fromDom);
  const fromCookie = readCookie(HERO_VARIANT_COOKIE);
  if (fromCookie && HERO_VARIANT_IDS.includes(fromCookie as HeroVariantId)) {
    return fromCookie as HeroVariantId;
  }
  return null;
}
