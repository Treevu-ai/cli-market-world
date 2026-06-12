/** Sinapsis Innovadora billing — USD (PayPal) vs soles (Yape · Plin · Mercado Pago). */

import { isPeruCheckoutAudience } from "@/lib/checkoutLocale";

export const SINAPSIS_BILLING = {
  entity: "Sinapsis Innovadora S.A.C.",
  taxId: "20613045563",
} as const;

export const PAYMENTS_PLACEHOLDER = "__PAYMENTS__";

const CHANNELS_INTL_ES = "PayPal (USD) · Yape · Plin · Mercado Pago (soles)";
const CHANNELS_INTL_EN = "PayPal (USD) · Yape · Plin · Mercado Pago (soles)";
const CHANNELS_PE_ES = "Mercado Pago (soles) · Yape · Plin · PayPal (USD)";
const CHANNELS_PE_EN = "Mercado Pago (soles) · Yape · Plin · PayPal (USD)";

function channelsOrdered(isES: boolean): string {
  if (isPeruCheckoutAudience()) {
    return isES ? CHANNELS_PE_ES : CHANNELS_PE_EN;
  }
  return isES ? CHANNELS_INTL_ES : CHANNELS_INTL_EN;
}

/** Short channel list — static default for SSR / JSON-LD; client hooks refresh order. */
export function paymentsChannelsShort(isES: boolean): string {
  return isES ? CHANNELS_INTL_ES : CHANNELS_INTL_EN;
}

/** Checkout modal + pricing cards — Peru lists soles first. */
export function paymentsChannelsForCheckout(isES: boolean): string {
  return channelsOrdered(isES);
}

export function formatPaymentsFeature(line: string, paymentsLabel: string): string {
  return line.includes(PAYMENTS_PLACEHOLDER)
    ? line.replace(PAYMENTS_PLACEHOLDER, paymentsLabel)
    : line;
}

/** Full billing policy for FAQ, pricing footnote, and docs. */
export function sinapsisBillingPolicy(isES: boolean): string {
  return isES
    ? `${SINAPSIS_BILLING.entity} (RUC ${SINAPSIS_BILLING.taxId}) factura suscripciones Build y Procure en dólares (USD) con PayPal y en soles (PEN) con Yape, Plin o tarjeta vía Mercado Pago. El comprobante se emite en la moneda del pago.`
    : `${SINAPSIS_BILLING.entity} (tax ID ${SINAPSIS_BILLING.taxId}) invoices Build and Procure subscriptions in US dollars (USD) via PayPal and in soles (PEN) via Yape, Plin, or card through Mercado Pago. Receipts match the payment currency.`;
}

/** One-line footnote under pricing cards. */
export function pricingBillingFootnote(isES: boolean): string {
  if (isPeruCheckoutAudience()) {
    return isES
      ? `${SINAPSIS_BILLING.entity} · RUC ${SINAPSIS_BILLING.taxId} · soles (Yape · Plin · Mercado Pago) o USD (PayPal).`
      : `${SINAPSIS_BILLING.entity} · tax ID ${SINAPSIS_BILLING.taxId} · soles (Yape · Plin · Mercado Pago) or USD (PayPal).`;
  }
  return isES
    ? `${SINAPSIS_BILLING.entity} · RUC ${SINAPSIS_BILLING.taxId} · USD (PayPal) o soles (Yape · Plin · Mercado Pago).`
    : `${SINAPSIS_BILLING.entity} · tax ID ${SINAPSIS_BILLING.taxId} · USD (PayPal) or soles (Yape · Plin · Mercado Pago).`;
}
