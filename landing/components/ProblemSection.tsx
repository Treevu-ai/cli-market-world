"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";

export default function ProblemSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  const cards = [
    {
      title: isES ? "Precios que no se pueden comparar" : "Prices you can't actually compare",
      body: isES
        ? "Cada tienda usa presentaciones, unidades y categorías distintas. Comparar S/ 4.90 de 900 g contra S/ 5.20 de 1 kg a mano es lento y propenso a errores."
        : "Every store uses different pack sizes, units, and categories. Manually comparing S/ 4.90 for 900 g vs S/ 5.20 for 1 kg is slow and error-prone.",
    },
    {
      title: isES ? "Horas perdidas cada semana" : "Hours lost every week",
      body: isES
        ? "Los equipos de compras invierten entre 4 y 8 horas semanales cotizando en múltiples tiendas, actualizando hojas de cálculo y persiguiendo aprobaciones."
        : "Procurement teams spend 4–8 hours a week quoting across stores, updating spreadsheets, and chasing approvals.",
    },
    {
      title: isES ? "Sin visibilidad ni control" : "No visibility or control",
      body: isES
        ? "Sin historial de precios, sin alertas de subida, sin trazabilidad de quién aprobó qué. Las decisiones de compra quedan opacas para la gerencia."
        : "No price history, no spike alerts, no audit trail of who approved what. Purchasing decisions remain opaque to management.",
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
              ? "Comprar bien no debería costar tanto tiempo"
              : "Buying smart shouldn't cost so much time"}
          </h2>
          <p className="section-intro text-[#64748b]">
            {isES
              ? "Los equipos de compras de LATAM comparan precios a mano, en múltiples tiendas, cada semana. Con datos que cambian cada pocas horas. Sin automatización que los ayude."
              : "LATAM procurement teams compare prices manually, across multiple stores, every week — with data that changes every few hours and no automation to help."}
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
