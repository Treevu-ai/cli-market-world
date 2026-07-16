/**
 * Canonical Build (API) tier limits for landing copy.
 * Source of truth: cli-market-core/market_core/market_billing.py (TIERS,
 * TRIAL_DAYS). No free plan — Starter starts with a time-limited trial
 * instead (see TRIAL_DAYS below, and db_set_subscription(..., "starter",
 * expires_days=TRIAL_DAYS) in cli-market-backend's registration flow).
 */

export type ReqPeriod = "day" | "month";

export type BuildTierId = "starter" | "pro" | "enterprise";

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

export const TRIAL_DAYS = 7;

export const BUILD_TIER_STARTER: BuildTierSpec = {
  id: "starter",
  name: "Starter",
  priceUsd: 9,
  latamPricePen: "S/35",
  trialDays: TRIAL_DAYS,
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

export function formatTrialHeroChip(isES: boolean): string {
  return isES
    ? `Prueba gratis ${TRIAL_DAYS} días · sin tarjeta`
    : `${TRIAL_DAYS}-day free trial · no card`;
}

export function formatTierPriceLine(tier: BuildTierSpec, isES: boolean): string {
  const req = formatReqLimit(tier.reqLimit, isES, "short");
  if (tier.trialDays) {
    return isES
      ? `USD ${tier.priceUsd}/mes · ${req} · ${tier.trialDays} días gratis`
      : `USD ${tier.priceUsd}/mo · ${req} · ${tier.trialDays}-day trial`;
  }
  return `USD ${tier.priceUsd}/mo · ${req}`;
}

export function formatFaqPricingSummary(isES: boolean): string {
  const starter = formatReqLimit(BUILD_TIER_STARTER.reqLimit, isES, "short");
  const pro = formatReqLimit(BUILD_TIER_PRO.reqLimit, isES, "short");
  if (isES) {
    return `Build (API): Starter USD 9/mes (${starter}, export CSV, prueba gratis de ${TRIAL_DAYS} días); Pro USD 49/mes o USD 490/año (${pro}, alertas, API completa + checkout). Enterprise a medida. Procure (compras): Compare/Ops/Scale desde USD 29/mes — distinto de Build. Advisors: lista de espera. Listado retailer: gratis.`;
  }
  return `Build (API): Starter USD 9/mo (${starter}, CSV export, ${TRIAL_DAYS}-day free trial); Pro USD 49/mo or USD 490/yr (${pro}, alerts, full API + checkout). Enterprise custom. Procure (procurement): Compare/Ops/Scale from USD 29/mo — separate from Build. Advisors: waitlist. Retailer listing: free forever.`;
}

export function formatTrialApiKeyBlurb(isES: boolean): string {
  const req = formatReqLimit(BUILD_TIER_STARTER.reqLimit, isES, "long");
  if (isES) {
    return `pip install cli-market-world → market login → se genera tu key automáticamente. Empezás con ${TRIAL_DAYS} días gratis del plan Starter: ${req}, sin tarjeta de crédito. Tu key también activa el endpoint API remoto (claude.ai, ChatGPT, Cursor) y la CLI local.`;
  }
  return `pip install cli-market-world → market login → your key is generated automatically. You start with a ${TRIAL_DAYS}-day free trial of the Starter plan: ${req}, no credit card. Your key also activates the remote API endpoint (claude.ai, ChatGPT, Cursor) and the local CLI.`;
}