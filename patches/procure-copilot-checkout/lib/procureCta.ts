/** Procure Copilot — subscribe CTAs (on-site checkout Phase 2). */

export const CLI_MARKET_CONTACT_PROCURE =
  "https://cli-market.dev/contact?topic=procure#contact-procure";

export const PROCURE_DASHBOARD = "/dashboard";

export function buildProcureSubscribeHref(plan: "starter" | "pro" | "builder"): string {
  return `/procure/subscribe?plan=${plan}&checkout=open`;
}

export const PROCURE_STARTER_CHECKOUT = buildProcureSubscribeHref("starter");
export const PROCURE_PRO_CHECKOUT = buildProcureSubscribeHref("pro");
export const PROCURE_BUILDER_CHECKOUT = buildProcureSubscribeHref("builder");

export function procureBookDemoHref(): string {
  return CLI_MARKET_CONTACT_PROCURE;
}

export function procureTryDemoHref(): string {
  return `${PROCURE_DASHBOARD}?welcome=1`;
}

export function procureSalesHref(subject: string): string {
  const q = new URLSearchParams({ topic: "procure", subject });
  return `https://cli-market.dev/contact?${q.toString()}#contact-procure`;
}
