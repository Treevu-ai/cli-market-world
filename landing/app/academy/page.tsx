"use client";

import { motion } from "framer-motion";
import AcademyRegisterForm from "@/components/AcademyRegisterForm";

const AUDIENCE = [
  {
    title: "Pricing / trade marketing",
    body: "Necesitas saber cómo se ve tu marca frente a la competencia, retailer por retailer — no solo el precio que te reporta el proveedor.",
  },
  {
    title: "Category / compras",
    body: "Decides dónde y cuándo comprar la canasta recurrente del negocio — retail, F&B, hotelería, oficinas.",
  },
  {
    title: "Growth / marketing",
    body: "Quieres detectar vacíos de mercado y promociones infladas de la competencia antes que reaccionar tarde.",
  },
];

const LIVE_FLOWS = [
  {
    idx: "01",
    title: "Pricing",
    prompt: "“Tengo un serum facial a S/45, ¿cómo está posicionado frente al mercado en Lima?”",
    tools: "market_search → market_compare → market_price_history",
    payoff: "Banda de precio competitiva y si conviene subir o bajar.",
  },
  {
    idx: "02",
    title: "Growth",
    prompt: "“¿Qué categoría tiene un vacío entre S/40 y S/90 que nadie cubre bien?”",
    tools: "market_trending → market_scores → market_intel_brief",
    payoff: "Oportunidad de producto o categoría con evidencia, no intuición.",
  },
  {
    idx: "03",
    title: "Marketing / competencia",
    prompt: "“Mi competencia bajó su precio, ¿es un descuento real o inflado?”",
    tools: "market_promo_detector → market_retailer_scorecard",
    payoff: "Cómo responder en comunicación o pricing, con evidencia.",
  },
  {
    idx: "04",
    title: "Compras / timing",
    prompt: "“Necesito comprar insumos este mes, ¿compro ahora o espero?”",
    tools: "market_procurement_signal → market_price_risk → market_optimize_purchase",
    payoff: "Decisión de timing y ahorro cuantificado.",
  },
];

const HONESTY = [
  { label: "Sí hace", val: "Mide retail formal online — VTEX, Shopify, Magento, WooCommerce — refrescado cada 4 horas." },
  { label: "No hace", val: "No reemplaza el IPC oficial ni cubre ferias o mercados informales — y lo decimos en cada respuesta." },
];

const LOGISTICS = [
  { label: "Fecha", val: "Jueves 16 de mayo", sub: "confirmar año" },
  { label: "Hora", val: "7:00 PM", sub: "Hora Perú (GMT-5)" },
  { label: "Duración", val: "2 horas", sub: "sesión única, en vivo" },
  { label: "Cupo", val: "20 personas", sub: "grupo reducido, con tu caso" },
];

const FAQS = [
  {
    q: "¿Y si no puedo asistir en vivo?",
    a: "Queda grabado. Te llega el link de la grabación aunque no puedas conectarte a las 7:00 PM.",
  },
  {
    q: "¿Por qué solo 20 cupos?",
    a: "Porque en varios bloques trabajamos con tu propio precio o tu propia categoría, no un ejemplo genérico — un grupo grande no permite eso.",
  },
  {
    q: "¿Qué pasa después del mes de CLI Market PRO?",
    a: "Nada automático: no se renueva solo ni hay compromiso posterior. Si quieres seguir usándolo, la decisión es tuya.",
  },
  {
    q: "¿Necesito saber programar o usar IA?",
    a: "No. La sesión se dicta en lenguaje de negocio — el foco es la decisión que tomas con el dato, no la herramienta.",
  },
];

