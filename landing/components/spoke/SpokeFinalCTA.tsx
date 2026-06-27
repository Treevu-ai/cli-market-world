"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { SPOKE_FINAL_CTA, type SpokeIcp } from "@/lib/spokeConfig";

type SpokeFinalCTAProps = {
  icp: SpokeIcp;
};

export default function SpokeFinalCTA({ icp }: SpokeFinalCTAProps) {
  const { lang } = useLang();
  const isES = lang === "es";
  const config = SPOKE_FINAL_CTA[icp];
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });

  const primaryLabel = isES ? config.primaryCta.es : config.primaryCta.en;
  const secondary = config.secondaryCta;
  const secondaryLabel = secondary ? (isES ? secondary.es : secondary.en) : null;

  return (
    <section
      ref={ref}
      id={config.id}
      className="landing-section scroll-mt-24"
      style={{
        background:
          "linear-gradient(160deg, rgba(234,88,12,0.12) 0%, var(--cm-surface-low) 50%, var(--cm-background) 100%)",
        borderTop: "1px solid rgba(234,88,12,0.2)",
      }}
    >
      <div className="landing-container-wide text-center">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="inline-flex mb-4 stripe-tag-soft">
            {isES ? config.eyebrow_es : config.eyebrow_en}
          </span>

          <h2 className="section-title">
            <span className="text-[var(--cm-on-surface)]">
              {isES ? config.titleBefore_es : config.titleBefore_en}
            </span>
            <span className="text-gradient-orange">
              {isES ? config.titleAccent_es : config.titleAccent_en}
            </span>
            {(isES ? config.titleAfter_es : config.titleAfter_en) ? (
              <span className="text-[var(--cm-on-surface)]">
                {isES ? config.titleAfter_es : config.titleAfter_en}
              </span>
            ) : null}
          </h2>

          <p className="section-intro">{isES ? config.body_es : config.body_en}</p>

          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <a href={config.primaryCta.href} className="btn-mint text-base px-8 py-3">
              {primaryLabel}
            </a>
            {secondary && secondaryLabel ? (
              <a href={secondary.href} className="btn-outline text-base px-8 py-3">
                {secondaryLabel}
              </a>
            ) : null}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
