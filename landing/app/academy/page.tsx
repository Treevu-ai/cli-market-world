"use client";

import { motion } from "framer-motion";
import AcademyRegisterForm from "@/components/AcademyRegisterForm";

const VALUE_CARDS = [
  {
    idx: "01",
    title: "Pricing en tiempo real",
    body: "Si fijas precio copiando a tu competencia, ya perdiste. Compara contra 37+ retailers en 9 países y decide con evidencia, no con copy-paste.",
  },
  {
    idx: "02",
    title: "Oportunidades de crecimiento",
    body: 'Mientras tú "sientes" que hay un vacío en el mercado, alguien más ya lo está midiendo. Detéctalo antes de que lo ocupen.',
  },
  {
    idx: "03",
    title: "Inteligencia competitiva y de marketing",
    body: "Ese descuento de tu competencia probablemente es falso. Deja de reaccionar a promociones infladas — detéctalas.",
  },
  {
    idx: "04",
    title: "Compras y proveedores optimizados",
    body: "Comprar por costumbre te está costando margen. Señales claras de cuándo comprar y con quién — no por default.",
  },
];

const LOGISTICS = [
  { label: "Fecha", val: "Jueves 16 de mayo", sub: "confirmar año" },
  { label: "Hora", val: "7:00 PM", sub: "Hora Perú (GMT-5)" },
  { label: "Duración", val: "2 horas", sub: "sesión única" },
  { label: "Modalidad", val: "100% online", sub: "en vivo vía Zoom" },
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
              compras — en una sola sesión.
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

      {/* Value cards */}
      <section className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide py-12 sm:py-16">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {VALUE_CARDS.map((card) => (
              <div key={card.idx} className="card-cyber p-6">
                <div className="text-xs font-mono text-[var(--cm-mint)] mb-2">{card.idx}</div>
                <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-2">{card.title}</h3>
                <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">{card.body}</p>
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
              <span className="text-xs font-mono text-[var(--cm-mint)] border border-[var(--cm-mint)]/30 rounded-full px-3 py-1 inline-block">
                ◆ PRO ACCESS
              </span>
            </div>
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