export default function AcademyPage() {
  return (
    <main className="bg-[var(--cm-canvas)]">
      {/* Hero */}
      <section
        id="academy-hero"
        className="landing-section relative overflow-hidden"
        style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}
      >
        <div className="landing-container-wide hero-inner pt-10 pb-12 sm:pt-14 sm:pb-16 relative z-10">
          <div className="max-w-3xl text-left">
            <motion.span
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="inline-flex mb-4 stripe-tag-soft"
            >
              Inteligencia que transforma
            </motion.span>

            <motion.h1
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="hero-garamond-headline text-balance"
            >
              <span className="text-[var(--cm-on-surface)]">TU PRECIO NO ES UNA OPINIÓN. </span>
              <span className="text-gradient-orange">ES UN DATO.</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
              className="mt-4 text-base sm:text-lg max-w-[560px] leading-relaxed text-[var(--cm-on-surface-variant)]"
            >
              Mientras tú decides por intuición, alguien más ya está comparando tu precio, vigilando tu categoría
              y comprando mejor que tú. Este taller te da las mismas herramientas — pricing, growth, marketing y
              compras — en una sola sesión, con tu propio caso corriendo en vivo.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.16 }}
              className="mt-6 flex flex-wrap justify-start gap-2"
            >
              <span className="text-xs font-mono text-[var(--cm-on-surface-variant)] bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-full px-3 py-1">
                ● LIVE · VÍA ZOOM
              </span>
              <span className="text-xs font-mono text-[var(--cm-on-surface-variant)] bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-full px-3 py-1">
                37+ RETAILERS · 9 PAÍSES · CADA 4H
              </span>
              <span className="text-xs font-mono text-[var(--cm-on-surface-variant)] bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-full px-3 py-1">
                SOLO 20 CUPOS
              </span>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.24 }}
              className="mt-8"
            >
              <a href="#academy-register" className="btn-mint inline-block">
                Deja de adivinar →
              </a>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Audience qualification */}
      <section className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide py-12 sm:py-16">
          <span className="stripe-tag-soft inline-flex mb-4">Es para ti si...</span>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {AUDIENCE.map((item) => (
              <div key={item.title} className="card-cyber p-6">
                <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-2">{item.title}</h3>
                <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Live agenda — real flows from the runsheet */}
      <section className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide py-12 sm:py-16">
          <span className="stripe-tag-soft inline-flex mb-4">Lo que corre en vivo</span>
          <h2 className="text-xl sm:text-2xl font-semibold text-[var(--cm-on-surface)] mb-2">
            4 flujos reales, no funciones sueltas
          </h2>
          <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-2xl mb-8 leading-relaxed">
            Cada bloque parte de una pregunta de negocio, muestra qué herramienta llama el agente y en qué orden,
            y termina en una decisión accionable — con tu propio precio o categoría cuando aplica.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {LIVE_FLOWS.map((flow) => (
              <div key={flow.idx} className="card-cyber p-6">
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-xs font-mono text-[var(--cm-mint)]">{flow.idx}</span>
                  <h3 className="text-base font-semibold text-[var(--cm-on-surface)]">{flow.title}</h3>
                </div>
                <p className="text-sm text-[var(--cm-on-surface)] italic leading-relaxed mb-3">{flow.prompt}</p>
                <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] mb-3 break-words">{flow.tools}</p>
                <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">{flow.payoff}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Facilitator */}
      <section className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide py-12 sm:py-16">
          <div className="card-cyber p-8 max-w-2xl">
            <span className="stripe-tag-soft inline-flex mb-3">Facilitador</span>
            <h2 className="text-xl font-semibold text-[var(--cm-on-surface)] mb-2">Ricardo Cuba Alván</h2>
            <p className="text-sm text-[var(--cm-on-surface)] font-medium mb-1">
              Fundador de CLI Market y Procure Copilot — inteligencia de precios y compras para LATAM
            </p>
            <p className="text-sm text-[var(--cm-on-surface-variant)] mb-4">Gerente de Sinapsis Innovadora</p>
            <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
              Especialista en inteligencia de mercados aplicada a pricing, growth, marketing y compras — para
              quienes ya no quieren decidir a ciegas.
            </p>
          </div>
        </div>
      </section>

      {/* Honesty / differentiation */}
      <section className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide py-12 sm:py-16">
          <span className="stripe-tag-soft inline-flex mb-4">Sin humo</span>
          <h2 className="text-xl sm:text-2xl font-semibold text-[var(--cm-on-surface)] mb-6">
            Qué sí hace, qué no hace — te lo decimos antes de que preguntes
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {HONESTY.map((item) => (
              <div key={item.label} className="card-cyber p-6">
                <div className="text-xs font-mono uppercase tracking-wide text-[var(--cm-mint)] mb-2">
                  {item.label}
                </div>
                <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">{item.val}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Logistics + pricing */}
      <section className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide py-12 sm:py-16">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
            {LOGISTICS.map((item) => (
              <div key={item.label} className="card-cyber p-5">
                <div className="text-xs font-mono uppercase tracking-wide text-[var(--cm-on-surface-variant)] mb-1">
                  {item.label}
                </div>
                <div className="text-lg font-semibold text-[var(--cm-on-surface)]">{item.val}</div>
                <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{item.sub}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl">
            <div className="card-cyber p-6">
              <span className="stripe-tag-soft inline-flex mb-3">Inversión</span>
              <div className="text-3xl font-semibold text-[var(--cm-on-surface)]">
                US$ 49 <small className="text-base font-normal text-[var(--cm-on-surface-variant)]">≈ S/ 185</small>
              </div>
              <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">tipo de cambio referencial</div>
            </div>
            <div className="card-cyber p-6">
              <div className="text-xs font-mono uppercase tracking-wide text-[var(--cm-on-surface-variant)] mb-1">
                Incluye
              </div>
              <div className="text-base font-semibold text-[var(--cm-on-surface)] mb-2">
                1 mes de uso de CLI Market PRO
              </div>
              <p className="text-xs text-[var(--cm-on-surface-variant)] mb-2 leading-relaxed">
                Sin renovación automática ni compromiso posterior — si sigues, es tu decisión.
              </p>
              <span className="text-xs font-mono text-[var(--cm-mint)] border border-[var(--cm-mint)]/30 rounded-full px-3 py-1 inline-block">
                ◆ PRO ACCESS
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide py-12 sm:py-16">
          <div className="text-center mb-8">
            <span className="stripe-tag-soft inline-flex mb-3">FAQ</span>
            <h2 className="text-2xl sm:text-3xl font-semibold text-[var(--cm-on-surface)]">Preguntas frecuentes</h2>
          </div>
          <div className="max-w-2xl mx-auto space-y-0">
            {FAQS.map((faq, i) => (
              <details
                key={faq.q}
                className="group border-b border-[var(--cm-outline-variant)]/30 py-1"
                {...(i === 0 ? { open: true } : {})}
              >
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-5 text-base font-medium text-[var(--cm-on-surface)] marker:content-none [&::-webkit-details-marker]:hidden">
                  <span className="text-left">{faq.q}</span>
                  <span
                    className="shrink-0 text-[var(--cm-mint)] text-lg leading-none transition-transform duration-200 group-open:rotate-45"
                    aria-hidden
                  >
                    +
                  </span>
                </summary>
                <p className="pb-5 text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">{faq.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Registration */}
      <section id="academy-register" className="landing-section">
        <div className="landing-container-wide py-14 sm:py-20">
          <div className="text-center mb-8">
            <span className="stripe-tag-soft inline-flex mb-3">Registro</span>
            <h2 className="text-2xl sm:text-3xl font-semibold text-[var(--cm-on-surface)]">Reserva tu lugar</h2>
          </div>
          <AcademyRegisterForm />
          <p className="text-center text-sm text-[var(--cm-on-surface-variant)] mt-8">
            cli-market.dev · hello@cli-market.dev · WhatsApp 902 126 765
          </p>
        </div>
      </section>
    </main>
  );
}
