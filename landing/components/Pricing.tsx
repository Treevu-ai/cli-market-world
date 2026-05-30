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
      className={`card-cyber header-strip p-6 text-left flex flex-col relative ${
        tier.featured ? "energy-border-active" : ""
      } ${tier.dark ? "bg-[var(--cm-surface-high)]" : ""}`}
    >
      {tier.featured && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-[11px] font-semibold px-4 py-1 rounded-full whitespace-nowrap font-mono uppercase tracking-wider">
          {isES ? "Foco comercial" : "Commercial focus"}
        </span>
      )}
      <h3 className={`text-lg font-bold ${tier.dark ? "text-[var(--cm-mint)]" : "text-white"}`}>
        {tier.name}
      </h3>
      <div className="mt-3 mb-5">
        <span className={`text-3xl font-black break-all tabular-nums ${tier.dark ? "text-white" : "text-[var(--cm-mint)]"}`}>
          {tier.price}
        </span>
        {(tier.period_es || tier.period_en) && (
          <span className={`text-sm ml-1 ${tier.dark ? "text-white/80" : "text-[var(--cm-on-surface-variant)]"}`}>
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
                  : tier.dark
                    ? "text-white/80"
                    : "text-[var(--cm-on-surface-variant)]"
              }`}
            >
              {!isHighlight && (
                <svg className="w-4 h-4 mt-0.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="#3afecf" strokeWidth="2.5">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
              )}
              {f}
            </li>
          );
        })}
      </ul>
      {(tier.anchor_es || tier.anchor_en) && (
        <p className="text-[11px] text-[var(--cm-on-surface-variant)]/70 leading-relaxed mb-4 border-t border-[var(--cm-outline-variant)]/30 pt-3">
          {isES ? tier.anchor_es : tier.anchor_en}
        </p>
      )}
      {children}
    </div>
  );
}

export default function Pricing() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="pricing" className="landing-section landing-section-alt">
      <div className="landing-container-wide text-center">
        <p className="section-eyebrow mb-4">{isES ? "Planes" : "Plans"}</p>
        <h2 className="section-title mb-2">
          {isES ? "Intelligence para equipos. Build gratis." : "Intelligence for teams. Build free."}
        </h2>
        <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-2xl mx-auto mb-12">
          {isES
            ? "Foco comercial este trimestre: datos de precios con capa de calidad (Puerta C). Build (Puerta A) para quien integra. Listado retailer (Puerta B) gratis — más abajo."
            : "Commercial focus this quarter: quality-filtered price data (Door C). Build (Door A) for integrators. Retailer listing (Door B) free — below."}
        </p>

        {/* ── Intelligence (foco comercial) ── */}
        <div id="pricing-intelligence" className="scroll-mt-24 mb-16 text-left">
          <div className="mb-6">
            <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-1">
              {isES ? "Puerta C · Intelligence" : "Door C · Intelligence"}
            </p>
            <h3 className="text-xl font-bold text-white">
              {isES ? "Datos de precios para equipos comerciales" : "Price data for commercial teams"}
            </h3>
            <p className="text-sm text-[var(--cm-on-surface-variant)] mt-1 max-w-2xl">
              {isES
                ? "Spreads, inflación, canasta y calidad verificable. Lo que vendemos este trimestre — no checkout autónomo."
                : "Spreads, inflation, basket, and verifiable quality. What we sell this quarter — not autonomous checkout."}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
            {intelligenceTiers.map((tier) => (
              <TierCard key={tier.name} tier={tier} isES={isES}>
                <a
                  href={tier.href || "#contact-intelligence"}
                  className={`inline-flex items-center justify-center text-sm font-semibold px-6 py-3 transition-colors w-full font-mono uppercase tracking-wider text-[11px] ${
                    tier.dark
                      ? "bg-white text-[var(--cm-on-mint)] hover:bg-[var(--cm-mint)]"
                      : "btn-mint"
                  }`}
                >
                  {isES ? tier.cta_es : tier.cta_en}
                </a>
              </TierCard>
            ))}
          </div>
          <p className="text-[11px] text-[var(--cm-on-surface-variant)]/70 mt-4 max-w-2xl mx-auto">
            {isES ? (
              <>
                One-pager del piloto:{" "}
                <a href="/intelligence-pilot-es.md" className="text-[var(--cm-mint)] underline hover:brightness-110">
                  intelligence-pilot-es.md
                </a>
              </>
            ) : (
              <>
                Pilot one-pager:{" "}
                <a href="/intelligence-pilot-es.md" className="text-[var(--cm-mint)] underline hover:brightness-110">
                  intelligence-pilot-es.md
                </a>
              </>
            )}
          </p>
        </div>

        {/* ── Build ── */}
        <div id="pricing-build" className="scroll-mt-24 mb-16 text-left">
          <div className="mb-6">
            <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-1">
              {isES ? "Puerta A · Build" : "Door A · Build"}
            </p>
            <h3 className="text-xl font-bold text-white">
              {isES ? "API, MCP y CLI para builders" : "API, MCP, and CLI for builders"}
            </h3>
            <p className="text-sm text-[var(--cm-on-surface-variant)] mt-1 max-w-2xl">
              {isES
                ? "Integre agentes, automatice búsquedas y exporte datos. Sin tarjeta para Free."
                : "Integrate agents, automate search, and export data. No card for Free."}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
            {buildTiers.map((tier) => (
              <TierCard key={tier.name} tier={tier} isES={isES}>
                {tier.name === "Pro" ? (
                  <div id="pro-checkout" className="scroll-mt-24 space-y-3">
                    <ProSubscribeButton />
                    {tier.proNote_es && (
                      <p className="text-[11px] text-[var(--cm-on-surface-variant)]/70 leading-relaxed">
                        {isES ? tier.proNote_es : tier.proNote_en}
                      </p>
                    )}
                  </div>
                ) : (
                  <a
                    href={tier.href}
                    className="inline-flex items-center justify-center text-sm font-semibold px-6 py-3 transition-colors w-full bg-[var(--cm-surface-high)] text-white border border-[var(--cm-outline-variant)] hover:border-[var(--cm-mint)]/50 font-mono uppercase tracking-wider text-[11px]"
                  >
                    {isES ? tier.cta_es : tier.cta_en}
                  </a>
                )}
              </TierCard>
            ))}
          </div>
        </div>

        <div className="card-cyber p-4 max-w-3xl mx-auto mb-16 text-left">
          <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-2">
            {isES ? "¿Build Pro o Intelligence?" : "Build Pro or Intelligence?"}
          </p>
          <ul className="text-xs text-[var(--cm-on-surface-variant)] space-y-1.5">
            <li>
              <strong className="text-white">Pro (USD 49)</strong>
              {isES
                ? " — usted integra API/MCP y exporta datos técnicos. Ideal para devs y agentes."
                : " — you integrate API/MCP and export technical data. Best for devs and agents."}
            </li>
            <li>
              <strong className="text-white">Intelligence (USD 300–500)</strong>
              {isES
                ? " — paquete comercial: spreads, inflación, canasta, calidad y SLA. Ideal para pricing y trade."
                : " — commercial package: spreads, inflation, basket, quality, and SLA. Best for pricing and trade."}
            </li>
          </ul>
        </div>

        <div
          id="contact-intelligence"
          className="w-full max-w-lg mx-auto scroll-mt-24 min-w-0 border-t border-[var(--cm-outline-variant)]/30 pt-12"
        >
          <ContactForm
            plan="intelligence"
            eyebrow={isES ? "Intelligence · Piloto" : "Intelligence · Pilot"}
            title={
              isES
                ? "¿Pricing, trade marketing o inteligencia comercial?"
                : "Pricing, trade marketing, or commercial intelligence?"
            }
            subtitle={
              isES
                ? "Cuéntenos país, categorías y volumen. Respondemos en 48 h con propuesta de piloto. Puede adjuntar contexto o referirse al one-pager público."
                : "Tell us country, categories, and volume. We reply within 48 h with a pilot proposal. Attach context or refer to the public one-pager."
            }
            placeholder={
              isES
                ? "Ej.: spreads supermercados PE, 90 días histórico, equipo de pricing..."
                : "E.g. grocery spreads Peru, 90-day history, pricing team..."
            }
          />
        </div>
      </div>
    </section>
  );
}
