"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { recordIcpDoorClick, recordPipInstallIntent } from "@/lib/funnel";
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

  const handleDoorClick = (doorId: (typeof PRODUCT_DOORS)[number]["id"]) => {
    recordIcpDoorClick(doorId, "hub");
    if (doorId === "build") {
      recordPipInstallIntent("landing_hub_door_build");
    }
  };

  return (
    <section
      id="hero"
      className="landing-section animate-fade-in relative overflow-hidden"
      style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}
    >
      <HeroBackground />
      <div className="landing-container-wide hero-inner pt-4 pb-10 sm:pt-6 sm:pb-12 lg:py-8 relative z-10">
        <div className="max-w-3xl text-left">
          <motion.span
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="inline-flex mb-4 stripe-tag-soft"
          >
            {isES ? "INFRAESTRUCTURA DE COMERCIO PARA AGENTES DE IA" : "COMMERCE INFRASTRUCTURE FOR AI AGENTS"}
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="hero-garamond-headline text-balance"
          >
            {isES ? (
              <>
                <span className="text-[var(--cm-on-surface)]">Precios verificados. </span>
                <span className="text-gradient-orange">Hechos para que los use un agente.</span>
              </>
            ) : (
              <>
                <span className="text-[var(--cm-on-surface)]">Verified prices. </span>
                <span className="text-gradient-orange">Built for an agent to use.</span>
              </>
            )}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
            className="mt-4 text-base sm:text-lg max-w-[540px] leading-relaxed text-[var(--cm-on-surface-variant)]"
          >
            {isES
              ? "CLI, API y MCP sobre una sola capa de datos verificada. Elige cómo construyes, compras o analizas."
              : "CLI, API, and MCP over one verified data layer. Choose how you build, buy, or analyze."}
          </motion.p>

          {mounted && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.16 }}
              className="mt-4 flex flex-wrap justify-start gap-2"
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
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, delay: 0.22, ease: "easeOut" }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-10 max-w-5xl"
        >
          {PRODUCT_DOORS.map((door) => (
            <ProductDoorCard
              key={door.id}
              door={door}
              isES={isES}
              onClick={() => handleDoorClick(door.id)}
            />
          ))}
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-8 text-left text-sm text-[var(--cm-on-surface-variant)]"
        >
          {isES ? "¿Vendes en retail? " : "Sell retail? "}
          <a
            href={CTA.forRetailers.href}
            className="font-semibold text-[var(--cm-mint)] hover:underline"
            onClick={() => recordIcpDoorClick("retailers", "hub")}
          >
            {isES ? "Indexa tu catálogo gratis →" : "List your catalog free →"}
          </a>
        </motion.p>
      </div>
    </section>
  );
}
