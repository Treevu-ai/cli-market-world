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
  anchor_es?: string;
  anchor_en?: string;
};

const buildTiers: Tier[] = [
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
      "Soporte prioritario por email",
    ],
    f_en: [
      "10,000 requests / day",
      "10 API keys (read + write)",
      "✦ Price data export (JSON/CSV)",
      "Priority email support",
    ],
    cta_es: "Obtener Pro",
    cta_en: "Get Pro",
    featured: true,
    proNote_es:
      "Para builders y agentes en producción. Checkout autónomo en roadmap — este trimestre el foco comercial es Intelligence.",
    proNote_en:
      "For builders and agents in production. Autonomous checkout is on the roadmap — this quarter we sell Intelligence.",
  },
];

const intelligenceTiers: Tier[] = [
  {
    name: "Intelligence Pilot",
    price: "$300–500",
    period_es: "/ mes",
    period_en: "/ month",
    f_es: [
      "✦ Spreads, inflación y canasta básica",
      "✦ Capa de calidad (clean / flagged / citable)",
      "✦ Series históricas y export CSV/JSON",
      "✦ API dedicada + onboarding en 48 h",
      "Piloto 30–90 días · Perú / LATAM",
    ],
    f_en: [
      "✦ Spreads, inflation, and basic basket",
      "✦ Quality layer (clean / flagged / citable)",
      "✦ Historical series and CSV/JSON export",
      "✦ Dedicated API + 48 h onboarding",
      "30–90 day pilot · Peru / LATAM",
    ],
    cta_es: "Solicitar piloto",
    cta_en: "Request pilot",
    featured: true,
    href: "#contact-intelligence",
    anchor_es:
      "Bureaus y herramientas legacy cobran USD 500+/mes por menos cobertura regional y sin filtros de calidad.",
    anchor_en:
      "Legacy bureaus and tools charge USD 500+/mo for less regional coverage and no quality filters.",
  },
  {
    name: "Enterprise",
    price: "A medida",
    period_en: "",
    period_es: "",
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
    href: "#contact-intelligence",
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
          {isES ? "Foco comercial" : "Commercial focus"}
        </span>
      )}
      <h3 className={`text-lg font-bold ${tier.dark ? "text-[var(--cm-mint)]" : "text-white"}`}>
        {tier.name}
      </h3>
      <div className="mt-3 mb-5">
        <span
          className={`text-3xl font-black break-all tabular-nums ${tier.dark ? "text-white" : "text-white"}`}
        >
          {tier.price}
        </span>
        {(tier.period_es || tier.period_en) && (
          <span className={`text-sm ml-1 ${tier.dark ? "text-[var(--cm-on-surface-variant)]" : "text-[var(--cm-on-surface-variant)]"}`}>
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
      {(tier.anchor_es || tier.anchor_en) && (
        <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed mb-4 border-t border-[var(--cm-outline-variant)]/30 pt-3">
          {isES ? tier.anchor_es : tier.anchor_en}
        </p>
      )}
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

        {/* Build Tiers */}
        <div id="pricing-build" className="scroll-mt-24 mb-16">
          <p className="font-label-caps text-[var(--cm-mint)] mb-6">
            {isES ? "Build · API y MCP" : "Build · API and MCP"}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
            {buildTiers.map((tier) => (
              <TierCard key={tier.name} tier={tier} isES={isES}>
                {tier.name === "Pro" ? (
                  <div id="pro-checkout" className="scroll-mt-24 space-y-3">
                    <ProSubscribeButton />
                    {tier.proNote_es && (
                      <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">
                        {isES ? tier.proNote_es : tier.proNote_en}
                      </p>
                    )}
                  </div>
                ) : (
                  <a
                    href={tier.href}
                    className="btn-mint"
                  >
                    {isES ? tier.cta_es : tier.cta_en}
                  </a>
                )}
              </TierCard>
            ))}
          </div>
          <p className="text-xs text-[var(--cm-on-surface-variant)] mt-6 max-w-2xl mx-auto">
            {isES
              ? "¿Builders buscando más escalabilidad? Pro elimina límites de exportación y da acceso a 10 API keys."
              : "Builders looking for more scale? Pro removes export limits and gives you 10 API keys."}
          </p>
        </div>

        {/* Intelligence Tiers */}
        <div id="pricing-intelligence" className="scroll-mt-24 mb-16">
          <p className="font-label-caps text-[var(--cm-mint)] mb-6">
            {isES ? "Intelligence · Datos comerciales" : "Intelligence · Commercial data"}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
            {intelligenceTiers.map((tier) => (
              <TierCard key={tier.name} tier={tier} isES={isES} />
            ))}
          </div>
          <p className="text-xs text-[var(--cm-on-surface-variant)] mt-4 max-w-2xl mx-auto">
            {isES ? (
              <>
                One-pager del piloto:{" "}
                <a href="/intelligence-pilot-es.md" className="underline hover:text-[var(--cm-mint)]">
                  intelligence-pilot-es.md
                </a>
              </>
            ) : (
              <>
                Pilot one-pager:{" "}
                <a href="/intelligence-pilot-es.md" className="underline hover:text-[var(--cm-mint)]">
                  intelligence-pilot-es.md
                </a>
              </>
            )}
          </p>
        </div>

        {/* Intelligence contact form */}
        <div id="contact-intelligence" className="scroll-mt-24 border-t border-[var(--cm-outline-variant)]/30 pt-12">
          <ContactForm
            plan="intelligence"
            eyebrow={isES ? "Intelligence" : "Intelligence"}
            title={isES ? "Solicitar piloto de Intelligence" : "Request Intelligence pilot"}
            subtitle={
              isES
                ? "Cuéntenos país, categorías y volumen. Respondemos en 48 h con propuesta de piloto. Puede adjuntar contexto o referirse al one-pager público."
                : "Tell us country, categories, and volume. We reply within 48 h with a pilot proposal. Attach context or refer to the public one-pager."
            }
          />
        </div>
      </div>
    </section>
  );
}
