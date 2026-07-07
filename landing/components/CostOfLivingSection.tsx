"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import AffordabilityBadge from "@/components/AffordabilityBadge";

const FEATURES_ES = [
  {
    icon: "📊",
    title: "Affordability OS",
    desc: "Score 0–100 de asequibilidad desde precios reales de góndola — no de encuestas.",
  },
  {
    icon: "🔄",
    title: "Sustitutos inteligentes",
    desc: "Cuando el producto ideal supera tu presupuesto, encuentra la mejor alternativa verificada.",
  },
  {
    icon: "🛒",
    title: "Canasta optimizada",
    desc: "TCO real: precio de góndola + delivery + comisión del método de pago. Sin sorpresas.",
  },
  {
    icon: "📋",
    title: "Contexto regulatorio",
    desc: "Eventos regulatorios (aranceles, IVA, controles) que explican movimientos de precio.",
  },
];

const FEATURES_EN = [
  {
    icon: "📊",
    title: "Affordability OS",
    desc: "0–100 affordability score from real shelf prices — not surveys.",
  },
  {
    icon: "🔄",
    title: "Smart substitutes",
    desc: "When the ideal product exceeds your budget, find the best verified alternative.",
  },
  {
    icon: "🛒",
    title: "Optimized basket",
    desc: "Real TCO: shelf price + delivery + payment fee. No surprises.",
  },
  {
    icon: "📋",
    title: "Regulatory context",
    desc: "Regulatory events (tariffs, VAT, controls) that explain price moves.",
  },
];

const TIERS_ES = [
  { name: "Free", price: "Gratis", features: ["Affordability score", "Sustitutos (1/consulta)", "Canasta básica"] },
  { name: "Starter", price: "$9/mes", features: ["Todo Free", "Sustitutos ilimitados", "TCO + delivery"], highlight: false },
  { name: "Pro", price: "$49/mes", features: ["Todo Starter", "optimize purchase", "Contexto regulatorio", "Export CSV"], highlight: true },
];

const TIERS_EN = [
  { name: "Free", price: "Free", features: ["Affordability score", "Substitutes (1/query)", "Basic basket"] },
  { name: "Starter", price: "$9/mo", features: ["All Free", "Unlimited substitutes", "TCO + delivery"], highlight: false },
  { name: "Pro", price: "$49/mo", features: ["All Starter", "optimize purchase", "Regulatory context", "CSV export"], highlight: true },
];

