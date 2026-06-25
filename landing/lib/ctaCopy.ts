import { PRICING_BUILD_HASH, PRICING_PROCURE_HASH } from "@/lib/siteNav";

export type Lang = "en" | "es";

export const CTA = {
  getApiKey: {
    en: "Get API Key →",
    es: "Obtener API Key →",
    href: "/docs#auth",
  },
  watchDemo: {
    en: "Watch Demo →",
    es: "Ver Demo →",
    href: "https://procure-copilot.contacto-8e4.workers.dev/procure#demo",
  },
  bookDemo: {
    en: "Book Demo →",
    es: "Reservar Demo →",
    href: "/contact",
  },
  viewPlans: {
    en: "View plans →",
    es: "Ver planes →",
    href: PRICING_BUILD_HASH,
  },
  viewProcurePlans: {
    en: "See Procure plans →",
    es: "Ver planes Procure →",
    href: PRICING_PROCURE_HASH,
  },
  signIn: {
    en: "Sign in",
    es: "Iniciar sesión",
    href: "/account",
  },
  signUp: {
    en: "Get API Key",
    es: "Obtener API Key",
    href: PRICING_BUILD_HASH,
  },
  forRetailers: {
    en: "For retailers",
    es: "Para retailers",
    href: "/retailers",
  },
  contact: {
    en: "Contact",
    es: "Contacto",
    href: "/contact",
  },
} as const;

export function t(cta: keyof typeof CTA, lang: Lang): string {
  return CTA[cta][lang];
}
