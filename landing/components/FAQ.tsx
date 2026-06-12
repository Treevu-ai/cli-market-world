"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { sinapsisBillingPolicy } from "@/lib/billingCopy";
import { usePaymentsChannels } from "@/lib/useBillingCopy";

function faqsFor(lang: "es" | "en", channels: string) {
  const isES = lang === "es";
  const rp = isES ? MARKET_STATS.retailersPhraseEs : MARKET_STATS.retailersPhraseEn;
  const billingPolicy = sinapsisBillingPolicy(isES);

  if (isES) {
    return [
      {
        q: "¿Qué es CLI Market?",
        a: `CLI Market es infraestructura de comercio para agentes de IA y equipos comerciales: ${MARKET_STATS.pricesVerifiedLabel} precios de góndola normalizados por kg/L sobre ${rp}. Build (Free/Starter/Pro) para integrar API y MCP; Procure para compras con aprobaciones. Cero scraping.`,
      },
      {
        q: "¿Con qué retailers funciona?",
        a: `${MARKET_STATS.retailersDefined} retailers en catálogo, ${MARKET_STATS.retailersVerified} verificados activos, en ${MARKET_STATS.countries} países. 4 plataformas: VTEX (${MARKET_STATS.platformVtex}), Shopify (${MARKET_STATS.platformShopify} marcas moda/beauty), Magento (${MARKET_STATS.platformMagento}) y WooCommerce (${MARKET_STATS.platformWooCommerce} piloto FMCG).`,
      },
      {
        q: "¿Cómo funciona el pago y la facturación?",
        a: `${billingPolicy} Canales: ${channels}. La confirmación actualiza tu tier u orden automáticamente. Comprobante: hello@cli-market.dev.`,
      },
      {
        q: "¿El agente compra en el supermercado?",
        a: `No directamente en el sitio del retailer. CLI Market unifica búsqueda y comparación en ${MARKET_STATS.retailersVerified} tiendas; checkout Pro crea una orden interna y cobra con Yape/Plin/PayPal (LATAM). No ejecuta el checkout de Wong, Rappi ni Mercado Libre. Ver GET /v1/capabilities.`,
      },
      {
        q: "¿Mis agentes pueden usar esto sin intervención humana?",
        a: `Búsqueda, comparación y canasta: sí, vía las ${MARKET_STATS.mcpTools} herramientas MCP. Pago: Yape/Plin requieren confirmación manual hoy; PayPal/Mercado Pago cierran vía webhook cuando el gateway está configurado.`,
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
      a: `${MARKET_STATS.retailersDefined} retailers in catalog, ${MARKET_STATS.retailersVerified} verified active, across ${MARKET_STATS.countries} countries. 4 platforms: VTEX (${MARKET_STATS.platformVtex}), Shopify (${MARKET_STATS.platformShopify} fashion/beauty brands), Magento (${MARKET_STATS.platformMagento}), and WooCommerce (${MARKET_STATS.platformWooCommerce} FMCG pilot).`,
    },
    {
      q: "How do payments and billing work?",
      a: `${billingPolicy} Channels: ${channels}. Confirmation updates your tier or order automatically. Receipts: hello@cli-market.dev.`,
    },
    {
      q: "Does the agent buy on the retailer's website?",
      a: `No — not on the retailer's own checkout. CLI Market unifies search/compare across ${MARKET_STATS.retailersVerified} stores; Pro checkout creates an internal order and charges via Yape/Plin/PayPal (LATAM). It does not complete checkout on Wong, Rappi, or Mercado Libre. See GET /v1/capabilities.`,
    },
    {
      q: "Can my agents use this autonomously?",
      a: `Search, compare, and basket: yes, via ${MARKET_STATS.mcpTools} MCP tools. Payment: Yape/Plin need manual confirmation today; PayPal/Mercado Pago close via webhook when the gateway is configured.`,
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
  const isES = lang === "es";
  const paymentsLabel = usePaymentsChannels(isES);
  const faqs = faqsFor(lang, paymentsLabel);

  return (
    <section id="faq" className="landing-section animate-fade-in">
      <div className="landing-container-wide">
        <div className="landing-section-header text-center">
          <p className="section-eyebrow mb-4">FAQ</p>
          <h2 className="section-title">
            {isES ? "Preguntas frecuentes." : "Frequently asked questions."}
          </h2>
        </div>

        <div className="landing-content-narrow text-left space-y-0">
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