export default function CostOfLivingSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const features = isES ? FEATURES_ES : FEATURES_EN;
  const tiers = isES ? TIERS_ES : TIERS_EN;
  const featRef = useRef(null);
  const inView = useInView(featRef, { once: true, margin: "-60px" });

  return (
    <>
      {/* Live affordability signal */}
      <section className="landing-section landing-section-alt !pt-12 scroll-mt-24">
        <div className="landing-container-wide">
          <div className="max-w-2xl mx-auto text-center mb-8">
            <p className="section-eyebrow mb-3">
              {isES ? "SEÑAL EN VIVO — PERÚ" : "LIVE SIGNAL — PERU"}
            </p>
            <h2 className="section-title mb-4">
              {isES ? (
                <>¿Cuánto cuesta <span className="text-gradient-orange">vivir hoy</span>?</>
              ) : (
                <>What does it cost to <span className="text-gradient-orange">live today</span>?</>
              )}
            </h2>
            <AffordabilityBadge country="PE" lang={isES ? "es" : "en"} className="mx-auto" />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-3xl mx-auto">
            {[
              { country: "PE", flag: "🇵🇪", label: "Perú" },
              { country: "MX", flag: "🇲🇽", label: "México" },
              { country: "CO", flag: "🇨🇴", label: "Colombia" },
            ].map(({ country, flag, label }) => (
              <div key={country} className="card-cyber rounded-xl p-4 text-center">
                <p className="text-2xl mb-1">{flag}</p>
                <p className="text-sm font-semibold text-[var(--cm-on-surface)]">{label}</p>
                <AffordabilityBadge
                  country={country}
                  lang={isES ? "es" : "en"}
                  className="mt-2 mx-auto"
                />
              </div>
            ))}
          </div>

          <p className="text-center text-xs font-mono text-[var(--cm-on-surface-variant)]/50 mt-6">
            {isES
              ? `Actualizado cada 4h · fuente: ${" "}góndola verificada CLI Market`
              : `Refreshed every 4h · source: CLI Market verified shelf`}
          </p>

          {/* Dashboard CTA */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
            <a
              href="/dashboard/household"
              className="inline-flex items-center gap-2 rounded-lg bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold px-5 py-2.5 hover:opacity-90 transition-opacity"
            >
              {isES ? "Configurar mi hogar →" : "Set up my household →"}
            </a>
            <a
              href="/dashboard/household#tickets"
              className="inline-flex items-center gap-2 rounded-lg border border-[var(--cm-outline-variant)] text-sm font-mono text-[var(--cm-on-surface-variant)] px-5 py-2.5 hover:border-[var(--cm-mint)] hover:text-[var(--cm-on-surface)] transition-colors"
            >
              {isES ? "Subir ticket de compra" : "Upload receipt"}
            </a>
          </div>
        </div>
      </section>

      {/* Features grid */}
      <section ref={featRef} className="landing-section scroll-mt-24">
        <div className="landing-container-wide">
          <div className="landing-section-header text-center mb-10">
            <p className="section-eyebrow mb-4">
              {isES ? "CAPACIDADES" : "CAPABILITIES"}
            </p>
            <h2 className="section-title">
              {isES ? (
                <>
                  Más allá del precio de <span className="text-gradient-orange">lista</span>
                </>
              ) : (
                <>
                  Beyond the <span className="text-gradient-orange">list price</span>
                </>
              )}
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                className="card-cyber rounded-xl p-5"
                initial={{ opacity: 0, y: 16 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.4, delay: i * 0.08 }}
              >
                <p className="text-2xl mb-3">{f.icon}</p>
                <p className="text-sm font-bold text-[var(--cm-on-surface)] mb-2">{f.title}</p>
                <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CLI showcase */}
      <section className="landing-section landing-section-alt scroll-mt-24">
        <div className="landing-container-wide">
          <div className="max-w-2xl mx-auto">
            <p className="section-eyebrow mb-4 text-center">
              {isES ? "INTERFAZ CLI" : "CLI INTERFACE"}
            </p>
            <h2 className="section-title text-center mb-8">
              {isES ? (
                <>Una línea para <span className="text-gradient-orange">optimizar tu canasta</span></>
              ) : (
                <>One line to <span className="text-gradient-orange">optimize your basket</span></>
              )}
            </h2>
            <div className="rounded-xl bg-[#0a0c0f] border border-[#1e2a22] p-5 font-mono text-sm overflow-x-auto">
              <p className="text-[#666] text-xs mb-3">$ # {isES ? "compra óptima con TCO real" : "optimal buy with real TCO"}</p>
              <p className="text-[#00FF88]">{"$ market optimize leche:2 arroz:1kg aceite:1 --budget 30"}</p>
              <p className="text-[#888] mt-3 text-xs">
                {"→ "}{isES ? "Recomendación: " : "Recommendation: "}
                <span className="text-[#00FF88]">BUY_NOW</span>
              </p>
              <p className="text-[#888] text-xs">
                {"  "}{isES ? "Tienda: Wong · Góndola: PEN 28.50 · TCO: PEN 35.50" : "Store: Wong · Shelf: PEN 28.50 · TCO: PEN 35.50"}
              </p>
              <p className="text-[#888] text-xs mt-1">
                {"  "}{isES ? "Sustit.: Leche Gloria → Laive (–S/ 0.60/L)" : "Subst.: Leche Gloria → Laive (–S/ 0.60/L)"}
              </p>
              <p className="text-[#888] text-xs mt-1">
                {"  "}{isES ? "Delivery Rappi: S/ 7.00 · Método sugerido: Yape (sin comisión)" : "Rappi delivery: S/ 7.00 · Suggested method: Yape (no fee)"}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing tiers */}
      <section className="landing-section scroll-mt-24" id="cost-of-living-pricing">
        <div className="landing-container-wide">
          <p className="section-eyebrow mb-4 text-center">
            {isES ? "PLANES" : "PLANS"}
          </p>
          <h2 className="section-title text-center mb-10">
            {isES ? "Incluido en tu plan CLI Market" : "Included in your CLI Market plan"}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 max-w-3xl mx-auto">
            {tiers.map((tier) => (
              <div
                key={tier.name}
                className={`card-cyber rounded-xl p-5 ${tier.highlight ? "energy-border-active" : ""}`}
              >
                {tier.highlight && (
                  <span className="inline-block mb-3 text-xs font-semibold bg-[var(--cm-mint)] text-[var(--cm-on-mint)] px-3 py-0.5 rounded-full">
                    {isES ? "Más popular" : "Most popular"}
                  </span>
                )}
                <p className="text-base font-bold text-[var(--cm-on-surface)]">{tier.name}</p>
                <p className="text-2xl font-black text-[var(--cm-on-surface)] mt-1 mb-4">{tier.price}</p>
                <ul className="space-y-2">
                  {tier.features.map((f) => (
                    <li key={f} className="flex gap-2 text-xs text-[var(--cm-on-surface-variant)]">
                      <span className="text-[var(--cm-mint)] shrink-0">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
