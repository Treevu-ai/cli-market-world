import { MARKET_STATS } from "@/lib/marketStats";
import { CTA } from "@/lib/ctaCopy";

export type SpokeIcp = "build" | "intelligence" | "retailers";

export type SpokeBrandMode = "terminal" | "operations";

export type SpokeCta = {
  es: string;
  en: string;
  href: string;
  external?: boolean;
};

export type SpokeHeroConfig = {
  eyebrow_es: string;
  eyebrow_en: string;
  titleBefore_es: string;
  titleAccent_es: string;
  titleAfter_es: string;
  titleBefore_en: string;
  titleAccent_en: string;
  titleAfter_en: string;
  subhead_es: string;
  subhead_en: string;
  chips: { label_es: string; label_en: string }[];
  primaryCta: SpokeCta;
  secondaryCta?: SpokeCta;
};

export type SpokeConfig = {
  id: SpokeIcp;
  brandMode: SpokeBrandMode;
  heroBackgroundDense: boolean;
  hero: SpokeHeroConfig;
};

export type SpokeFinalCtaConfig = {
  id: string;
  eyebrow_es: string;
  eyebrow_en: string;
  titleBefore_es: string;
  titleAccent_es: string;
  titleAfter_es: string;
  titleBefore_en: string;
  titleAccent_en: string;
  titleAfter_en: string;
  body_es: string;
  body_en: string;
  primaryCta: SpokeCta;
  secondaryCta?: SpokeCta;
};

export const SPOKE_FINAL_CTA: Record<SpokeIcp, SpokeFinalCtaConfig> = {
  build: {
    id: "build-final",
    eyebrow_es: "LISTO",
    eyebrow_en: "READY",
    titleBefore_es: "Conecta tu agente en ",
    titleAccent_es: "minutos",
    titleAfter_es: "",
    titleBefore_en: "Connect your agent in ",
    titleAccent_en: "minutes",
    titleAfter_en: "",
    body_es: "Instala el SDK, genera tu API key y corre el benchmark en tu terminal.",
    body_en: "Install the SDK, generate your API key, and run the benchmark in your terminal.",
    primaryCta: {
      es: "Empezar — CLI Market Pro",
      en: "Get started — CLI Market Pro",
      href: CTA.getApiKey.href,
    },
    secondaryCta: {
      es: "Ver planes →",
      en: "View plans →",
      href: "#pricing",
    },
  },
  intelligence: {
    id: "intelligence-final",
    eyebrow_es: "PILOTO",
    eyebrow_en: "PILOT",
    titleBefore_es: "Señales de retail ",
    titleAccent_es: "listas para tu equipo",
    titleAfter_es: "",
    titleBefore_en: "Retail signals ",
    titleAccent_en: "ready for your team",
    titleAfter_en: "",
    body_es: "Agenda una demo y recibe un one-pager con metodología y tiers de piloto.",
    body_en: "Book a demo and receive a one-pager with methodology and pilot tiers.",
    primaryCta: {
      es: "Solicitar piloto →",
      en: "Request pilot →",
      href: "/contact?topic=intelligence#contact-intelligence",
    },
    secondaryCta: {
      es: "One-pager Intelligence →",
      en: "Intelligence one-pager →",
      href: "/intelligence-pilot-es",
    },
  },
  retailers: {
    id: "retailers-final",
    eyebrow_es: "GRATIS",
    eyebrow_en: "FREE",
    titleBefore_es: "Indexa tu catálogo ",
    titleAccent_es: "hoy",
    titleAfter_es: "",
    titleBefore_en: "List your catalog ",
    titleAccent_en: "today",
    titleAfter_en: "",
    body_es: "Sin SDK ni integración técnica — solo tu catálogo donde compran los negocios.",
    body_en: "No SDK or technical integration — just your catalog where businesses buy.",
    primaryCta: {
      es: "Listar mi tienda — gratis",
      en: "List my store — free",
      href: "#retailer-apply",
    },
  },
};

