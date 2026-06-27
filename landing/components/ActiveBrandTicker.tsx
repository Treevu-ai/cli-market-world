"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { ACTIVE_BRAND_NAMES } from "@/lib/activeBrands";
import { MARKET_STATS } from "@/lib/marketStats";

const INTERVAL_MS = 2800;

export default function ActiveBrandTicker() {
  const { lang } = useLang();
  const isES = lang === "es";
  const brands = ACTIVE_BRAND_NAMES;
  const [index, setIndex] = useState(0);
  const [reduceMotion, setReduceMotion] = useState(true);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduceMotion(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    if (reduceMotion || brands.length <= 1) return;
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % brands.length);
    }, INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [reduceMotion, brands.length]);

  const current = brands[index] ?? brands[0];

  return (
    <div
      className="price-ticker brand-ticker brand-mode-terminal"
      role="status"
      aria-live="polite"
      aria-label={
        isES
          ? `Marcas activas en CLI Market: ${current}`
          : `Active brands on CLI Market: ${current}`
      }
    >
      <div className="brand-ticker-inner">
        <span className="brand-ticker-label">
          {isES ? "Activo en CLI Market" : "Live on CLI Market"}
        </span>
        <span className="price-ticker-sep" aria-hidden="true">
          ·
        </span>
        <span className="brand-ticker-name">
          {reduceMotion ? (
            current
          ) : (
            <AnimatePresence mode="wait">
              <motion.span
                key={current}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.35, ease: "easeOut" }}
                className="inline-block"
              >
                {current}
              </motion.span>
            </AnimatePresence>
          )}
        </span>
        <span className="price-ticker-sep hidden sm:inline" aria-hidden="true">
          ·
        </span>
        <span className="brand-ticker-meta hidden sm:inline">
          {isES
            ? `${MARKET_STATS.retailersVerified} retailers verificados`
            : `${MARKET_STATS.retailersVerified} verified retailers`}
        </span>
      </div>
    </div>
  );
}
