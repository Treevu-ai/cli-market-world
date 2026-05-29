"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

function faqsFor(lang: "es" | "en") {
  const isES = lang === "es";
  const rp = isES ? MARKET_STATS.retailersPhraseEs : MARKET_STATS.retailersPhraseEn;
  const pp = isES ? MARKET_STATS.platformsPhraseEs : MARKET_STATS.platformsPhraseEn;

  if (isES) {
    return [
      {
        q: "¿Qué es CLI Market?",
        a: `CLI Market es una API y CLI que permite a agentes de IA buscar, comparar y comprar productos en ${rp}. Precios de góndola normalizados por unidad. Una sola API. Cero scraping.`,
      },
      {
        q: "¿Con qué retailers funciona?",
        a: `${MARKET_STATS.retailersDefined} retailers en catálogo, ${MARKET_STATS.retailersVerified} verificados activos en ${MARKET_STATS.businessLines} líneas. ${pp}. VTEX (${MARKET_STATS.platformVtex}), Shopify (${MARKET_STATS.platformShopify} marcas moda/beauty), Magento (${MARKET_STATS.platformMagento}).`,
      },
      {
        q: "¿Cómo funciona el pago?",
        a: `Aceptamos ${MARKET_STATS.paymentsLabel}. El checkout genera un QR que escaneas desde tu app de pagos. El webhook confirma la transacción y actualiza el estado de tu orden automáticamente.`,
      },
      {
        q: "¿Mis agentes pueden usar esto sin intervención humana?",
        a: `Sí. Las ${MARKET_STATS.mcpTools} herramientas MCP están diseñadas para que tu agente busque, compare, arme canastas y complete compras de forma autónoma. El pago requiere aprobación humana por ahora.`,
      },
      {
        q: "¿Los precios son reales?",
        a: `Sí. Nuestro collector corre cada ${MARKET_STATS.pricesRefreshHours} horas contra ${MARKET_STATS.retailersVerified} retailers verificados y extrae precios reales de góndola. ${MARKET_STATS.pricesVerifiedLabel} precios normalizados por kilo/litro, filtrados antes de publicar comparaciones.`,
      },
      {
        q: "¿Cuánto cuesta?",
        a: "La CLI es open source y gratuita (licencia MIT). La API tiene un tier gratuito de 1,000 consultas al día. El plan Pro cuesta USD 49 al mes con checkout habilitado y data export. Si tienes un caso más grande, escríbenos.",
      },
    ];
  }

  return [
    {
      q: "What is CLI Market?",
      a: `CLI Market is an API and CLI that lets AI agents search, compare, and buy products across ${rp}. Unit-normalized shelf prices. One API. Zero scraping.`,
    },
    {
      q: "Which retailers do you support?",
      a: `${MARKET_STATS.retailersDefined} retailers in catalog, ${MARKET_STATS.retailersVerified} verified active across ${MARKET_STATS.businessLines} lines. ${pp}. VTEX (${MARKET_STATS.platformVtex}), Shopify (${MARKET_STATS.platformShopify} fashion/beauty brands), Magento (${MARKET_STATS.platformMagento}).`,
    },
    {
      q: "How does payment work?",
      a: `${MARKET_STATS.paymentsLabel}. Checkout generates a QR code you scan from your payment app. A webhook confirms the transaction and updates your order status automatically.`,
    },
    {
      q: "Can my agents use this autonomously?",
      a: `Yes. All ${MARKET_STATS.mcpTools} MCP tools are designed for agents to search, compare, build baskets, and complete purchases autonomously. Payment requires human approval for now.`,
    },
    {
      q: "Are the prices real?",
      a: `Yes. Our collector runs every ${MARKET_STATS.pricesRefreshHours} hours against ${MARKET_STATS.retailersVerified} verified retailers and extracts real shelf prices. ${MARKET_STATS.pricesVerifiedLabel} prices normalized per kg/L and filtered before publishing comparisons.`,
    },
    {
      q: "How much does it cost?",
      a: "The CLI is open source and free (MIT license). The API has a free tier of 1,000 requests per day. The Pro plan is USD 49/month with checkout enabled and data export. For larger use cases, contact us.",
    },
  ];
}

export default function FAQ() {
  const { lang } = useLang();
  const faqs = faqsFor(lang);

  return (
    <section id="faq" className="relative bg-[var(--wise-canvas-soft)] py-16 border-t border-[#c5edab]">
      <div className="landing-container text-center">
        <p className="text-xs text-[var(--wise-body)] font-mono uppercase tracking-[0.15em] mb-8">FAQ</p>
        <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-12 tracking-tight">
          {lang === "es" ? "Preguntas frecuentes." : "Frequently asked questions."}
        </h2>

        <div className="text-left divide-y divide-[#e5e5e5]">
          {faqs.map((faq, i) => (
            <div key={i} className="py-4">
              <h3 className="text-sm font-medium text-[var(--wise-ink)] mb-1">{faq.q}</h3>
              <p className="text-sm text-[var(--wise-body)] leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
