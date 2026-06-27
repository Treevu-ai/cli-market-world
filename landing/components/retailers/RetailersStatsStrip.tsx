"use client";

import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { RETAILERS_STATS } from "@/lib/retailersSpokeContent";

export default function RetailersStatsStrip() {
  const { lang } = useLang();
  const isES = lang === "es";
  const stats = RETAILERS_STATS(isES);

  return (
    <section className="landing-section landing-section-alt scroll-mt-24">
      <div className="landing-container-wide">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-40px" }}
          transition={{ duration: 0.45, ease: "easeOut" }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center max-w-[720px] mx-auto"
        >
          {stats.map((s) => (
            <div key={s.l}>
              <div className="text-3xl font-black text-[var(--cm-mint)] tabular-nums">{s.n}</div>
              <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{s.l}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
