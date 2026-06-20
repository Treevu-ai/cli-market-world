/**
 * Canonical Build (API) tier limits for landing copy.
 * Source of truth: docs/pricing-strategy.md · server RATE_LIMIT_DAY=1000.
 */

export type ReqPeriod = "day" | "month";

export type BuildTierId = "free" | "starter" | "pro" | "enterprise";

export type BuildTierSpec = {
  id: BuildTierId;
  name: string;
  priceUsd: number | null;
  latamPricePen?: string;
  annualPriceUsd?: number;
  annualLatamPricePen?: string;
  trialDays?: number;
  reqLimit: { amount: number; period: ReqPeriod };
  apiKeys: number;
  features_es: string[];
  features_en: string[];
};

export const BUILD_TIER_FREE: BuildTierSpec = {
  id: "free",
  name: "Free",
  priceUsd: 0,
  reqLimit: { amount: 1_000, period: "day" },
  apiKeys: 1,
  features_es: [
    "1.000 consultas / día",
    "1 asiento · API key",
    "API + CLI · datos reales",
    "Compare · basket · búsqueda",
    "Historial 7 días",
  ],
  features_en: [
    "1,000 requests / day",
    "1 seat · API key",
    "API + CLI · real data",
    "Compare · basket · search",
    "7-day history",
  ],
};

export const BUILD_TIER_STARTER: BuildTierSpec = {
  id: "starter",
  name: "Starter",
  priceUsd: 9,
  latamPricePen: "S/35",
  trialDays: 14,
  reqLimit: { amount: 5_000, period: "day" },
  apiKeys: 1,
  features_es: [
    "5.000 consultas / día",
    "1 asiento · API key",
    "API + CLI · datos reales",
    "Basket básico · compare · export CSV",
    "Historial 7 días",
  ],
  features_en: [
    "5,000 requests / day",
    "1 seat · API key",
    "API + CLI · real data",
    "Basic basket · compare · CSV export",
    "7-day history",
  ],
};

export const BUILD_TIER_PRO: BuildTierSpec = {
  id: "pro",
  name: "Pro",
  priceUsd: 49,
  latamPricePen: "S/179",
  annualPriceUsd: 490,
  annualLatamPricePen: "S/1,790",
  reqLimit: { amount: 10_000, period: "day" },
  apiKeys: 10,
  features_es: [
    "10.000 consultas / día",
    "3 asientos · 10 API keys",
    "Checkout retail · PayPal · Yape · Plin · Mercado Pago",
    "Alertas · historial 12 meses",
    "Export CSV · basket optimization",
  ],
  features_en: [
    "10,000 requests / day",
    "3 seats · 10 API keys",
    "Retail checkout · PayPal · Yape · Plin · Mercado Pago",
    "Alerts · 12-month history",
    "CSV export · basket optimization",
  ],
};

export const BUILD_TIERS: BuildTierSpec[] = [
  BUILD_TIER_FREE,
  BUILD_TIER_STARTER,
  BUILD_TIER_PRO,
];

export function formatReqLimit(
  limit: BuildTierSpec["reqLimit"],
  isES: boolean,
  style: "short" | "long" = "long",
): string {
  const n = limit.amount.toLocaleString(isES ? "es-PE" : "en-US");
  if (style === "short") {
    return isES
      ? limit.period === "day"
        ? `${n}/día`
        : `${n}/mes`
      : limit.period === "day"
        ? `${n}/day`
        : `${n}/mo`;
  }
  return isES
    ? limit.period === "day"
      ? `${n} consultas / día`
      : `${n} consultas / mes`
    : limit.period === "day"
      ? `${n} requests / day`
      : `${n} requests / month`;
}

export function formatFreeHeroChip(isES: boolean): string {
  return isES ? "1.000 consultas/día · sin tarjeta" : "1,000 req/day · no card";
}

export function formatTierPriceLine(tier: BuildTierSpec, isES: boolean): string {
  if (tier.priceUsd === 0) {
    return isES ? "Gratis · sin tarjeta" : "Free · no card";
  }
  const req = formatReqLimit(tier.reqLimit, isES, "short");
  return `USD ${tier.priceUsd}/mo · ${req}`;
}

export function formatFaqPricingSummary(isES: boolean): string {
  const free = formatReqLimit(BUILD_TIER_FREE.reqLimit, isES, "short");
  const starter = formatReqLimit(BUILD_TIER_STARTER.reqLimit, isES, "short");
  const pro = formatReqLimit(BUILD_TIER_PRO.reqLimit, isES, "short");
  if (isES) {
    return `Build (API): Free USD 0 (${free}); Starter USD 9/mes (${starter}, export CSV); Pro USD 49/mes o USD 490/año (${pro}, alertas, API completa + checkout). Enterprise a medida. Procure (compras): Compare/Ops/Scale desde USD 29/mes — distinto de Build. Intelligence: lista de espera. Listado retailer: gratis.`;
  }
  return `Build (API): Free USD 0 (${free}); Starter USD 9/mo (${starter}, CSV export); Pro USD 49/mo or USD 490/yr (${pro}, alerts, full API + checkout). Enterprise custom. Procure (procurement): Compare/Ops/Scale from USD 29/mo — separate from Build. Intelligence: waitlist. Retailer listing: free forever.`;
}

export function formatFreeApiKeyBlurb(isES: boolean): string {
  const req = formatReqLimit(BUILD_TIER_FREE.reqLimit, isES, "long");
  if (isES) {
    return `pip install cli-market-world → market login → se genera tu key automáticamente. El tier Free incluye ${req} sin tarjeta de crédito. Tu key también activa el endpoint API remoto (claude.ai, ChatGPT, Cursor) y la CLI local.`;
  }
  return `pip install cli-market-world → market login → your key is generated automatically. The Free tier includes ${req} with no credit card. Your key also activates the remote API endpoint (claude.ai, ChatGPT, Cursor) and the local CLI.`;
}