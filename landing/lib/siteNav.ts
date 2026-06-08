export type NavItem = {
  id: string;
  es: string;
  en: string;
};

/** Section anchors on the home page — single source for Navbar + SideNav. */
export const SECTION_NAV: NavItem[] = [
  { id: "how", es: "Flujo", en: "Flow" },
  { id: "api", es: "API", en: "API" },
  { id: "coverage", es: "Cobertura", en: "Coverage" },
  { id: "casos", es: "Casos", en: "Use cases" },
  { id: "intelligence", es: "Intelligence", en: "Intelligence" },
  { id: "pricing", es: "Planes", en: "Pricing" },
  { id: "faq", es: "FAQ", en: "FAQ" },
  { id: "contact", es: "Contacto", en: "Contact" },
];

/** Side rail includes hero home dot. Build · Procure · Listed live under #pricing. */
export const SIDE_NAV: NavItem[] = [{ id: "hero", es: "Inicio", en: "Home" }, ...SECTION_NAV];

export const PRICING_BUILD_HASH = "#pricing";
export const PRICING_PROCURE_HASH = "#procure";
export const PRICING_LISTED_HASH = "#listed";
/** Legacy alias — opens Listed tab */
export const PRICING_RETAILERS_HASH = "#listed";