import { PROCURE_LANDING_URL } from "./procurePlans";

export type NavItem = {
  id: string;
  es: string;
  en: string;
  href: string;
  external?: boolean;
};

/** Top nav — ICP hub (Build · Procure · Intelligence · Docs). */
export const TOP_NAV: NavItem[] = [
  { id: "build", es: "Build", en: "Build", href: "/build" },
  { id: "procure", es: "Procure", en: "Procure", href: PROCURE_LANDING_URL, external: true },
  { id: "intelligence", es: "Intelligence", en: "Intelligence", href: "/intelligence" },
  { id: "docs", es: "Docs", en: "Docs", href: "/docs" },
];

/** Homepage hub sections (SideNav removed on hub — kept for hash / active-section compat). */
export const HUB_SECTION_NAV: NavItem[] = [
  { id: "hero", es: "Inicio", en: "Home", href: "/#hero" },
  { id: "solution", es: "Solución", en: "Solution", href: "/#solution" },
  { id: "metrics", es: "Data moat", en: "Data moat", href: "/#metrics" },
];

/** @deprecated Hub no longer uses side rail — use HUB_SECTION_NAV if needed. */
export const SECTION_NAV: NavItem[] = HUB_SECTION_NAV;

/** @deprecated Hub no longer renders SideNav. */
export const SIDE_NAV: NavItem[] = HUB_SECTION_NAV;

/** Maps section anchor ids to TOP_NAV group (homepage scroll spy). */
export const TOP_NAV_GROUP: Record<string, string> = {
  hero: "build",
  solution: "build",
  metrics: "build",
};

export const BUILD_PAGE = "/build";
export const INTELLIGENCE_PAGE = "/intelligence";

/** Build pricing anchor on dedicated spoke. */
export const PRICING_BUILD_HASH = `${BUILD_PAGE}#pricing`;
/** Procure marketing + pricing on sister site. */
export const PRICING_PROCURE_HASH = PROCURE_LANDING_URL;
/** Retailer free listing — dedicated page. */
export const RETAILERS_PAGE = "/retailers";
/** @deprecated Use RETAILERS_PAGE */
export const PRICING_LISTED_HASH = RETAILERS_PAGE;
/** @deprecated Use RETAILERS_PAGE */
export const PRICING_RETAILERS_HASH = RETAILERS_PAGE;
