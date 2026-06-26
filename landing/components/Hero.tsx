"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { recordPipInstallIntent } from "@/lib/funnel";
import { PRODUCT_DOORS } from "@/lib/productDoors";
import ProductDoorCard from "@/components/ProductDoorCard";
import HeroBackground from "@/components/HeroBackground";

export default function Hero() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  const proofChips = [
    {
      label: isES
        ? `${MARKET_STATS.retailersVerified} retailers verificados`
        : `${MARKET_STATS.retailersVerified} verified retailers`,
    },
    {
      label: isES
        ? `${MARKET_STATS.pricesVerifiedLabel} precios normalizados`
        : `${MARKET_STATS.pricesVerifiedLabel} normalized prices`,
    },
    {
      label: isES
        ? `${MARKET_STATS.countries} países LATAM`
        : `${MARKET_STATS.countries} LATAM countries`,
    },
    {
      label: isES
        ? `Refresh cada ${MARKET_STATS.pricesRefreshHours}h`
        : `${MARKET_STATS.pricesRefreshHours}h refresh cycle`,
    },
  ];

  return (
    <section
      id="hero"
      className="landing-section animate-fade-in relative overflow-hidden hero-stripe-mesh"
      style={{ borderBottom: "1px solid #e2e8f0" }}
    >
      <HeroBackground />
      <div className="landing-container-wide pt-16 pb-12 sm:pt-20 sm:pb-16 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mb-4 stripe-tag-soft inline-flex"
        >
          {isES ? "INTELIGENCIA DE PRECIOS RETAIL EN LATAM" : "LATAM RETAIL PRICE INTELLIGENCE"}
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="hero-garamond-headline max-w-[820px]"
        >
          {isES ? (
            <>
              Precios verificados para{" "}
              <span className="text-gradient-orange">construir</span>, comprar y{" "}
              <span className="text-gradient-orange">analizar</span>
            </>
          ) : (
            <>
              Verified prices to{" "}
              <span className="text-gradient-orange">build</span>, buy, and{" "}
              <span className="text-gradient-orange">analyze</span>
            </>
          )}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
          className="mt-4 text-base sm:text-lg max-w-[640px] leading-relaxed stripe-body"
        >
          {isES
            ? "Tres productos sobre la misma data verificada — elige tu puerta."
            : "Three products on one verified data layer — pick your door."}
        </motion.p>

        {mounted && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.16 }}
            className="mt-4 flex flex-wrap gap-2"
          >
            {proofChips.map((chip, i) => (
              <span
                key={i}
                className="text-xs font-mono text-[#64748b] bg-[#f1f5f9] border border-[#e2e8f0] rounded-full px-3 py-1"
              >
                {chip.label}
              </span>
            ))}
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, delay: 0.22 }}
          className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-5"
        >
          {PRODUCT_DOORS.map((door) => (
            <ProductDoorCard
              key={door.id}
              door={door}
              isES={isES}
              onClick={
                door.id === "build"
                  ? () => recordPipInstallIntent("landing_hero_door_build")
                  : undefined
              }
            />
          ))}
        </motion.div>
      </div>
    </section>
  );
}
