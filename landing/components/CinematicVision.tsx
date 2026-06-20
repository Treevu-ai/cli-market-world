"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { EditorialSection } from "@/components/EditorialSection";

export default function CinematicVision() {
  const textRef = useRef<HTMLDivElement>(null);
  const { lang } = useLang();
  const isES = lang === "es";

  useEffect(() => {
    const text = textRef.current;
    if (!text) return;

    gsap.set(text, { opacity: 0, y: 32 });

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            gsap.to(text, { opacity: 1, y: 0, duration: 1, ease: "power3.out" });
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 },
    );

    observer.observe(text);
    return () => observer.disconnect();
  }, []);

  return (
    <EditorialSection
      id="infrastructure"
      eyebrow={isES ? "Infraestructura" : "Infrastructure"}
      variant="muted"
    >
      <div ref={textRef} className="landing-editorial-split">
        <h2 className="landing-editorial-split__title">
          {isES
            ? "Precios verificados. Sin scraping. Para agentes."
            : "Verified prices. Zero scraping. For agents."}
        </h2>
        <p className="landing-editorial-split__body">
          {isES
            ? `CLI Market normaliza precios por kg/L en ${MARKET_STATS.retailersVerified} retailers de ${MARKET_STATS.countries} países. Cada price point pasa por validación de calidad — sin valores atípicos, sin precios stale. Tu agente recibe datos limpios, listos para comparar canastas o disparar flujos de procurement.`
            : `CLI Market normalizes prices per kg/L across ${MARKET_STATS.retailersVerified} retailers in ${MARKET_STATS.countries} countries. Every price point passes quality validation — no outliers, no stale data. Your agent gets clean data, ready to compare baskets or trigger procurement workflows.`}
        </p>
      </div>
    </EditorialSection>
  );
}
