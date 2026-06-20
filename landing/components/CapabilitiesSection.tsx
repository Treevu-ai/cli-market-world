"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const CAPABILITIES = [
  {
    slug: "price-engine",
    title_es: "Price Engine",
    title_en: "Price Engine",
    description_es: `Precios normalizados por kg/L en ${MARKET_STATS.retailersVerified} retailers de ${MARKET_STATS.countries} países. Cada ciclo de ${MARKET_STATS.pricesRefreshHours}h pasa por validación de calidad: sin valores atípicos, sin datos stale. ${MARKET_STATS.pricesVerifiedLabel} price points listos para comparar.`,
    description_en: `Prices normalized per kg/L across ${MARKET_STATS.retailersVerified} retailers in ${MARKET_STATS.countries} countries. Every ${MARKET_STATS.pricesRefreshHours}h cycle passes quality validation: no outliers, no stale data. ${MARKET_STATS.pricesVerifiedLabel} price points ready to compare.`,
    href: "#how-it-works",
  },
  {
    slug: "agent-tools",
    title_es: "Agent Tools",
    title_en: "Agent Tools",
    description_es: `${MARKET_STATS.mcpTools} tools MCP — search, basket, compare, stock, delivery, historial de precios. Un pip install y tu agente puede buscar, comparar y comprar sin scraping ni integraciones manuales.`,
    description_en: `${MARKET_STATS.mcpTools} MCP tools — search, basket, compare, stock, delivery, price history. One pip install and your agent can search, compare, and buy without scraping or manual integrations.`,
    href: "#how-it-works",
  },
  {
    slug: "procurement",
    title_es: "Procurement",
    title_en: "Procurement",
    description_es: "Canasta multi-retailer con flujo de aprobaciones, control presupuestario y checkout. Tu equipo de compras compara en segundos y cierra con Yape o PayPal — sin WhatsApp, sin hojas de cálculo.",
    description_en: "Multi-retailer basket with approval workflows, budget control, and checkout. Your procurement team compares in seconds and closes with Yape or PayPal — no WhatsApp, no spreadsheets.",
    href: "#procure",
  },
  {
    slug: "intelligence",
    title_es: "Intelligence",
    title_en: "Intelligence",
    description_es: `${MARKET_STATS.indicatorsCount} indicadores de mercado — tendencias de precios, spreads de calidad, inflación desde góndola. Para analistas, fondos y equipos que necesitan datos de retail LATAM antes que el IPC.`,
    description_en: `${MARKET_STATS.indicatorsCount} market indicators — price trends, quality spreads, shelf-price inflation. For analysts, funds, and teams that need LATAM retail data before CPI.`,
    href: "#intelligence",
  },
];

export default function CapabilitiesSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const itemRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  useEffect(() => {
    const items = itemRefs.current.filter(Boolean) as HTMLDivElement[];
    const observers: IntersectionObserver[] = [];

    items.forEach((item, index) => {
      gsap.set(item, { opacity: 0, y: 60 });

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              gsap.to(item, {
                opacity: 1,
                y: 0,
                duration: 1.0,
                delay: index * 0.12,
                ease: "power3.out",
              });
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.15 }
      );

      observer.observe(item);
      observers.push(observer);
    });

    return () => observers.forEach((o) => o.disconnect());
  }, []);

  return (
    <section
      id="capabilities"
      className="landing-section"
      style={{ background: "#0a0a0a", position: "relative", zIndex: 2 }}
    >
      <div className="landing-container-wide">
        <div className="mb-6">
          <span className="text-[11px] font-mono uppercase tracking-[3px] text-[var(--cm-on-surface-variant)]/60">
            {isES ? "Capacidades" : "Capabilities"}
          </span>
        </div>
        <div className="mb-16 sm:mb-24 w-full h-px bg-white/10" />

        <div className="flex flex-col" style={{ gap: "clamp(60px, 8vw, 100px)" }}>
          {CAPABILITIES.map((cap, i) => (
            <div
              key={cap.slug}
              ref={(el) => { itemRefs.current[i] = el; }}
              className="flex flex-col md:flex-row md:items-start"
              style={{ gap: "clamp(24px, 4vw, 60px)", cursor: "default" }}
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {/* Large Garamond title — 70% width */}
              <div style={{ flex: "0 0 65%" }}>
                <a href={cap.href} className="block no-underline group">
                  <h3
                    style={{
                      fontFamily: "var(--font-garamond), 'EB Garamond', Georgia, serif",
                      fontWeight: 400,
                      fontSize: "clamp(36px, 5.4vw, 80px)",
                      lineHeight: 1.05,
                      letterSpacing: "-1.2px",
                      color: hoveredIndex === i ? "rgba(200, 170, 130, 1)" : "#ffffff",
                      margin: 0,
                      textWrap: "balance",
                      transition: "color 0.4s ease",
                    }}
                  >
                    {isES ? cap.title_es : cap.title_en}
                  </h3>
                </a>
              </div>

              {/* Description — 35% width, fades on hover */}
              <div
                style={{
                  flex: "1 1 35%",
                  paddingTop: "clamp(4px, 1vw, 14px)",
                  position: "relative",
                  minHeight: 80,
                }}
              >
                <p
                  style={{
                    fontFamily: "var(--font-inter), Inter, sans-serif",
                    fontWeight: 300,
                    fontSize: 15,
                    lineHeight: 1.8,
                    color: "rgba(218, 218, 218, 0.8)",
                    margin: 0,
                    textWrap: "pretty",
                    opacity: hoveredIndex === i ? 0.4 : 1,
                    transition: "opacity 0.35s ease",
                  }}
                >
                  {isES ? cap.description_es : cap.description_en}
                </p>
                <a
                  href={cap.href}
                  className="text-[11px] font-mono text-[var(--cm-amber)] mt-4 inline-block"
                  style={{
                    opacity: hoveredIndex === i ? 1 : 0,
                    transform: hoveredIndex === i ? "translateY(0)" : "translateY(4px)",
                    transition: "opacity 0.35s ease, transform 0.35s ease",
                    pointerEvents: hoveredIndex === i ? "auto" : "none",
                  }}
                >
                  {isES ? "Explorar →" : "Explore →"}
                </a>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-16 sm:mt-24 w-full h-px bg-white/10" />
      </div>
    </section>
  );
}
