/** Sinapsis Innovadora billing — USD (PayPal) vs soles (Yape · Plin · Mercado Pago). */

import { isPeruCheckoutAudience } from "@/lib/checkoutLocale";

export const SINAPSIS_BILLING = {
  entity: "Sinapsis Innovadora S.A.C.",
  taxId: "20613045563",
} as const;

/** Short channel list for cards and inline copy. */
export function paymentsChannelsShort(isES: boolean): string {
  return isES
    ? "PayPal (USD) · Yape · Plin · Mercado Pago (soles)"
    : "PayPal (USD) · Yape · Plin · Mercado Pago (soles)";
}

/** Checkout modal — Peru audience lists soles first; international lists PayPal first. */
export function paymentsChannelsForCheckout(isES: boolean): string {
  if (isPeruCheckoutAudience()) {
    return isES
      ? "Mercado Pago (soles) · Yape · Plin · PayPal (USD)"
      : "Mercado Pago (soles) · Yape · Plin · PayPal (USD)";
  }
  return isES
    ? "PayPal (USD) · Mercado Pago (soles) · Yape · Plin"
    : "PayPal (USD) · Mercado Pago (soles) · Yape · Plin";
}

/** Full billing policy for FAQ, pricing footnote, and docs. */
export function sinapsisBillingPolicy(isES: boolean): string {
  return isES
    ? `${SINAPSIS_BILLING.entity} (RUC ${SINAPSIS_BILLING.taxId}) factura suscripciones Build y Procure en dólares (USD) con PayPal y en soles (PEN) con Yape, Plin o tarjeta vía Mercado Pago. El comprobante se emite en la moneda del pago.`
    : `${SINAPSIS_BILLING.entity} (tax ID ${SINAPSIS_BILLING.taxId}) invoices Build and Procure subscriptions in US dollars (USD) via PayPal and in soles (PEN) via Yape, Plin, or card through Mercado Pago. Receipts match the payment currency.`;
}

/** One-line footnote under pricing cards. */
export function pricingBillingFootnote(isES: boolean): string {
  return isES
    ? `${SINAPSIS_BILLING.entity} · RUC ${SINAPSIS_BILLING.taxId} · USD (PayPal) o soles (Yape · Plin · Mercado Pago).`
    : `${SINAPSIS_BILLING.entity} · tax ID ${SINAPSIS_BILLING.taxId} · USD (PayPal) or soles (Yape · Plin · Mercado Pago).`;
}
