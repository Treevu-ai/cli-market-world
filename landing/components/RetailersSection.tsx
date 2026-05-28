"use client";
import { useLang } from "@/lib/LanguageContext";

export default function RetailersSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const steps = [
    { icon: "1", title: isES ? "Tu plataforma" : "Your platform",
      desc: isES ? "VTEX y Magento. Ya nos conectamos. Cero desarrollo." : "VTEX and Magento. We already connect. Zero dev work." },
    { icon: "2", title: isES ? "30 segundos" : "30 seconds",
      desc: isES ? "Token de solo lectura. Sin acceso a clientes ni ventas." : "Read-only token. No customer or sales data access." },
    { icon: "3", title: isES ? "Apareces" : "You appear",
      desc: isES ? "Tus productos comparados por agentes de IA junto a 41 retailers." : "Your products compared by AI agents alongside 41 retailers." },
  ];

  const benefits = isES
    ? ["Sin costo. Siempre. La competencia cobra USD 500/mes por menos cobertura.",
       "Sin integración técnica. Si ya vendes online, ya estas listo.",
       "Visibilidad en un canal que no existía hace 6 meses: agentes autónomos que compran solos.",
       "Cada día sin estar aquí es un día que tu competidor aparece y tú no."]
    : ["Free. Forever. Competitors charge $500/mo for less coverage.",
       "Zero technical integration. If you sell online, you're already ready.",
       "Visibility in a channel that didn't exist 6 months ago: autonomous AI shopping agents.",
       "Every day you're not here, your competitor is — and you stay invisible."];

  return (
    <section id="retailers" className="relative bg-[var(--wise-ink)] py-24" itemScope itemType="https://schema.org/Service">
      <meta itemProp="name" content="CLI Market Retailer Listing" />
      <meta itemProp="description" content={isES ? "Agrega tu tienda gratis a CLI Market. VTEX, Shopify o Magento. 30 segundos. Sin costo. Tus productos visibles para agentes de IA." : "List your store on CLI Market free. VTEX, Shopify, or Magento. 30 seconds. No cost. Products visible to AI agents."} />
      <meta itemProp="offers" content='{"@type":"Offer","price":"0","priceCurrency":"USD"}' />

      <div className="max-w-[1100px] mx-auto px-6">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-6 text-center">
          {isES ? "Para retailers" : "For retailers"}
        </p>
        <h2 className="text-[clamp(28px,5vw,48px)] leading-[1.05] font-black text-white mb-4 text-center tracking-tight">
          {isES ? "Tu tienda, sin costo.\nDesde hoy." : "Your store, zero cost.\nStarting today."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-[600px] mx-auto mb-4 text-center">
          {isES
            ? "Si usas VTEX, Shopify o Magento, tus productos YA pueden aparecer en busquedas de agentes de IA. En 30 segundos. Sin pagar un centavo."
            : "If you use VTEX or Magento, your products can ALREADY appear in AI agent searches. 30 seconds. Zero cost."}
        </p>
        <p className="text-[11px] text-[#ffbd2e] max-w-[600px] mx-auto mb-12 text-center font-medium">
          {isES
            ? "La competencia cobra cientos de dolares al mes. Nosotros no. Plazas limitadas por pais."
            : "Competitors charge hundreds per month. We don't. Limited spots per country."}
        </p>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-14">
          {steps.map((s) => (
            <div key={s.icon} className="bg-[#1a1d19] rounded-2xl p-6 border border-[#2a2d25] text-left">
              <span className="inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-black text-[var(--wise-ink)] bg-[var(--wise-green)] mb-3">{s.icon}</span>
              <h3 className="text-white font-bold text-sm mb-1">{s.title}</h3>
              <p className="text-[11px] text-[var(--wise-body)] leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>

        {/* Benefits */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-12 max-w-[800px] mx-auto">
          {benefits.map((b, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="text-[var(--wise-green)] mt-0.5 shrink-0">✓</span>
              <p className="text-xs text-[var(--wise-body)] leading-relaxed">{b}</p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center">
          <a href="#contact" className="inline-block bg-[var(--wise-green)] text-[var(--wise-ink)] font-black text-sm px-8 py-3.5 rounded-full hover:bg-white transition-colors shadow-lg">
            {isES ? "Quiero que mi tienda aparezca →" : "I want my store listed →"}
          </a>
          <p className="text-[10px] text-[var(--wise-mute)] mt-3 font-mono">
            {isES ? "Gratis. Siempre. MIT. Sin letra chica." : "Free. Forever. MIT. No fine print."}
          </p>
        </div>
      </div>
    </section>
  );
}
