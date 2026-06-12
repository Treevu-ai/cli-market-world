/** Checkout audience — Peru defaults to Mercado Pago (soles); international to PayPal (USD). */

export type ProCheckoutPaymentId = "paypal" | "soles";

const PE_TIMEZONES = new Set(["America/Lima"]);

let peAudienceCache: boolean | null = null;

export function isPeruCheckoutAudience(): boolean {
  if (typeof window === "undefined") return false;
  if (peAudienceCache !== null) return peAudienceCache;
  try {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (PE_TIMEZONES.has(tz)) {
      peAudienceCache = true;
      return true;
    }
    const lang = (navigator.language || "").toLowerCase();
    if (lang === "es-pe" || lang.endsWith("-pe")) {
      peAudienceCache = true;
      return true;
    }
  } catch {
    /* ignore */
  }
  peAudienceCache = false;
  return false;
}

export function defaultProPaymentMethod(): ProCheckoutPaymentId {
  return isPeruCheckoutAudience() ? "soles" : "paypal";
}

export function orderProPaymentOptions<T extends { id: ProCheckoutPaymentId }>(options: T[]): T[] {
  const prefer = defaultProPaymentMethod();
  return [...options].sort((a, b) => {
    if (a.id === prefer && b.id !== prefer) return -1;
    if (b.id === prefer && a.id !== prefer) return 1;
    return 0;
  });
}
