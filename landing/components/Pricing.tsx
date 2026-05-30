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
      className={`rounded-3xl p-6 text-left flex flex-col relative ${
        tier.dark
          ? "bg-[var(--wise-ink)] text-white"
          : tier.featured
            ? "bg-[var(--wise-canvas)] border-2 border-[var(--wise-ink)] shadow-lg"
            : "bg-[var(--wise-canvas)] border border-[var(--wise-green-pale)]"
      }`}
    >
      {tier.featured && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--wise-ink)] text-[var(--wise-canvas)] text-[11px] font-semibold px-4 py-1 rounded-full whitespace-nowrap">
          {isES ? "Foco comercial" : "Commercial focus"}
        </span>
      )}
      <h3 className={`text-lg font-bold ${tier.dark ? "text-[var(--wise-green)]" : "text-[var(--wise-ink)]"}`}>
        {tier.name}
      </h3>
      <div className="mt-3 mb-5">
        <span
          className={`text-3xl font-black break-all tabular-nums ${tier.dark ? "text-white" : "text-[var(--wise-ink)]"}`}
        >
          {tier.price}
        </span>
        {(tier.period_es || tier.period_en) && (
          <span className={`text-sm ml-1 ${tier.dark ? "text-white/80" : "text-[var(--wise-mute)]"}`}>
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
                  ? "font-semibold text-[var(--wise-ink)]"
                  : tier.dark
                    ? "text-white/80"
                    : "text-[var(--wise-body)]"
              }`}
            >
              {!isHighlight && (
                <svg
                  className="w-4 h-4 mt-0.5 shrink-0"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke={tier.dark ? "#9fe870" : "var(--wise-ink)"}
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
        <p className="text-[11px] text-[var(--wise-mute)] leading-relaxed mb-4 border-t border-[var(--wise-green-pale)] pt-3">
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
    <section id="pricing" className="relative bg-[var(--wise-canvas-soft)] py-16 border-t border-[#c5edab]">
      <div className="landing-container text-center">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-4">
          {isES ? "Planes" : "Plans"}
        </p>
        <h2 className="text-[clamp(22px,4vw,28px)] font-medium text-[var(--wise-ink)] mb-2 tracking-tight">
          {isES ? "Build gratis. Intelligence para equipos." : "Build free. Intelligence for teams."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-2xl mx-auto mb-12">
          {isES
            ? "Dos productos visibles: infraestructura para agentes (Build) y datos de precios con capa de calidad (Intelligence). Listado retailer sigue gratis en la sección de abajo."
            : "Two visible products: agent infrastructure (Build) and quality-filtered price data (Intelligence). Retailer listing stays free in the section below."}
        </p>

        {/* ── Build ── */}
        <div id="pricing-build" className="scroll-mt-24 mb-16 text-left">
          <div className="mb-6">
            <p className="text-[10px] font-mono uppercase tracking-[0.2em] text-[var(--wise-mute)] mb-1">
              {isES ? "Puerta A · Build" : "Door A · Build"}
            </p>
            <h3 className="text-xl font-bold text-[var(--wise-ink)]">
              {isES ? "API, MCP y CLI para builders" : "API, MCP, and CLI for builders"}
            </h3>
            <p className="text-sm text-[var(--wise-body)] mt-1 max-w-2xl">
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
                      <p className="text-[11px] text-[var(--wise-mute)] leading-relaxed">
                        {isES ? tier.proNote_es : tier.proNote_en}
                      </p>
                    )}
                  </div>
                ) : (
                  <a
                    href={tier.href}
                    className="inline-flex items-center justify-center rounded-3xl text-sm font-semibold px-6 py-3 transition-colors w-full bg-[var(--wise-ink)] text-[var(--wise-canvas)] hover:opacity-90"
                  >
                    {isES ? tier.cta_es : tier.cta_en}
                  </a>
                )}
              </TierCard>
            ))}
          </div>
        </div>

        {/* ── Intelligence ── */}
        <div id="pricing-intelligence" className="scroll-mt-24 mb-16 text-left">
          <div className="mb-6">
            <p className="text-[10px] font-mono uppercase tracking-[0.2em] text-[var(--wise-mute)] mb-1">
              {isES ? "Puerta C · Intelligence" : "Door C · Intelligence"}
            </p>
            <h3 className="text-xl font-bold text-[var(--wise-ink)]">
              {isES ? "Datos de precios para equipos comerciales" : "Price data for commercial teams"}
            </h3>
            <p className="text-sm text-[var(--wise-body)] mt-1 max-w-2xl">
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
                  className={`inline-flex items-center justify-center rounded-3xl text-sm font-semibold px-6 py-3 transition-colors w-full ${
                    tier.dark
                      ? "bg-white text-[var(--wise-ink)] hover:bg-[var(--wise-green-pale)]"
                      : "bg-[var(--wise-green)] text-[var(--wise-ink)] hover:bg-[var(--wise-green-hover)]"
                  }`}
                >
                  {isES ? tier.cta_es : tier.cta_en}
                </a>
              </TierCard>
            ))}
          </div>
          <p className="text-[11px] text-[var(--wise-mute)] mt-4 max-w-2xl mx-auto">
            {isES ? (
              <>
                One-pager del piloto:{" "}
                <a href="/intelligence-pilot-es.md" className="underline hover:text-[var(--wise-ink)]">
                  intelligence-pilot-es.md
                </a>
              </>
            ) : (
              <>
                Pilot one-pager:{" "}
                <a href="/intelligence-pilot-es.md" className="underline hover:text-[var(--wise-ink)]">
                  intelligence-pilot-es.md
                </a>
              </>
            )}
          </p>
        </div>

        <div className="rounded-2xl border border-[var(--wise-green-pale)] bg-[var(--wise-canvas)] p-4 max-w-3xl mx-auto mb-16 text-left">
          <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--wise-mute)] mb-2">
            {isES ? "¿Build Pro o Intelligence?" : "Build Pro or Intelligence?"}
          </p>
          <ul className="text-xs text-[var(--wise-body)] space-y-1.5">
            <li>
              <strong className="text-[var(--wise-ink)]">Pro (USD 49)</strong>
              {isES
                ? " — usted integra API/MCP y exporta datos técnicos. Ideal para devs y agentes."
                : " — you integrate API/MCP and export technical data. Best for devs and agents."}
            </li>
            <li>
              <strong className="text-[var(--wise-ink)]">Intelligence (USD 300–500)</strong>
              {isES
                ? " — paquete comercial: spreads, inflación, canasta, calidad y SLA. Ideal para pricing y trade."
                : " — commercial package: spreads, inflation, basket, quality, and SLA. Best for pricing and trade."}
            </li>
          </ul>
        </div>

        <div
          id="contact-intelligence"
          className="w-full max-w-lg mx-auto scroll-mt-24 min-w-0 border-t border-[#c5edab] pt-12"
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
