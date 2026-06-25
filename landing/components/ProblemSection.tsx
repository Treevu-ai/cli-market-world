"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function ProblemSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  const cards = [
    {
      title: isES
        ? "Los agentes IA no tienen precios reales"
        : "AI agents don't have real prices",
      body: isES
        ? "Los modelos alucinan precios, usan datos de entrenamiento de meses atrás o llaman a endpoints que no existen. Necesitan una fuente de verdad verificada y actualizada en tiempo real."
        : "Models hallucinate prices, use training data from months ago, or call endpoints that don't exist. They need a verified, real-time source of truth.",
    },
    {
      title: isES
        ? `${MARKET_STATS.retailersDefined} retailers, cada uno con su propio formato`
        : `${MARKET_STATS.retailersDefined} retailers, each with their own format`,
      body: isES
        ? `${MARKET_STATS.retailersVerified} activos en ${MARKET_STATS.countries} países: SKUs distintos, unidades mezcladas, categorías incompatibles. Normalizar eso desde cero toma 18 meses — y todavía se rompe.`
        : `${MARKET_STATS.retailersVerified} active across ${MARKET_STATS.countries} countries: different SKUs, mixed units, incompatible categories. Normalizing that from scratch takes 18 months — and still breaks.`,
    },
    {
      title: isES
        ? "El precio solo no es suficiente contexto"
        : "Price alone isn't enough context",
      body: isES
        ? "S/ 5.20/kg no le dice nada a un agente. Necesita saber si es caro vs. el mes pasado, si hay stock, si hay una alternativa más barata y si el precio va a subir mañana."
        : "S/ 5.20/kg tells an agent nothing. It needs to know if that's expensive vs. last month, whether there's stock, if there's a cheaper alternative, and if the price is about to spike.",
    },
  ];

  return (
    <section
      ref={ref}
      id="problem"
      className="landing-section scroll-mt-24"
      style={{ backgroundColor: "#f8fafc" }}
    >
      <div className="landing-container-wide text-center">
        <motion.div
          className="landing-section-header"
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <h2 className="section-title text-[#0f172a]">
            {isES
              ? "Los agentes IA necesitan datos de comercio reales"
              : "AI agents need real commerce data"}
          </h2>
          <p className="section-intro text-[#64748b]">
            {isES
              ? `Construir sobre precios inventados o de entrenamiento no funciona. CLI Market es la capa de infraestructura que conecta a tus agentes con ${MARKET_STATS.pricesVerifiedLabel} precios verificados de góndola, normalizados y frescos.`
              : `Building on hallucinated or stale training prices doesn't work. CLI Market is the infrastructure layer that connects your agents to ${MARKET_STATS.pricesVerifiedLabel} verified shelf prices, normalized and fresh.`}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
          {cards.map((card, i) => (
            <motion.div
              key={i}
              className="card-cyber rounded-2xl p-6 text-left"
              initial={{ opacity: 0, y: 32 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.55, delay: 0.1 + i * 0.08, ease: [0.16, 1, 0.3, 1] }}
            >
              <h3 className="text-base font-semibold text-[#0f172a] mb-3">{card.title}</h3>
              <p className="text-sm leading-relaxed text-[#64748b]">{card.body}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
