"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ActiveBrandTicker from "@/components/ActiveBrandTicker";
import RetailerApplyModal from "@/components/RetailerApplyModal";
import ScrambleText from "@/components/ScrambleText";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLang } from "@/lib/LanguageContext";

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-40px" },
  transition: { duration: 0.45, ease: "easeOut" as const },
};

export default function RetailersPage() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [applyOpen, setApplyOpen] = useState(false);

  const stats = [
    { n: String(MARKET_STATS.retailersVerified), l: isES ? "Retailers activos" : "Retailers live" },
    { n: MARKET_STATS.pricesVerifiedLabel, l: isES ? "Precios indexados" : "Prices indexed" },
    { n: String(MARKET_STATS.countries), l: isES ? "Países" : "Countries" },
    { n: `${MARKET_STATS.pricesRefreshHours}h`, l: isES ? "Actualización de precios" : "Price refresh" },
  ];

  const benefits = [
    {
      t: isES ? "Visibilidad en canales de IA" : "Visibility in AI channels",
      d: isES
        ? `Los agentes de IA comparan productos automáticamente para compradores empresariales. Tus productos aparecen en sus resultados — como el SEO de la era de agentes. Cada día que no estás, tu competidor sí.`
        : `AI agents automatically compare products for business buyers. Your products appear in their results — like SEO for the agent era. Every day you're not here, your competitor is.`,
    },
    {
      t: isES ? "Inteligencia competitiva en tiempo real" : "Real-time competitive intelligence",
      d: isES
        ? `Ve cómo tus precios se posicionan frente a ${MARKET_STATS.retailersVerified} retailers verificados. Detecta spread de precios, identifica oportunidades y ajusta antes de perder ventas frente a un rival que ya sí está indexado.`
        : `See how your prices position against ${MARKET_STATS.retailersVerified} verified retailers. Detect price spreads, spot opportunities, and adjust before losing sales to an already-indexed competitor.`,
    },
    {
      t: isES ? "Sin integración técnica requerida" : "No technical integration required",
      d: isES
        ? "Completa un formulario. Nuestro equipo indexa tu catálogo sin que muevas un dedo. Sin SDK, sin APIs, sin desarrolladores. Gratis para siempre."
        : "Fill out a form. Our team indexes your catalog without you lifting a finger. No SDK, no APIs, no developers. Free forever.",
    },
  ];

  const steps = [
    {
      step: "01",
      title: isES ? "Completa el formulario" : "Fill out the form",
      desc: isES
        ? "Nombre de tu tienda, URL, categoría de productos y país. Menos de 2 minutos. Sin datos sensibles."
        : "Store name, URL, product category, and country. Less than 2 minutes. No sensitive data.",
    },
    {
      step: "02",
      title: isES ? "Nuestro equipo verifica tu catálogo" : "Our team verifies your catalog",
      desc: isES
        ? "Indexamos tus productos con precios normalizados por unidad (kg, L, unidad). Te confirmamos en 24–48 horas."
        : "We index your products with unit-normalized prices (kg, L, unit). We confirm within 24–48 hours.",
    },
    {
      step: "03",
      title: isES ? "Tus productos aparecen en búsquedas" : "Your products appear in searches",
      desc: isES
        ? "Compradores empresariales, agentes de IA y herramientas de procurement encuentran tus productos y los comparan contra tu competencia."
        : "Business buyers, AI agents, and procurement tools find your products and compare them against your competition.",
    },
  ];

  return (
    <main className="relative min-h-screen bg-[var(--cm-background)]">
      <div className="grid-bg fixed inset-0 opacity-40 pointer-events-none" aria-hidden="true" />
      <Navbar />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: [
              {
                "@type": "Question",
                name: isES ? "¿Cómo listo mi tienda en CLI Market?" : "How do I list my store on CLI Market?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: isES
                    ? "Completa el formulario con el nombre de tu tienda, URL y categoría. Nuestro equipo indexa tu catálogo sin integración técnica de tu parte. Gratis para siempre."
                    : "Fill out the form with your store name, URL, and category. Our team indexes your catalog with no technical integration required. Free forever.",
                },
              },
              {
                "@type": "Question",
                name: isES ? "¿CLI Market es gratis para retailers?" : "Is CLI Market free for retailers?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: isES
                    ? "Sí. Completamente gratis. Sin costos ocultos, sin límites de uso, sin tarjeta de crédito."
                    : "Yes. Completely free. No hidden fees, no usage limits, no credit card required.",
                },
              },
              {
                "@type": "Question",
                name: isES ? "¿Necesito un equipo técnico para integrarme?" : "Do I need a technical team to integrate?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: isES
                    ? "No. Solo completa el formulario con la URL de tu tienda. Nuestro equipo realiza la indexación. Sin APIs, sin desarrolladores, sin configuración técnica."
                    : "No. Just fill out the form with your store URL. Our team handles the indexing. No APIs, no developers, no technical setup.",
                },
              },
              {
                "@type": "Question",
                name: isES ? "¿Cuántos retailers ya están en CLI Market?" : "How many retailers are already on CLI Market?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: isES
                    ? `${MARKET_STATS.retailersDefined} retailers en ${MARKET_STATS.countries} países (${MARKET_STATS.retailersVerified} verificados activos): ${MARKET_STATS.countryCodes.join(", ")}. ${MARKET_STATS.pricesVerifiedLabel} precios reales actualizados cada ${MARKET_STATS.pricesRefreshHours} horas.`
                    : `${MARKET_STATS.retailersDefined} retailers across ${MARKET_STATS.countries} countries (${MARKET_STATS.retailersVerified} verified active): ${MARKET_STATS.countryCodes.join(", ")}. ${MARKET_STATS.pricesVerifiedLabel} real prices refreshed every ${MARKET_STATS.pricesRefreshHours} hours.`,
                },
              },
              {
                "@type": "Question",
                name: isES ? "¿Qué es GEO y por qué mi tienda lo necesita?" : "What is GEO and why does my store need it?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: isES
                    ? "GEO (Generative Engine Optimization) es el equivalente de SEO para agentes de IA. Cuando asistentes como ChatGPT y Claude buscan productos, usan índices de datos estructurados como CLI Market. Si tu tienda no está indexada, eres invisible para el canal de compras de mayor crecimiento."
                    : "GEO (Generative Engine Optimization) is the equivalent of SEO for AI agents. When AI assistants like ChatGPT and Claude search for products, they use structured data indexes like CLI Market. If your store isn't indexed, you're invisible to the fastest-growing shopping channel.",
                },
              },
            ],
          }),
        }}
      />

      <div className="relative z-10">
        <section className="py-24 px-[var(--cm-gutter)] text-center pt-28 bg-[var(--cm-surface-low)] border-b border-[var(--cm-outline-variant)]">
          <motion.div {...fadeUp} className="max-w-[720px] mx-auto">
            <p className="text-[11px] font-mono uppercase tracking-widest text-[var(--cm-mint)] mb-4">
              {isES ? "CLI Market para Retailers" : "CLI Market for Retailers"}
            </p>
            <h1 className="font-display text-[clamp(1.75rem,5vw,3rem)] leading-tight font-bold text-[var(--cm-on-surface)] mb-3 tracking-tight">
              {isES ? (
                <>
                  Tus productos, donde compran los negocios.{" "}
                  <ScrambleText
                    text="Gratis. Hoy."
                    autoStart
                    delay={600}
                    duration={0.6}
                    className="text-[var(--cm-mint)]"
                  />
                </>
              ) : (
                <>
                  Your products, where businesses buy.{" "}
                  <ScrambleText
                    text="Free. Today."
                    autoStart
                    delay={600}
                    duration={0.6}
                    className="text-[var(--cm-mint)]"
                  />
                </>
              )}
            </h1>
            <p className="text-[11px] text-[var(--cm-mint)] max-w-[500px] mx-auto mb-6 font-medium tracking-wide">
              {isES ? "Gratis para siempre. Cupos limitados por país." : "Free forever. Limited spots per country."}
            </p>
            <p className="text-base text-[var(--cm-on-surface-variant)] max-w-[500px] mx-auto leading-relaxed">
              {isES
                ? "Compradores empresariales y agentes de IA comparan precios en CLI Market antes de ordenar. Si tu catálogo no está indexado, sos invisible frente a quien ya sí está."
                : "Business buyers and AI agents compare prices on CLI Market before ordering. If your catalog isn't indexed, you're invisible against competitors who already are."}
            </p>
            <button
              type="button"
              onClick={() => setApplyOpen(true)}
              className="inline-flex items-center justify-center mt-8 px-8 py-3 rounded-[10px] bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold hover:opacity-90 transition-opacity shadow-lg"
            >
              {isES ? "Listar mi tienda — gratis" : "List my store — free"}
            </button>
          </motion.div>
        </section>

        <ActiveBrandTicker />

        <section className="py-16 px-[var(--cm-gutter)] border-b border-[var(--cm-outline-variant)]/20 landing-section-alt">
          <motion.div {...fadeUp} className="max-w-[720px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {stats.map((s) => (
              <div key={s.l}>
                <div className="text-3xl font-black text-[var(--cm-mint)]">{s.n}</div>
                <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{s.l}</div>
              </div>
            ))}
          </motion.div>
        </section>

        <section className="py-16 px-[var(--cm-gutter)] border-b border-[var(--cm-outline-variant)]/20">
          <motion.div {...fadeUp} className="max-w-[720px] mx-auto">
            <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-on-surface-variant)] text-center mb-2">
              {isES ? "Por qué aparecer" : "Why get listed"}
            </p>
            <h2 className="section-title mb-12 text-center">
              {isES ? "Lo que obtienes" : "What you get"}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {benefits.map((b, i) => (
                <motion.div
                  key={b.t}
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.08 }}
                  className="card-cyber header-strip p-6"
                >
                  <h3 className="text-sm font-bold text-[var(--cm-on-surface)] mb-2">{b.t}</h3>
                  <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">{b.d}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </section>

        <section className="py-16 px-[var(--cm-gutter)] border-b border-[var(--cm-outline-variant)]/20 landing-section-alt">
          <motion.div {...fadeUp} className="max-w-[560px] mx-auto">
            <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-on-surface-variant)] text-center mb-2">
              {isES ? "Proceso" : "How it works"}
            </p>
            <h2 className="section-title mb-12 text-center">
              {isES ? "Cómo aparecer" : "How to get listed"}
            </h2>
            <div className="space-y-4">
              {steps.map((s, i) => (
                <motion.div
                  key={s.step}
                  initial={{ opacity: 0, x: -12 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.35, delay: i * 0.06 }}
                  className="card-cyber p-5 flex gap-4"
                >
                  <span className="text-[var(--cm-mint)] font-bold text-2xl shrink-0">{s.step}</span>
                  <div>
                    <h3 className="text-sm font-bold text-[var(--cm-on-surface)] mb-1">{s.title}</h3>
                    <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">{s.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </section>

        <section className="py-24 px-[var(--cm-gutter)] text-center">
          <motion.div {...fadeUp} className="max-w-[520px] mx-auto">
            <h2 className="section-title mb-2">
              {isES ? "¿Listo para aparecer?" : "Ready to get listed?"}
            </h2>
            <p className="text-sm text-[var(--cm-on-surface-variant)] mb-8">
              {isES
                ? "Completa el formulario en 2 minutos. Sin tarjeta de crédito. Sin equipo técnico."
                : "Fill out the form in 2 minutes. No credit card. No technical team."}
            </p>
            <button type="button" onClick={() => setApplyOpen(true)} className="btn-mint px-8">
              {isES ? "Abrir formulario — gratis" : "Open form — free"}
            </button>
            <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-8">
              {isES ? "¿Prefieres email? " : "Prefer email? "}
              <a href="mailto:hello@cli-market.dev?subject=CLI%20Market%20Retailer%20Listing" className="text-[var(--cm-mint)] underline">
                hello@cli-market.dev
              </a>
            </p>
          </motion.div>
        </section>

        <RetailerApplyModal open={applyOpen} onClose={() => setApplyOpen(false)} />

        <Footer />
      </div>
    </main>
  );
}
