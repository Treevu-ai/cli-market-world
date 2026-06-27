"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { RETAILERS_BENEFITS_SECTION } from "@/lib/retailersSpokeContent";

export default function RetailersBenefitsSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const { eyebrow_es, eyebrow_en, title_es, title_en, benefits } = RETAILERS_BENEFITS_SECTION;

  return (
    <section ref={ref} className="landing-section scroll-mt-24">
      <div className="landing-container-wide">
        <motion.div
          className="landing-section-header text-center"
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="section-eyebrow mb-4">{isES ? eyebrow_es : eyebrow_en}</p>
          <h2 className="section-title">{isES ? title_es : title_en}</h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
          {benefits.map((b, i) => (
            <motion.div
              key={b.title_en}
              className="card-cyber rounded-2xl p-6"
              initial={{ opacity: 0, y: 16 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: 0.1 + i * 0.08 }}
            >
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-2">
                {isES ? b.title_es : b.title_en}
              </h3>
              <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                {isES ? b.body_es : b.body_en}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
