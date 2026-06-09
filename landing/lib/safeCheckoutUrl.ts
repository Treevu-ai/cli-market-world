const CHECKOUT_HOST_SUFFIXES = [
  "paypal.com",
  "mercadopago.com",
  "mercadopago.com.pe",
  "mercadolibre.com",
  "mercadolibre.com.pe",
];

/** Allow only HTTPS checkout links from known payment providers. */
export function safeCheckoutRedirectUrl(raw: string | undefined): string | null {
  if (!raw?.trim()) return null;
  const trimmed = raw.trim();
  try {
    const u = new URL(trimmed);
    if (u.protocol !== "https:") return null;
    const host = u.hostname.toLowerCase();
    const allowed = CHECKOUT_HOST_SUFFIXES.some(
      (suffix) => host === suffix || host.endsWith(`.${suffix}`),
    );
    return allowed ? trimmed : null;
  } catch {
    return null;
  }
}

export function checkoutRedirectFromResult(data: {
  approve_url?: string;
  checkout_url?: string;
  payment_link?: string;
}): string | null {
  const raw = data.approve_url || data.checkout_url || data.payment_link;
  return safeCheckoutRedirectUrl(raw);
}