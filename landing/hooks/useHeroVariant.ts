"use client";

import { useEffect, useState } from "react";
import { assignHeroVariant, readAssignedHeroVariant } from "@/lib/heroVariantAssign";
import {
  FIXED_HERO_VARIANT,
  HERO_AB_ENABLED,
  type HeroVariantId,
  resolveHeroVariant,
} from "@/lib/heroVariants";

function initialVariant(): HeroVariantId {
  if (!HERO_AB_ENABLED) return FIXED_HERO_VARIANT;
  const assigned = readAssignedHeroVariant();
  if (assigned) return assigned;
  return FIXED_HERO_VARIANT;
}

export function useHeroVariant(): HeroVariantId {
  const [variant, setVariant] = useState<HeroVariantId>(initialVariant);

  useEffect(() => {
    if (!HERO_AB_ENABLED) {
      setVariant(FIXED_HERO_VARIANT);
      return;
    }
    setVariant(assignHeroVariant());
  }, []);

  return variant;
}

/** For SSR/static HTML default before inline script runs. */
export function getStaticHeroVariant(): HeroVariantId {
  return HERO_AB_ENABLED ? "a" : FIXED_HERO_VARIANT;
}

export { HERO_AB_ENABLED, FIXED_HERO_VARIANT, resolveHeroVariant };
