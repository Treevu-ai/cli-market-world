"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { CTA } from "@/lib/ctaCopy";

export default function FinalCTASection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });

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
              ? <>¿Listo para <span className="text-gradient-orange">empezar</span>?</>
              : <>Ready to <span className="text-gradient-orange">get started</span>?</>}
          </h2>
          <p className="section-intro">
            {isES
              ? "Elige cómo quieres usar los precios."
              : "Choose how you want to use the prices."}
          </p>

          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <a href={CTA.getApiKey.href} className="btn-mint text-base px-8 py-3">
              {isES ? CTA.getApiKey.es : CTA.getApiKey.en}
            </a>
            <a href={CTA.contact.href} className="btn-outline text-base px-8 py-3">
              {isES ? CTA.contact.es : CTA.contact.en}
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
