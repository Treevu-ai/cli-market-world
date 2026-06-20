"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { EditorialSection, EditorialRule } from "@/components/EditorialSection";

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
    href: "/tools",
  },
  {
    slug: "procurement",
    title_es: "Procurement",
    title_en: "Procurement",
    description_es: "Canasta multi-retailer con flujo de aprobaciones, control presupuestario y checkout. Tu equipo de compras compara en segundos y cierra con Yape o PayPal — sin WhatsApp, sin hojas de cálculo.",
    description_en: "Multi-retailer basket with approval workflows, budget control, and checkout. Your procurement team compares in seconds and closes with Yape or PayPal — no WhatsApp, no spreadsheets.",
    href: "/#procure",
  },
  {
    slug: "intelligence",
    title_es: "Intelligence",
    title_en: "Intelligence",
    description_es: `${MARKET_STATS.indicatorsCount} indicadores de mercado — tendencias de precios, spreads de calidad, inflación desde góndola. Para analistas, fondos y equipos que necesitan datos de retail LATAM antes que el IPC.`,
    description_en: `${MARKET_STATS.indicatorsCount} market indicators — price trends, quality spreads, shelf-price inflation. For analysts, funds, and teams that need LATAM retail data before CPI.`,
    href: "/docs#intel",
  },
];

export default function CapabilitiesSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const itemRefs = useRef<(HTMLElement | null)[]>([]);

  useEffect(() => {
    const items = itemRefs.current.filter(Boolean) as HTMLElement[];
    const observers: IntersectionObserver[] = [];

    items.forEach((item, index) => {
      gsap.set(item, { opacity: 0, y: 40 });

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              gsap.to(item, {
                opacity: 1,
                y: 0,
                duration: 0.85,
                delay: index * 0.1,
                ease: "power3.out",
              });
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.12 },
      );

      observer.observe(item);
      observers.push(observer);
    });

    return () => observers.forEach((o) => o.disconnect());
  }, []);

  return (
    <EditorialSection id="capabilities" eyebrow={isES ? "Capacidades" : "Capabilities"}>
      <div className="landing-editorial-stack">
        {CAPABILITIES.map((cap, i) => (
          <article
            key={cap.slug}
            ref={(el) => {
              itemRefs.current[i] = el;
            }}
            className="landing-editorial-row"
          >
            <div className="landing-editorial-row__title">
              <a href={cap.href} className="landing-editorial-capability-link">
                <h3 className="landing-editorial-capability-title">
                  {isES ? cap.title_es : cap.title_en}
                </h3>
              </a>
            </div>
            <div className="landing-editorial-row__body">
              <p className="landing-editorial-body">
                {isES ? cap.description_es : cap.description_en}
              </p>
              <a href={cap.href} className="landing-editorial-cta">
                {isES ? "Explorar →" : "Explore →"}
              </a>
            </div>
          </article>
        ))}
      </div>
      <EditorialRule className="mt-16 sm:mt-20" />
    </EditorialSection>
  );
}