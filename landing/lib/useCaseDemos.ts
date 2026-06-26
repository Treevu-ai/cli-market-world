import { MARKET_STATS } from "@/lib/marketStats";
import { PROCURE_SITE_URL } from "@/lib/procurePlans";

export type UseCaseId = "agents" | "market-data" | "basket" | "inflation" | "procure";

export type UseCaseDemo = {
  id: UseCaseId;
  icon: string;
  title_es: string;
  title_en: string;
  before_es: string;
  before_en: string;
  after_es: string;
  after_en: string;
  gif: string;
  alt_es: string;
  alt_en: string;
  ctaHref: string;
  cta_es: string;
  cta_en: string;
};

export const USE_CASE_DEMOS: UseCaseDemo[] = [
  {
    id: "agents",
    icon: "🤖",
    title_es: "Agentes de compra",
    title_en: "Shopping agents",
    before_es: "Scraping por retailer · parsers frágiles",
    before_en: "Per-retailer scraping · fragile parsers",
    after_es: `Una API + ${MARKET_STATS.mcpTools} API tools · canasta multi-cadena`,
    after_en: `One API + ${MARKET_STATS.mcpTools} API tools · multi-chain basket`,
    gif: "/use-cases/agents.gif",
    alt_es: "Demo: agente busca leche, agrega al carrito y expone API tools",
    alt_en: "Demo: agent searches milk, adds to cart, and exposes API tools",
    ctaHref: "/#pricing",
    cta_es: "Ver planes Build →",
    cta_en: "View Build plans →",
  },
  {
    id: "market-data",
    icon: "📊",
    title_es: "Datos de mercado",
    title_en: "Market data",
    before_es: "IPC y encuestas con semanas de retraso",
    before_en: "CPI and surveys weeks behind",
    after_es: "Índice de inflación y API bulk.",
    after_en: "Inflation index and bulk API.",
    gif: "/use-cases/market-data.gif",
    alt_es: "Demo: discover, stats y scores de cobertura de mercado",
    alt_en: "Demo: discover, stats, and market coverage scores",
    ctaHref: "/impact#coverage",
    cta_es: "Ver cobertura →",
    cta_en: "View coverage →",
  },
  {
    id: "basket",
    icon: "🧺",
    title_es: "Canasta multi-retailer",
    title_en: "Multi-retailer basket",
    before_es: "Comparar manualmente en 3+ apps",
    before_en: "Manual comparison across 3+ apps",
    after_es: "Un comando · mejor total por cadena",
    after_en: "One command · best total per chain",
    gif: "/use-cases/basket.gif",
    alt_es: "Demo: canasta multi-retailer con mejor total Metro",
    alt_en: "Demo: multi-retailer basket with best Metro total",
    ctaHref: "/docs#quickstart",
    cta_es: "Ver API →",
    cta_en: "View API →",
  },
  {
    id: "inflation",
    icon: "📈",
    title_es: "Inflación desde góndola",
    title_en: "Shelf-price inflation",
    before_es: "Estimaciones macro, no góndola",
    before_en: "Macro estimates, not shelf",
    after_es: "Tendencias desde góndola real.",
    after_en: "Trends from real shelf data.",
    gif: "/use-cases/inflation.gif",
    alt_es: "Demo: inflación desde góndola e intel brief",
    alt_en: "Demo: shelf inflation and intel brief",
    ctaHref: "/#intelligence",
    cta_es: "Ver Intelligence →",
    cta_en: "View Intelligence →",
  },
  {
    id: "procure",
    icon: "🛒",
    title_es: "Compras de empresa",
    title_en: "Enterprise procurement",
    before_es: "WhatsApp + Excel para aprobar compras",
    before_en: "WhatsApp + Excel to approve buys",
    after_es: "Procure Copilot · comparar y aprobar sin código",
    after_en: "Procure Copilot · compare and approve without code",
    gif: "/use-cases/procure.gif",
    alt_es: "Demo: Procure Copilot compara y aprueba orden",
    alt_en: "Demo: Procure Copilot compares and approves order",
    ctaHref: `${PROCURE_SITE_URL}/procure`,
    cta_es: "Ver Procure →",
    cta_en: "View Procure →",
  },
];

export function useCaseById(id: UseCaseId | null): UseCaseDemo | null {
  if (!id) return null;
  return USE_CASE_DEMOS.find((c) => c.id === id) ?? null;
}
