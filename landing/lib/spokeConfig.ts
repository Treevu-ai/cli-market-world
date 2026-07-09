import { MARKET_STATS } from "@/lib/marketStats";
import { CTA } from "@/lib/ctaCopy";

export type SpokeIcp = "build" | "intelligence" | "retailers" | "cost-of-living";

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
  "cost-of-living": {
    id: "cost-of-living-final",
    eyebrow_es: "PRUEBA GRATIS",
    eyebrow_en: "FREE TRIAL",
    titleBefore_es: "Empieza a optimizar ",
    titleAccent_es: "tu canasta",
    titleAfter_es: " hoy",
    titleBefore_en: "Start optimizing ",
    titleAccent_en: "your basket",
    titleAfter_en: " today",
    body_es: "Prueba gratis 7 días de Starter — score de asequibilidad, sustitutos y canasta optimizada sin tarjeta.",
    body_en: "7-day free trial of Starter — affordability score, substitutes, and optimized basket with no credit card.",
    primaryCta: {
      es: "Empezar prueba gratis →",
      en: "Start free trial →",
      href: CTA.getApiKey.href,
    },
    secondaryCta: {
      es: "Ver planes →",
      en: "View plans →",
      href: "#cost-of-living-pricing",
    },
  },
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
    id: "retailer-apply",
    eyebrow_es: "GRATIS",
    eyebrow_en: "FREE",
    titleBefore_es: "¿Listo para ",
    titleAccent_es: "aparecer",
    titleAfter_es: "?",
    titleBefore_en: "Ready to get ",
    titleAccent_en: "listed",
    titleAfter_en: "?",
    body_es: "Completa el formulario en 2 minutos. Sin tarjeta de crédito. Sin equipo técnico.",
    body_en: "Fill out the form in 2 minutes. No credit card. No technical team.",
    primaryCta: {
      es: "Abrir formulario — gratis",
      en: "Open form — free",
      href: "#retailer-apply",
    },
    secondaryCta: {
      es: "hello@cli-market.dev",
      en: "hello@cli-market.dev",
      href: "mailto:hello@cli-market.dev?subject=CLI%20Market%20Retailer%20Listing",
    },
  },
};

export const SPOKE_CONFIG: Record<SpokeIcp, SpokeConfig> = {
  "cost-of-living": {
    id: "cost-of-living",
    brandMode: "terminal",
    heroBackgroundDense: false,
    hero: {
      eyebrow_es: "COST OF LIVING OS",
      eyebrow_en: "COST OF LIVING OS",
      titleBefore_es: "¿Cuánto cuesta ",
      titleAccent_es: "vivir en LATAM",
      titleAfter_es: "?",
      titleBefore_en: "What does it cost to ",
      titleAccent_en: "live in LATAM",
      titleAfter_en: "?",
      subhead_es:
        "Score de asequibilidad, canasta optimizada con TCO real y sustitutos inteligentes — desde precios verificados de góndola.",
      subhead_en:
        "Affordability score, optimized basket with real TCO, and smart substitutes — from verified shelf prices.",
      chips: [
        { label_es: "Affordability score en vivo", label_en: "Live affordability score" },
        { label_es: `${MARKET_STATS.pricesVerifiedLabel} precios verificados`, label_en: `${MARKET_STATS.pricesVerifiedLabel} verified prices` },
        { label_es: "Free · Starter $9 · Pro $49/mes", label_en: "Free · Starter $9 · Pro $49/mo" },
      ],
      primaryCta: {
        es: "Ver mi canasta →",
        en: "Optimize my basket →",
        href: CTA.getApiKey.href,
      },
      secondaryCta: {
        es: "market optimize leche:2 arroz:1kg",
        en: "market optimize milk:2 rice:1kg",
        href: "#cli-demo",
      },
    },
  },
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
