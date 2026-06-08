"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function RetailersPricingPanel() {
  const { lang } = useLang();
  const isES = lang === "es";

  const steps = [
    {
      icon: "1",
      title: isES ? "Tu plataforma" : "Your platform",
      desc: isES
        ? "VTEX, Shopify, Magento y WooCommerce. Ya nos conectamos. Cero desarrollo."
        : "VTEX, Shopify, Magento, and WooCommerce. We already connect. Zero dev work.",
    },
    {
      icon: "2",
      title: isES ? "30 segundos" : "30 seconds",
      desc: isES
        ? "Token de solo lectura. Sin acceso a clientes ni ventas."
        : "Read-only token. No customer or sales data access.",
    },
    {
      icon: "3",
      title: isES ? "Apareces" : "You appear",
      desc: isES
        ? `Tus productos comparados por agentes de IA junto a ${MARKET_STATS.retailersVerified} retailers verificados.`
        : `Your products compared by AI agents alongside ${MARKET_STATS.retailersVerified} verified retailers.`,
    },
  ];

  const benefits = isES
    ? [
        "Sin costo, siempre. MIT. Sin letra chica.",
        "Sin integración técnica. Si ya vende online, ya está listo.",
        "Canal nuevo: agentes que comparan precios en tiempo real.",
      ]
    : [
        "Free forever. MIT. No fine print.",
        "Zero technical integration. If you sell online, you're already ready.",
        "New channel: agents comparing prices in real time.",
      ];

  return (
    <div
      id="retailers"
      className="scroll-mt-24 text-left"
      itemScope
      itemType="https://schema.org/Service"
    >
      <meta itemProp="name" content="CLI Market Retailer Listing" />
      <meta
        itemProp="description"
        content={
          isES
            ? "Lista tu tienda gratis en CLI Market. VTEX, Shopify, Magento o WooCommerce. 30 segundos. Sin costo."
            : "List your store on CLI Market free. VTEX, Shopify, Magento, or WooCommerce. 30 seconds. No cost."
        }
      />
      <meta itemProp="offers" content='{"@type":"Offer","price":"0","priceCurrency":"USD"}' />

      <div className="flex items-center justify-center gap-3 mb-4">
        <span className="h-px w-12 bg-[var(--cm-outline-variant)]/30" aria-hidden="true" />
        <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60">
          {isES ? "Para retailers · Puerta B" : "For retailers · Door B"}
        </p>
        <span className="h-px w-12 bg-[var(--cm-outline-variant)]/30" aria-hidden="true" />
      </div>
      <h3 className="text-[clamp(22px,4vw,32px)] leading-[1.1] font-bold text-white mb-3 text-center tracking-tight">
        {isES
          ? "Tu tienda en las búsquedas de agentes. Gratis, desde hoy."
          : "Your store in agent searches. Free, starting today."}
      </h3>
      <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-2xl mx-auto mb-4 text-center">
        {isES
          ? "Si usas VTEX, Shopify, Magento o WooCommerce, tus productos ya pueden aparecer en búsquedas de agentes de IA. En 30 segundos. Sin pagar un centavo."
          : "If you use VTEX, Shopify, Magento, or WooCommerce, your products can already appear in AI agent searches. 30 seconds. Zero cost."}
      </p>
      <p className="text-xs text-[var(--cm-mint)] max-w-2xl mx-auto mb-8 text-center font-medium">
        {isES ? "Gratis para siempre. Plazas limitadas por país." : "Free forever. Limited spots per country."}
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {steps.map((s) => (
          <div key={s.icon} className="card-cyber p-5 text-left">
            <span className="inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-black text-[var(--cm-on-mint)] bg-[var(--cm-mint)] mb-3">
              {s.icon}
            </span>
            <h4 className="text-white font-bold text-sm mb-1">{s.title}</h4>
            <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">{s.desc}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8 max-w-3xl mx-auto">
        {benefits.map((b, i) => (
          <div key={i} className="flex items-start gap-2">
            <span className="text-[var(--cm-mint)] mt-0.5 shrink-0">✓</span>
            <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">{b}</p>
          </div>
        ))}
      </div>

      <div className="text-center">
        <a
          href="/retailers"
          className="inline-block border-2 border-[var(--cm-mint)] text-[var(--cm-mint)] font-semibold text-sm px-8 py-3 rounded-full hover:bg-[var(--cm-mint)] hover:text-[var(--cm-on-mint)] transition-colors"
        >
          {isES ? "Listar mi tienda — gratis →" : "List my store — free →"}
        </a>
        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mt-3 font-mono">
          {isES ? "Gratis. Siempre. MIT. Sin letra chica." : "Free. Forever. MIT. No fine print."}
        </p>
      </div>
    </div>
  );
}