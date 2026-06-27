import { PRICING_BUILD_HASH } from "@/lib/siteNav";
import { PROCURE_SITE_URL } from "@/lib/procurePlans";

export type Lang = "en" | "es";

export const CTA = {
  getApiKey: {
    en: "Get API Key →",
    es: "Obtener API Key →",
    href: "/docs#auth",
  },
  watchDemo: {
    en: "Quickstart →",
    es: "Quickstart →",
    href: "/docs",
  },
  bookProcureDemo: {
    en: "Book Procure Demo →",
    es: "Agendar demo Procure →",
    href: "/contact?topic=procure#contact-procure",
  },
  viewPlans: {
    en: "View plans →",
    es: "Ver planes →",
    href: PRICING_BUILD_HASH,
  },
  viewProcurePlans: {
    en: "See Procure plans →",
    es: "Ver planes Procure →",
    href: `${PROCURE_SITE_URL}/procure`,
  },
  signIn: {
    en: "Sign in",
    es: "Iniciar sesión",
    href: "/account",
  },
  signUp: {
    en: "Get API Key",
    es: "Obtener API Key",
    href: "/build",
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
