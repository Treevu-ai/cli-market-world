/** Procure Copilot — public marketing site (procurecopilot.com). */

export const PROCURE_SITE_URL =
  process.env.NEXT_PUBLIC_PROCURE_SITE_URL || "https://procurecopilot.com";

export const PROCURE_LANDING_URL = `${PROCURE_SITE_URL}/procure`;

export const PROCURE_APP_URL =
  process.env.NEXT_PUBLIC_PROCURE_APP_URL ||
  `${PROCURE_SITE_URL}/dashboard`;

/** Display names avoid collision with Build tiers (Starter / Pro). Slugs unchanged for API. */
export const PROCURE_PLANS = [
  {
    slug: "starter" as const,
    name: "Compare",
    price: 29,
    description_es: "Comparar precios y calcular ahorro — sin checkout.",
    description_en: "Compare prices and savings — no checkout.",
    features_es: [
      "20 procurement / mes",
      "Hasta 3 retailers por consulta",
      "Comparación multi-retailer · data-gate",
      "Dashboard Procure incluido",
      "API Build incluida (tier Starter)",
    ],
    features_en: [
      "20 procurements / mo",
      "Up to 3 retailers per query",
      "Multi-retailer compare · data-gate",
      "Procure dashboard included",
      "Build API included (Starter tier)",
    ],
    highlighted: false,
  },
  {
    slug: "pro" as const,
    name: "Ops",
    price: 79,
    description_es: "Aprobaciones, stock, delivery y pago integrado.",
    description_en: "Approvals, stock, delivery, and integrated checkout.",
    features_es: [
      "200 procurement / mes",
      "Flujo run → approve → checkout",
      "Aprobaciones gerente · audit trail",
      "PayPal (USD) · Mercado Pago (soles)",
      "API Build Pro incluida",
    ],
    features_en: [
      "200 procurements / mo",
      "run → approve → checkout flow",
      "Manager approvals · audit trail",
      "PayPal (USD) · Mercado Pago (soles)",
      "Build Pro API included",
    ],
    highlighted: true,
  },
  {
    slug: "builder" as const,
    name: "Scale",
    price: 149,
    description_es: "Multi-país y alto volumen.",
    description_en: "Multi-country and high volume.",
    features_es: [
      "1,000 procurement / mes",
      "Multi-país · integraciones custom",
      "SLA 99.5%",
      "Soporte prioritario",
      "API Build Pro incluida",
    ],
    features_en: [
      "1,000 procurements / mo",
      "Multi-country · custom integrations",
      "99.5% SLA",
      "Priority support",
      "Build Pro API included",
    ],
    highlighted: false,
  },
] as const;

export type ProcurePlanSlug = (typeof PROCURE_PLANS)[number]["slug"];

export const PROCURE_ENTRY_PRICE = PROCURE_PLANS[0].price;
export const PROCURE_RECOMMENDED_PRICE = PROCURE_PLANS.find((p) => p.highlighted)!.price;

/** Hero / page copy — entry Compare tier + recommended Ops tier. */
export function procurePriceRangeLabel(isES: boolean): string {
  return isES
    ? `Compare $${PROCURE_ENTRY_PRICE} · Ops $${PROCURE_RECOMMENDED_PRICE}/mes`
    : `Compare $${PROCURE_ENTRY_PRICE} · Ops $${PROCURE_RECOMMENDED_PRICE}/mo`;
}

export function procureEntryPriceLabel(isES: boolean): string {
  return isES
    ? `Desde $${PROCURE_ENTRY_PRICE} (Compare)`
    : `From $${PROCURE_ENTRY_PRICE} (Compare)`;
}
