"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { PRODUCT_DOORS } from "@/lib/productDoors";
import { PROCURE_SITE_URL } from "@/lib/procurePlans";
import { CTA } from "@/lib/ctaCopy";

export default function FinalCTASection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });

  const doors = [
    {
      label: isES ? "Build" : "Build",
      title: isES ? "Integra en tu stack" : "Integrate into your stack",
      href: PRODUCT_DOORS[0].href,
      cta: isES ? PRODUCT_DOORS[0].cta_es : PRODUCT_DOORS[0].cta_en,
      external: false,
    },
    {
      label: isES ? "Procure" : "Procure",
      title: isES ? "Compra para tu empresa" : "Buy for your business",
      href: `${PROCURE_SITE_URL}/procure`,
      cta: isES ? "Ver Procure →" : "See Procure →",
      external: true,
    },
    {
      label: "Intelligence",
      title: isES ? "Piloto de datos" : "Data pilot",
      href: "/contact#contact-intelligence",
      cta: isES ? "Solicitar piloto →" : "Request pilot →",
      external: false,
    },
  ];

  return (
    <section
      ref={ref}
      id="final-cta"
      className="landing-section scroll-mt-24"
      style={{ background: "linear-gradient(160deg, #fff7f0 0%, #fff5ed 50%, #fef3ea 100%)", borderTop: "1px solid rgba(234,88,12,0.12)" }}
    >
      <div className="landing-container-wide text-center">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <h2 className="section-title">
            {isES
              ? <>Elige tu puerta a la <span className="text-gradient-orange">misma data</span></>
              : <>Pick your door to the <span className="text-gradient-orange">same data</span></>}
          </h2>
          <p className="section-intro">
            {isES
              ? "Sin mezclar audiencias. Cada producto resuelve un job distinto sobre precios verificados de LATAM."
              : "No mixed audiences. Each product solves a different job on verified LATAM prices."}
          </p>

          <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left max-w-4xl mx-auto">
            {doors.map((door) => (
              <a
                key={door.label}
                href={door.href}
                className="card-cyber rounded-xl p-5 hover:shadow-md transition-all border border-[#e2e8f0] hover:border-[#ea580c]/30"
                {...(door.external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
              >
                <p className="text-[10px] font-bold uppercase tracking-widest text-[#ea580c]">{door.label}</p>
                <p className="mt-2 text-sm font-semibold text-[#0f172a]">{door.title}</p>
                <p className="mt-3 text-sm font-semibold text-[#ea580c]">{door.cta}</p>
              </a>
            ))}
          </div>

          <div className="mt-8">
            <a href={CTA.bookDemo.href} className="btn-outline text-base px-8 py-3">
              {isES ? CTA.bookDemo.es : CTA.bookDemo.en}
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
