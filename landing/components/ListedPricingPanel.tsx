"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function ListedPricingPanel() {
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
      title: isES ? "En el radar" : "On the radar",
      desc: isES
        ? `Tu góndola comparada por agentes junto a ${MARKET_STATS.retailersVerified} retailers verificados.`
        : `Your shelf compared by agents alongside ${MARKET_STATS.retailersVerified} verified retailers.`,
    },
  ];

  const benefits = isES
    ? [
        "$0 para siempre. MIT. Sin letra chica.",
        "Sin integración: si ya vende online, ya está listo.",
        "Canal nuevo: agentes que comparan precios en tiempo real.",
      ]
    : [
        "$0 forever. MIT. No fine print.",
        "Zero integration: if you sell online, you're already ready.",
        "New channel: agents comparing prices in real time.",
      ];

  return (
    <div
      id="listed"
      className="scroll-mt-24 text-left"
      itemScope
      itemType="https://schema.org/Service"
    >
      <meta itemProp="name" content="CLI Market Listed — free shelf listing" />
      <meta
        itemProp="description"
        content={
          isES
            ? "Listed: muestra tu góndola gratis en CLI Market. VTEX, Shopify, Magento o WooCommerce. 30 segundos."
            : "Listed: show your shelf free on CLI Market. VTEX, Shopify, Magento, or WooCommerce. 30 seconds."
        }
      />
      <meta itemProp="offers" content='{"@type":"Offer","price":"0","priceCurrency":"USD"}' />

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
          {isES ? "Listed — listar mi tienda →" : "Listed — list my store →"}
        </a>
        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mt-3 font-mono">
          {isES ? "Góndola visible · gratis · siempre" : "Shelf visible · free · forever"}
        </p>
      </div>
    </div>
  );
}