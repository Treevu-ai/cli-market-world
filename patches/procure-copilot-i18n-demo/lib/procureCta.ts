/** Procure Copilot — demo & sales CTAs (no mailto:). */

export const CLI_MARKET_CONTACT_PROCURE =
  "https://cli-market.dev/contact?topic=procure#contact-procure";

/** Self-serve trial checkout on cli-market.dev */
export const PROCURE_STARTER_CHECKOUT =
  "https://cli-market.dev/?audience=procure&plan=starter&checkout=open#pricing";

/** In-app dashboard (API key / magic link). */
export const PROCURE_DASHBOARD = "/dashboard";

/** Book a 15-min demo — web form, works without mail client. */
export function procureBookDemoHref(): string {
  return CLI_MARKET_CONTACT_PROCURE;
}

/** Try the product — dashboard with onboarding hint. */
export function procureTryDemoHref(): string {
  return `${PROCURE_DASHBOARD}?welcome=1`;
}

/** Enterprise / pilot sales — same contact form, enterprise topic. */
export function procureSalesHref(subject: string): string {
  const q = new URLSearchParams({ topic: "procure", subject });
  return `https://cli-market.dev/contact?${q.toString()}#contact-procure`;
}
