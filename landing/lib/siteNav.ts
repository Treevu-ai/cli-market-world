export type NavItem = {
  id: string;
  es: string;
  en: string;
  href: string;
};

/** Top nav — clean, 4 items. */
export const TOP_NAV: NavItem[] = [
  { id: "product", es: "Producto", en: "Product", href: "/#hero" },
  { id: "procure", es: "Procure", en: "Procure", href: "/#procure" },
  { id: "pricing", es: "Planes", en: "Pricing", href: "/#pricing" },
  { id: "docs", es: "Docs", en: "Docs", href: "/docs" },
];

/** Homepage sections (SideNav dots) — matches actual section IDs in page.tsx. */
export const SECTION_NAV: NavItem[] = [
  { id: "hero", es: "Inicio", en: "Home", href: "/#hero" },
  { id: "problem", es: "Problema", en: "Problem", href: "/#problem" },
  { id: "solution", es: "Solución", en: "Solution", href: "/#solution" },
  { id: "architecture", es: "Stack", en: "Stack", href: "/#architecture" },
  { id: "pricing", es: "Planes", en: "Pricing", href: "/#pricing" },
  { id: "faq", es: "FAQ", en: "FAQ", href: "/#faq" },
];

/** Side rail homepage dots. */
export const SIDE_NAV: NavItem[] = SECTION_NAV;

/** Maps every SECTION_NAV anchor id to the TOP_NAV group it belongs to. */
export const TOP_NAV_GROUP: Record<string, string> = {
  hero: "product",
  problem: "product",
  "why-now": "product",
  solution: "product",
  architecture: "product",
  "who-its-for": "product",
  moat: "product",
  metrics: "product",
  procure: "procure",
  pricing: "pricing",
  faq: "pricing",
};

/** Leading slash so tabs work from any route. */
export const PRICING_BUILD_HASH = "/#pricing";
export const PRICING_PROCURE_HASH = "/#procure";
/** Retailer free listing — dedicated page. */
export const RETAILERS_PAGE = "/retailers";
/** @deprecated Use RETAILERS_PAGE */
export const PRICING_LISTED_HASH = RETAILERS_PAGE;
/** @deprecated Use RETAILERS_PAGE */
export const PRICING_RETAILERS_HASH = RETAILERS_PAGE;
