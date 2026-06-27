"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import type { SpokeStepContent } from "@/lib/retailersSpokeContent";

type SpokeStepsSectionProps = {
  id?: string;
  eyebrow_es: string;
  eyebrow_en: string;
  title_es: string;
  title_en: string;
  intro_es?: string;
  intro_en?: string;
  steps: SpokeStepContent[];
  altBackground?: boolean;
};

export default function SpokeStepsSection({
  id = "steps",
  eyebrow_es,
  eyebrow_en,
  title_es,
  title_en,
  intro_es,
  intro_en,
  steps,
  altBackground = false,
}: SpokeStepsSectionProps) {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section
      ref={ref}
      id={id}
      className={`landing-section scroll-mt-24${altBackground ? " landing-section-alt" : ""}`}
    >
      <div className="landing-container-wide">
        <motion.div
          className="landing-section-header text-center"
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="section-eyebrow mb-4">{isES ? eyebrow_es : eyebrow_en}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES ? title_es : title_en}
          </h2>
          {(intro_es || intro_en) && (
            <p className="section-intro">{isES ? intro_es : intro_en}</p>
          )}
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
          {steps.map((step, i) => (
            <motion.div
              key={step.n}
              className="card-cyber rounded-2xl p-6"
              initial={{ opacity: 0, y: 32 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.55, delay: 0.1 + i * 0.1, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="flex items-center gap-3 mb-4">
                <span
                  className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-xs font-bold text-white"
                  style={{ background: "linear-gradient(180deg, #f97316 0%, #ea580c 100%)" }}
                >
                  {step.n}
                </span>
                <h3 className="text-base font-semibold text-[var(--cm-on-surface)]">
                  {isES ? step.title_es : step.title_en}
                </h3>
              </div>
              <p className="text-sm leading-relaxed text-[var(--cm-on-surface-variant)]">
                {isES ? step.body_es : step.body_en}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
