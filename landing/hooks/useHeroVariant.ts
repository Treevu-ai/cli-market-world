"use client";

import { useEffect, useState } from "react";
import { readAssignedHeroVariant, resolveHeroVariantForSession } from "@/lib/heroVariantAssign";
import {
  FIXED_HERO_VARIANT,
  HERO_AB_ENABLED,
  type HeroVariantId,
  resolveHeroVariant,
} from "@/lib/heroVariants";

function initialVariant(): HeroVariantId {
  const assigned = readAssignedHeroVariant();
  if (assigned) return assigned;
  return HERO_AB_ENABLED ? "a" : FIXED_HERO_VARIANT;
}

export function useHeroVariant(): HeroVariantId {
  const [variant, setVariant] = useState<HeroVariantId>(initialVariant);

  useEffect(() => {
    setVariant(resolveHeroVariantForSession(HERO_AB_ENABLED, FIXED_HERO_VARIANT));
  }, []);

  return variant;
}

export function getStaticHeroVariant(): HeroVariantId {
  return HERO_AB_ENABLED ? "a" : FIXED_HERO_VARIANT;
}

export { HERO_AB_ENABLED, FIXED_HERO_VARIANT, resolveHeroVariant };
