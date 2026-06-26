"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { recordPipInstallIntent } from "@/lib/funnel";
import { PRODUCT_DOORS } from "@/lib/productDoors";
import { CTA } from "@/lib/ctaCopy";
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
        ? `${MARKET_STATS.pricesVerifiedLabel} precios verificados`
        : `${MARKET_STATS.pricesVerifiedLabel} verified prices`,
    },
    {
      label: isES
        ? `${MARKET_STATS.retailersVerified} retailers`
        : `${MARKET_STATS.retailersVerified} retailers`,
    },
    {
      label: isES ? "MCP · Cursor · Claude · VS Code" : "MCP · Cursor · Claude · VS Code",
    },
  ];

  return (
    <section
      id="hero"
      className="landing-section animate-fade-in relative overflow-hidden"
      style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}
    >
      <HeroBackground />
      <div className="landing-container-wide pt-10 pb-6 sm:pt-14 sm:pb-10 relative z-10">
        <div className="flex flex-col lg:flex-row lg:items-start lg:gap-12 xl:gap-16">
          <div className="flex-1 min-w-0">
            <motion.span
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="inline-flex mb-4 stripe-tag-soft"
            >
              {isES ? "INTELIGENCIA DE PRECIOS RETAIL EN LATAM" : "LATAM RETAIL PRICE INTELLIGENCE"}
            </motion.span>

            <motion.h1
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="hero-garamond-headline max-w-[620px] text-balance"
            >
              {isES ? (
                <>
                  <span className="text-[var(--cm-on-surface)]">Precios verificados para </span>
                  <span className="text-gradient-orange">construir</span>
                  <span className="text-[var(--cm-on-surface-variant)]">, comprar y </span>
                  <span className="text-gradient-orange">analizar</span>
                </>
              ) : (
                <>
                  <span className="text-[var(--cm-on-surface)]">Verified prices to </span>
                  <span className="text-gradient-orange">build</span>
                  <span className="text-[var(--cm-on-surface-variant)]">, buy, and </span>
                  <span className="text-gradient-orange">analyze</span>
                </>
              )}
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
              className="mt-4 text-base sm:text-lg max-w-[500px] leading-relaxed text-[var(--cm-on-surface-variant)]"
            >
              {isES
                ? "Tres puertas sobre la misma data verificada — elige la tuya."
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
                    className="text-xs font-mono text-[var(--cm-on-surface-variant)] bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-full px-3 py-1"
                  >
                    {chip.label}
                  </span>
                ))}
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.22 }}
              className="flex flex-wrap gap-3 mt-6"
            >
              <a
                href={CTA.getApiKey.href}
                className="btn-mint"
                onClick={() => recordPipInstallIntent("landing_hero_cta")}
              >
                {isES ? CTA.getApiKey.es : CTA.getApiKey.en}
              </a>
              <a href={CTA.watchDemo.href} className="btn-outline">
                {isES ? CTA.watchDemo.es : CTA.watchDemo.en}
              </a>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.65, delay: 0.28, ease: "easeOut" }}
            className="flex-1 min-w-0 mt-10 lg:mt-0 lg:max-w-md xl:max-w-lg"
          >
            <div className="flex flex-col gap-4">
              {PRODUCT_DOORS.map((door) => (
                <ProductDoorCard
                  key={door.id}
                  door={door}
                  isES={isES}
                  compact
                  onClick={
                    door.id === "build"
                      ? () => recordPipInstallIntent("landing_hero_door_build")
                      : undefined
                  }
                />
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
