"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function RetailersSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const steps = [
    { icon: "1", title: isES ? "Tu plataforma" : "Your platform",
      desc: isES ? "VTEX, Shopify y Magento. Ya nos conectamos, cero desarrollo." : "VTEX, Shopify, and Magento. We already connect — zero dev work." },
    { icon: "2", title: isES ? "30 segundos" : "30 seconds",
      desc: isES ? "Token de solo lectura. Sin acceso a tus clientes ni a tus ventas." : "Read-only token. No access to your customers or sales." },
    { icon: "3", title: isES ? "Apareces" : "You appear",
      desc: isES
        ? `Tus productos comparados por agentes de IA junto a ${MARKET_STATS.retailersVerified} retailers verificados.`
        : `Your products compared by AI agents alongside ${MARKET_STATS.retailersVerified} verified retailers.` },
  ];

  const benefits = isES
    ? [
        "Sin costo. Licencia MIT, open source.",
        "Sin integración técnica: si ya vendes online, ya está listo.",
        "Canal nuevo: agentes que comparan precios en tiempo real.",
      ]
    : [
        "No cost. MIT license, open source.",
        "No technical integration: if you already sell online, you're ready.",
        "New channel: agents comparing prices in real time.",
      ];

  return (
    <section id="retailers" className="landing-section landing-section-alt scroll-mt-24" itemScope itemType="https://schema.org/Service">
      <meta itemProp="name" content="CLI Market Retailer Listing" />
      <meta itemProp="description" content={isES ? "Lista tu tienda gratis en CLI Market. VTEX, Shopify o Magento. 30 segundos. Sin costo." : "List your store on CLI Market free. VTEX, Shopify, or Magento. 30 seconds. No cost."} />
      <meta itemProp="offers" content='{"@type":"Offer","price":"0","priceCurrency":"USD"}' />

      <div className="landing-container-wide">
        <div className="flex items-center justify-center gap-3 mb-4">
          <span className="h-px w-12 bg-[var(--cm-outline-variant)]/40" aria-hidden="true" />
          <p className="font-label-caps text-[var(--cm-mint)]">
            {isES ? "Para retailers · Puerta B" : "For retailers · Door B"}
          </p>
          <span className="h-px w-12 bg-[var(--cm-outline-variant)]/40" aria-hidden="true" />
        </div>
        <h2 className="section-title mb-3 text-center">
          {isES ? "Tu tienda en las búsquedas de agentes de IA." : "Your store in AI agent searches."}
        </h2>
        <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-2xl mx-auto mb-8 text-center">
          {isES ? "Gratis, en 30 segundos." : "Free, in 30 seconds."}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {steps.map((s) => (
            <div key={s.icon} className="card-cyber header-strip p-5 text-left">
              <span className="inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-black text-[var(--cm-on-mint)] bg-[var(--cm-mint)] mb-3">{s.icon}</span>
              <h3 className="text-white font-bold text-sm mb-1">{s.title}</h3>
              <p className="text-[11px] text-[var(--cm-on-surface-variant)] leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8 max-w-3xl mx-auto">
          {benefits.map((b, i) => (
            <div key={i} className={`flex items-start gap-2 ${i === 2 ? "sm:col-span-2 sm:justify-center" : ""}`}>
              <span className="text-[var(--cm-mint)] mt-0.5 shrink-0">✓</span>
              <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">{b}</p>
            </div>
          ))}
        </div>

        <div className="text-center">
          <a href="#contact-retailers" className="inline-block border border-[var(--cm-mint)] text-[var(--cm-mint)] font-semibold text-sm px-8 py-3 hover:bg-[var(--cm-mint)] hover:text-[var(--cm-on-mint)] transition-colors font-mono uppercase tracking-wider">
            {isES ? "Listar mi tienda — gratis →" : "List my store — free →"}
          </a>
        </div>
      </div>
    </section>
  );
}
