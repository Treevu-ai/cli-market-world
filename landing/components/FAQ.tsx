"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { paymentsChannelsShort, sinapsisBillingPolicy } from "@/lib/billingCopy";

function faqsFor(lang: "es" | "en") {
  const isES = lang === "es";
  const rp = isES ? MARKET_STATS.retailersPhraseEs : MARKET_STATS.retailersPhraseEn;
  const channels = paymentsChannelsShort(isES);
  const billingPolicy = sinapsisBillingPolicy(isES);

  if (isES) {
    return [
      {
        q: "¿Qué es CLI Market?",
        a: `CLI Market es infraestructura de comercio para agentes de IA y equipos comerciales: ${MARKET_STATS.pricesVerifiedLabel} precios de góndola normalizados por kg/L sobre ${rp}. Build (Free/Starter/Pro) para integrar API y MCP; Procure para compras con aprobaciones. Cero scraping.`,
      },
      {
        q: "¿Con qué retailers funciona?",
        a: `${MARKET_STATS.retailersDefined} retailers en catálogo, ${MARKET_STATS.retailersVerified} verificados activos, en ${MARKET_STATS.countries} países. 4 plataformas: VTEX (${MARKET_STATS.platformVtex}), Shopify (${MARKET_STATS.platformShopify} marcas moda/beauty) y Magento (${MARKET_STATS.platformMagento}).`,
      },
      {
        q: "¿Cómo funciona el pago y la facturación?",
        a: `${billingPolicy} Canales: ${channels}. La confirmación actualiza tu tier u orden automáticamente. Comprobante: hello@cli-market.dev.`,
      },
      {
        q: "¿Mis agentes pueden usar esto sin intervención humana?",
        a: `En gran parte. Las ${MARKET_STATS.mcpTools} herramientas MCP permiten que tu agente busque, compare y arme canastas de forma autónoma. El pago aún requiere aprobación humana, y el checkout autónomo está en roadmap.`,
      },
      {
        q: "¿Los precios son reales?",
        a: `Sí. Nuestro collector se actualiza cada ${MARKET_STATS.pricesRefreshHours} horas contra ${MARKET_STATS.retailersVerified} retailers verificados, obteniendo precios reales de góndola a través de las APIs públicas de catálogo de cada plataforma (VTEX, Shopify, Magento, WooCommerce), no por scraping de HTML. Más de ${MARKET_STATS.pricesVerifiedLabel} precios normalizados por kilo/litro, filtrados antes de publicar comparaciones.`,
      },
      {
        q: "¿Cuánto cuesta?",
        a: `Build (API/MCP): Free 1.000 consultas/día; Starter USD 24/mes (5.000/día); Pro USD 39/mes o USD 390/año (10.000/día, alertas, full MCP + checkout); Pro Founding USD 29/mes (100 plazas). Enterprise a medida. Procure (compras): Compare/Ops/Scale desde USD 29/mes — distinto de Build. Intelligence: lista de espera. Listado retailer: gratis.`,
      },
    ];
  }

  return [
    {
      q: "What is CLI Market?",
      a: `CLI Market is commerce infrastructure for AI agents and commercial teams: ${MARKET_STATS.pricesVerifiedLabel} shelf prices normalized per kg/L across ${rp}. Build (Free/Starter/Pro) for API and MCP; Procure for procurement with approvals. Zero scraping.`,
    },
    {
      q: "Which retailers do you support?",
      a: `${MARKET_STATS.retailersDefined} retailers in catalog, ${MARKET_STATS.retailersVerified} verified active, across ${MARKET_STATS.countries} countries. 4 platforms: VTEX (${MARKET_STATS.platformVtex}), Shopify (${MARKET_STATS.platformShopify} fashion/beauty brands), and Magento (${MARKET_STATS.platformMagento}).`,
    },
    {
      q: "How do payments and billing work?",
      a: `${billingPolicy} Channels: ${channels}. Confirmation updates your tier or order automatically. Receipts: hello@cli-market.dev.`,
    },
    {
      q: "Can my agents use this autonomously?",
      a: `Mostly. All ${MARKET_STATS.mcpTools} MCP tools let your agent search, compare, and build baskets autonomously. Payment still requires human approval, and autonomous checkout is on the roadmap.`,
    },
    {
      q: "Are the prices real?",
      a: `Yes. Our collector refreshes every ${MARKET_STATS.pricesRefreshHours} hours against ${MARKET_STATS.retailersVerified} verified retailers, fetching real shelf prices through each platform's public catalog APIs (VTEX, Shopify, Magento, WooCommerce), not HTML scraping. ${MARKET_STATS.pricesVerifiedLabel} prices normalized per kg/L, filtered before publishing comparisons.`,
    },
    {
      q: "How much does it cost?",
      a: `Build (API/MCP): Free 1,000 requests/day; Starter USD 24/mo (5,000/day); Pro USD 39/mo or USD 390/yr (10,000/day, alerts, full MCP + checkout); Pro Founding USD 29/mo (100 seats). Enterprise custom. Procure (procurement): Compare/Ops/Scale from USD 29/mo — separate from Build. Intelligence: waitlist. Retailer listing: free forever.`,
    },
  ];
}

export default function FAQ() {
  const { lang } = useLang();
  const faqs = faqsFor(lang);
  const isES = lang === "es";

  return (
    <section id="faq" className="landing-section animate-fade-in">
      <div className="landing-container-wide text-center max-w-3xl mx-auto">
        <p className="section-eyebrow mb-4">FAQ</p>
        <h2 className="section-title">
          {isES ? "Preguntas frecuentes." : "Frequently asked questions."}
        </h2>

        <div className="text-left mt-12 space-y-0">
          {faqs.map((faq, i) => (
            <details
              key={i}
              className="group border-b border-[var(--cm-outline-variant)]/30 py-1"
              {...(i === 0 ? { open: true } : {})}
            >
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-5 text-base font-medium text-white marker:content-none [&::-webkit-details-marker]:hidden">
                <span className="text-left">{faq.q}</span>
                <span
                  className="shrink-0 text-[var(--cm-mint)] text-lg leading-none transition-transform duration-200 group-open:rotate-45"
                  aria-hidden
                >
                  +
                </span>
              </summary>
              <p className="pb-5 text-base text-[var(--cm-on-surface-variant)] leading-relaxed">{faq.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
