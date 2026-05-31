"use client";
import { useLang } from "@/lib/LanguageContext";
import ProSubscribeButton from "@/components/ProSubscribeButton";
import ContactForm from "@/components/ContactForm";
import { MARKET_STATS } from "@/lib/marketStats";

type Tier = {
  name: string;
  price: string;
  period_es?: string;
  period_en?: string;
  f_es: string[];
  f_en: string[];
  cta_es: string;
  cta_en: string;
  dark?: boolean;
  featured?: boolean;
  href?: string;
  proNote_es?: string;
  proNote_en?: string;
};

const tiers: Tier[] = [
  {
    name: "Free",
    price: "$0",
    period_es: "sin costo",
    period_en: "no cost",
    f_es: [
      "1,000 consultas / día",
      "1 clave API (lectura)",
      `${MARKET_STATS.mcpTools} herramientas MCP`,
      "Búsqueda multi-retailer",
    ],
    f_en: [
      "1,000 requests / day",
      "1 API key (read-only)",
      `${MARKET_STATS.mcpTools} MCP tools`,
      "Multi-retailer search",
    ],
    cta_es: "Empezar",
    cta_en: "Get started",
    href: "https://pypi.org/project/cli-market/",
  },
  {
    name: "Pro",
    price: "$49",
    period_es: "/ mes",
    period_en: "/ month",
    f_es: [
      "10,000 consultas / día",
      "10 claves API (lectura y escritura)",
      "✦ Exportación de precios (JSON/CSV)",
      "Checkout (PayPal / QR) tras activación por email",
      "Soporte prioritario por email",
    ],
    f_en: [
      "10,000 requests / day",
      "10 API keys (read + write)",
      "✦ Price data export (JSON/CSV)",
      "Checkout (PayPal / QR) after email activation",
      "Priority email support",
    ],
    cta_es: "Obtener Pro",
    cta_en: "Get Pro",
    featured: true,
    proNote_es:
      "Para builders y agentes en producción. Facturación en soles con RUC 20613045563.",
    proNote_en:
      "For builders and agents in production. Invoicing in PEN with tax ID 20613045563.",
  },
  {
    name: "Enterprise",
    price: "A medida",
    period_es: "",
    period_en: "",
    f_es: [
      "Límites y SLAs personalizados",
      "Webhooks + endpoints dedicados",
      "Licencia de datos ampliada",
      "Soporte 24/7 + consultoría",
    ],
    f_en: [
      "Custom limits and SLAs",
      "Webhooks + dedicated endpoints",
      "Extended data license",
      "24/7 support + consulting",
    ],
    cta_es: "Contactar",
    cta_en: "Contact us",
    dark: true,
    href: "#contact-enterprise",
  },
];

function TierCard({
  tier,
  isES,
  children,
}: {
  tier: Tier;
  isES: boolean;
  children?: React.ReactNode;
}) {
  return (
    <div
      className={`rounded-2xl p-6 text-left flex flex-col relative ${
        tier.dark
          ? "energy-border-active card-cyber"
          : tier.featured
            ? "energy-border-active card-cyber"
            : "card-cyber"
      }`}
    >
      {tier.featured && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-xs font-semibold px-4 py-1 rounded-full whitespace-nowrap">
          {isES ? "Más popular" : "Most popular"}
        </span>
      )}
      <h3 className={`text-lg font-bold ${tier.dark ? "text-[var(--cm-mint)]" : "text-white"}`}>
        {tier.name}
      </h3>
      <div className="mt-3 mb-5">
        <span className="text-3xl font-black break-all tabular-nums text-white">
          {tier.price}
        </span>
        {(tier.period_es || tier.period_en) && (
          <span className="text-sm ml-1 text-[var(--cm-on-surface-variant)]">
            {isES ? tier.period_es : tier.period_en}
          </span>
        )}
      </div>
      <ul className="space-y-2.5 mb-6 flex-1">
        {(isES ? tier.f_es : tier.f_en).map((f, i) => {
          const isHighlight = f.startsWith("✦");
          return (
            <li
              key={i}
              className={`flex items-start gap-2.5 text-sm ${
                isHighlight
                  ? "font-semibold text-[var(--cm-mint)]"
                  : "text-[var(--cm-on-surface-variant)]"
              }`}
            >
              {!isHighlight && (
                <svg
                  className="w-4 h-4 mt-0.5 shrink-0"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="var(--cm-mint)"
                  strokeWidth="2.5"
                >
                  <path d="M20 6L9 17l-5-5" />
                </svg>
              )}
              {f}
            </li>
          );
        })}
      </ul>
      {children ? (
        children
      ) : tier.dark ? (
        <a
          href={tier.href ?? "#"}
          className="inline-flex items-center justify-center rounded-3xl border-2 border-[var(--cm-mint)] text-[var(--cm-mint)] text-sm font-semibold px-6 py-3 hover:bg-[var(--cm-mint)] hover:text-[var(--cm-on-mint)] transition-colors"
        >
          {isES ? tier.cta_es : tier.cta_en}
        </a>
      ) : (
        <a
          href={tier.href ?? "#"}
          className="btn-mint"
        >
          {isES ? tier.cta_es : tier.cta_en}
        </a>
      )}
    </div>
  );
}

export default function Pricing() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="pricing" className="landing-section-alt animate-fade-in">
      <div className="landing-container-wide text-center">
        <p className="section-eyebrow mb-4 text-[var(--cm-mint)]">
          {isES ? "Planes" : "Plans"}
        </p>
        <h2 className="section-title mb-2">
          {isES ? "Construido para escalar." : "Built to scale."}
        </h2>
        <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-xl mx-auto mb-12">
          {isES
            ? "Elige tu punto de entrada. Migra cuando crezcas sin cambiar de integración."
            : "Pick your entry point. Migrate as you grow without changing integrations."}
        </p>

        {/* Pricing cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto mb-12">
          {tiers.map((tier) => (
            <div key={tier.name}>
              <TierCard tier={tier} isES={isES}>
                {tier.name === "Pro" ? (
                  <div id="pro-checkout" className="scroll-mt-24">
                    <ProSubscribeButton />
                  </div>
                ) : tier.name === "Free" ? (
                  <a href={tier.href} className="btn-mint">
                    {isES ? tier.cta_es : tier.cta_en}
                  </a>
                ) : null}
              </TierCard>
              {tier.name === "Pro" && tier.proNote_es && (
                <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-2 text-center font-mono">
                  {isES ? tier.proNote_es : tier.proNote_en}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* Enterprise contact form */}
        <div id="contact-enterprise" className="scroll-mt-24 border-t border-[var(--cm-outline-variant)]/30 pt-12 max-w-2xl mx-auto">
          <ContactForm
            plan="enterprise"
            eyebrow={isES ? "Enterprise" : "Enterprise"}
            title={isES ? "¿Volumen Enterprise o SLAs a medida?" : "Enterprise volume or custom SLAs?"}
            subtitle={
              isES
                ? "Cuéntenos país, categorías y volumen. Respondemos en 48 h con propuesta."
                : "Tell us country, categories, and volume. We reply within 48 h with a proposal."
            }
          />
        </div>
      </div>
    </section>
  );
}
