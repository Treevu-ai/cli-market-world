export type NavItem = {
  id: string;
  es: string;
  en: string;
};

/** Section anchors on the home page — order matches page.tsx (Navbar + SideNav + Footer). */
export const SECTION_NAV: NavItem[] = [
  { id: "casos", es: "Casos de uso", en: "Use cases" },
  { id: "coverage", es: "Cobertura", en: "Coverage" },
  { id: "how", es: "Cómo funciona", en: "How it works" },
  { id: "api", es: "API en vivo", en: "Live API" },
  { id: "intelligence", es: "Intelligence", en: "Intelligence" },
  { id: "pricing", es: "Planes", en: "Pricing" },
  { id: "faq", es: "FAQ", en: "FAQ" },
  { id: "contact", es: "Contacto", en: "Contact" },
];

/** Side rail includes hero home dot. Build · Procure · Listed live under #pricing. */
export const SIDE_NAV: NavItem[] = [{ id: "hero", es: "Inicio", en: "Home" }, ...SECTION_NAV];

/** Leading slash so pricing tabs work from any route (/docs, /stats, …). */
export const PRICING_BUILD_HASH = "/#pricing";
export const PRICING_PROCURE_HASH = "/#procure";
export const PRICING_LISTED_HASH = "/#listed";
/** Legacy alias — opens Listed tab */
export const PRICING_RETAILERS_HASH = "/#listed";