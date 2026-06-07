"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

function faqsFor(lang: "es" | "en") {
  const isES = lang === "es";
  const rp = isES ? MARKET_STATS.retailersPhraseEs : MARKET_STATS.retailersPhraseEn;

  if (isES) {
    return [
      {
        q: "¿Qué es CLI Market?",
        a: `CLI Market es infraestructura de comercio para agentes de IA y equipos comerciales: ${MARKET_STATS.pricesVerifiedLabel} precios de góndola normalizados por kg/L sobre ${rp}. Intelligence (piloto USD 300–500/mes) para spreads e inflación; Build (Free/Pro) para integrar API y MCP. Cero scraping.`,
      },
      {
        q: "¿Con qué retailers funciona?",
        a: `${MARKET_STATS.retailersDefined} retailers en catálogo, ${MARKET_STATS.retailersVerified} verificados activos, en ${MARKET_STATS.countries} países. 4 plataformas: VTEX (${MARKET_STATS.platformVtex}), Shopify (${MARKET_STATS.platformShopify} marcas moda/beauty) y Magento (${MARKET_STATS.platformMagento}).`,
      },
      {
        q: "¿Cómo funciona el pago?",
        a: `Aceptamos ${MARKET_STATS.paymentsLabel}. Checkout con tarjeta vía PayPal para pagos internacionales, y QR de Yape/Plin para pagos locales en Perú. El webhook confirma la transacción y actualiza tu orden automáticamente.`,
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
        a: "Build (API/MCP): Free 1.000 consultas/día; Starter USD 29/mes (5.000/día, CSV, activación manual ≤24h); Pro USD 79/mes (10.000/día, checkout y export avanzado). Intelligence (datos comerciales): en desarrollo — lista de espera en la sección Intelligence. Listado retailer: gratis siempre.",
      },
    ];
  }

  return [
    {
      q: "What is CLI Market?",
      a: `CLI Market is commerce infrastructure for AI agents and commercial teams: ${MARKET_STATS.pricesVerifiedLabel} shelf prices normalized per kg/L across ${rp}. Intelligence (pilot USD 300–500/mo) for spreads and inflation; Build (Free/Pro) to integrate API and MCP. Zero scraping.`,
    },
      {
        q: "Which retailers do you support?",
        a: `${MARKET_STATS.retailersDefined} retailers in catalog, ${MARKET_STATS.retailersVerified} verified active, across ${MARKET_STATS.countries} countries. 4 platforms: VTEX (${MARKET_STATS.platformVtex}), Shopify (${MARKET_STATS.platformShopify} fashion/beauty brands), and Magento (${MARKET_STATS.platformMagento}).`,
      },
    {
      q: "How does payment work?",
      a: `${MARKET_STATS.paymentsLabel}. Card checkout via PayPal for international payments, and Yape/Plin QR for local payments in Peru. A webhook confirms the transaction and updates your order status automatically.`,
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
      a: "Build (API/MCP): Free 1,000 requests/day; Starter USD 29/mo (5,000/day, CSV, manual activation ≤24h); Pro USD 79/mo (10,000/day, checkout and advanced export). Intelligence (commercial data): in development — waitlist in the Intelligence section. Retailer listing: free forever.",
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

        <div className="text-left divide-y divide-[var(--cm-outline-variant)]/30 mt-12">
          {faqs.map((faq, i) => (
            <div key={i} className="py-6">
              <h3 className="text-base font-medium text-white mb-3">{faq.q}</h3>
              <p className="text-base text-[var(--cm-on-surface-variant)] leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