export const SPOKE_CONFIG: Record<SpokeIcp, SpokeConfig> = {
  build: {
    id: "build",
    brandMode: "terminal",
    heroBackgroundDense: false,
    hero: {
      eyebrow_es: "CLI BUILD",
      eyebrow_en: "CLI BUILD",
      titleBefore_es: "Inteligencia de retail ",
      titleAccent_es: "programable",
      titleAfter_es: "",
      titleBefore_en: "Programmable ",
      titleAccent_en: "retail intelligence",
      titleAfter_en: "",
      subhead_es:
        "API, MCP y CLI sobre precios normalizados por kg/L — para agentes y productos con código.",
      subhead_en:
        "API, MCP, and CLI on kg/L-normalized prices — for agents and code-first products.",
      chips: [
        {
          label_es: "MCP · Cursor · Claude · VS Code",
          label_en: "MCP · Cursor · Claude · VS Code",
        },
        {
          label_es: `${MARKET_STATS.pricesVerifiedLabel} precios verificados`,
          label_en: `${MARKET_STATS.pricesVerifiedLabel} verified prices`,
        },
        { label_es: "Free · Starter $9 · Pro $49/mes", label_en: "Free · Starter $9 · Pro $49/mo" },
      ],
      primaryCta: {
        es: CTA.getApiKey.es,
        en: CTA.getApiKey.en,
        href: CTA.getApiKey.href,
      },
      secondaryCta: {
        es: CTA.watchDemo.es,
        en: CTA.watchDemo.en,
        href: CTA.watchDemo.href,
      },
    },
  },
  intelligence: {
    id: "intelligence",
    brandMode: "terminal",
    heroBackgroundDense: false,
    hero: {
      eyebrow_es: "INTELLIGENCE",
      eyebrow_en: "INTELLIGENCE",
      titleBefore_es: "Señales de retail ",
      titleAccent_es: "antes del IPC",
      titleAfter_es: "",
      titleBefore_en: "Retail signals ",
      titleAccent_en: "before CPI",
      titleAfter_en: "",
      subhead_es:
        "Para pricing, trade marketing, fintech y consultoras — spreads, inflación y canasta desde góndola real.",
      subhead_en:
        "For pricing, trade marketing, fintech, and consultancies — spreads, inflation, and basket from real shelf data.",
      chips: [
        { label_es: "Spreads multi-retailer", label_en: "Cross-retailer spreads" },
        { label_es: "Inflación 7 / 30 / 90 días", label_en: "Inflation 7 / 30 / 90 days" },
        { label_es: "Piloto desde $300/mes", label_en: "Pilot from $300/mo" },
      ],
      primaryCta: {
        es: "Solicitar piloto →",
        en: "Request pilot →",
        href: "/contact?topic=intelligence#contact-intelligence",
      },
      secondaryCta: {
        es: "One-pager Intelligence →",
        en: "Intelligence one-pager →",
        href: "/intelligence-pilot-es",
      },
    },
  },
  retailers: {
    id: "retailers",
    brandMode: "operations",
    heroBackgroundDense: true,
    hero: {
      eyebrow_es: "PARA RETAILERS",
      eyebrow_en: "FOR RETAILERS",
      titleBefore_es: "Tus productos, donde ",
      titleAccent_es: "compran los negocios",
      titleAfter_es: ".",
      titleBefore_en: "Your products, where ",
      titleAccent_en: "businesses buy",
      titleAfter_en: ".",
      subhead_es:
        "Compradores empresariales y agentes de IA comparan precios en CLI Market. Indexa tu catálogo gratis — sin SDK ni integración técnica.",
      subhead_en:
        "Business buyers and AI agents compare prices on CLI Market. List your catalog free — no SDK or technical integration.",
      chips: [
        { label_es: "Gratis para siempre", label_en: "Free forever" },
        { label_es: "Sin código", label_en: "No code" },
        {
          label_es: `${MARKET_STATS.retailersVerified} retailers indexados`,
          label_en: `${MARKET_STATS.retailersVerified} indexed retailers`,
        },
      ],
      primaryCta: {
        es: "Listar mi tienda — gratis",
        en: "List my store — free",
        href: "#retailer-apply",
      },
    },
  },
};
