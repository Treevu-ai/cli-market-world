"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLang } from "@/lib/LanguageContext";
import { useLiveStats, formatMarketingPrices } from "@/hooks/useLiveStats";
import { MARKET_STATS } from "@/lib/marketStats";

const ACTS = [
  {
    id: "gondola",
    idx: "01",
    title_es: "Góndola",
    title_en: "Shelf",
    headline_es: "El precio vive en la góndola.",
    headline_en: "Price lives on the shelf.",
    body_es:
      "Cada etiqueta en Metro, Wong o Plaza Vea es un dato que hoy vive aislado. Sin API, sin historial, sin comparar.",
    body_en:
      "Every tag at Metro, Wong, or Plaza Vea is data trapped in silos. No API, no history, no cross-store compare.",
  },
  {
    id: "terminal",
    idx: "02",
    title_es: "Terminal",
    title_en: "Terminal",
    headline_es: "Un comando. Todas las cadenas.",
    headline_en: "One command. Every chain.",
    body_es:
      "market compare normaliza por kg/L y devuelve el mejor precio en segundos — misma superficie que tu agente usará en producción.",
    body_en:
      "market compare normalizes per kg/L and returns the best price in seconds — the same surface your agent runs in production.",
  },
  {
    id: "data",
    idx: "03",
    title_es: "Dato",
    title_en: "Data",
    headline_es: "Verificado cada 4 horas.",
    headline_en: "Verified every 4 hours.",
    body_es:
      "Snapshots en PostgreSQL, spreads reales, serie histórica del moat. Sin estimaciones de encuestas.",
    body_en:
      "PostgreSQL snapshots, real spreads, moat time series. No survey estimates.",
  },
  {
    id: "agent",
    idx: "04",
    title_es: "Agente",
    title_en: "Agent",
    headline_es: "Tu agente compra con contexto.",
    headline_en: "Your agent shops with context.",
    body_es: `${MARKET_STATS.mcpTools} herramientas MCP · API REST · CLI · cero scraping.`,
    body_en: `${MARKET_STATS.mcpTools} MCP tools · REST API · CLI · zero scraping.`,
  },
] as const;

function GondolaVisual() {
  const shelves = [
    { name: "Arroz 1kg", price: "S/ 3.90" },
    { name: "Leche 900ml", price: "S/ 4.50" },
    { name: "Aceite 900ml", price: "S/ 8.20" },
  ];
  return (
    <div className="scroll-story-gondola" aria-hidden="true">
      {shelves.map((s) => (
        <div key={s.name} className="scroll-story-shelf">
          <span className="scroll-story-shelf-name">{s.name}</span>
          <span className="scroll-story-shelf-price">{s.price}</span>
        </div>
      ))}
    </div>
  );
}

function TerminalVisual({ isES }: { isES: boolean }) {
  return (
    <div className="scroll-story-term" aria-hidden="true">
      <div className="scroll-story-term-line scroll-story-term-cmd">
        $ market compare &quot;arroz&quot; --country PE
      </div>
      <div className="scroll-story-term-line scroll-story-term-out">Metro · S/ 2.90 /kg</div>
      <div className="scroll-story-term-line scroll-story-term-out">Wong · S/ 3.10 /kg</div>
      <div className="scroll-story-term-line scroll-story-term-best">
        ▸ Plaza Vea · S/ 2.85 /kg {isES ? "· MEJOR" : "· BEST"}
      </div>
    </div>
  );
}

function DataVisual({
  isES,
  pricesLabel,
  snapshots,
  sparkCoords,
  sparkLast,
}: {
  isES: boolean;
  pricesLabel: string;
  snapshots: string | null;
  sparkCoords: string;
  sparkLast: string | null;
}) {
  return (
    <div className="scroll-story-data" aria-hidden="true">
      <div className="scroll-story-stat-grid">
        <div>
          <p className="scroll-story-stat-n">{pricesLabel}</p>
          <p className="scroll-story-stat-l">{isES ? "precios indexados" : "indexed prices"}</p>
        </div>
        <div>
          <p className="scroll-story-stat-n">{MARKET_STATS.retailersVerified}</p>
          <p className="scroll-story-stat-l">{isES ? "retailers activos" : "active retailers"}</p>
        </div>
        {snapshots ? (
          <div>
            <p className="scroll-story-stat-n">{snapshots}</p>
            <p className="scroll-story-stat-l">{isES ? "snapshots 24h" : "snapshots 24h"}</p>
          </div>
        ) : null}
      </div>
      {sparkCoords ? (
        <svg viewBox="0 0 200 48" className="scroll-story-spark">
          <polyline
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinejoin="round"
            points={sparkCoords}
          />
        </svg>
      ) : null}
      {sparkLast ? <p className="scroll-story-spark-meta">{sparkLast}</p> : null}
    </div>
  );
}

function AgentVisual() {
  const tools = ["market_search", "market_compare", "market_basket", "market_checkout"];
  return (
    <div className="scroll-story-agent" aria-hidden="true">
      <div className="scroll-story-agent-flow">
        <span className="scroll-story-agent-node">Agent</span>
        <span className="scroll-story-agent-arrow">→</span>
        <span className="scroll-story-agent-node scroll-story-agent-node-mcp">MCP</span>
        <span className="scroll-story-agent-arrow">→</span>
        <span className="scroll-story-agent-node scroll-story-agent-node-api">API</span>
        <span className="scroll-story-agent-arrow">→</span>
        <span className="scroll-story-agent-node">VTEX</span>
      </div>
      <ul className="scroll-story-tool-list">
        {tools.map((t) => (
          <li key={t}>
            <span className="text-[var(--cm-data)]">▸</span> {t}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function ScrollStorySection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const sectionRef = useRef<HTMLElement>(null);
  const pinRef = useRef<HTMLDivElement>(null);
  const actsRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const { stats, liveLoaded } = useLiveStats();

  const { chip: pricesChip } = formatMarketingPrices(stats.indexed);
  const snapshots24h =
    stats.snapshots24h != null && stats.snapshots24h > 0
      ? stats.snapshots24h.toLocaleString()
      : null;

  const inventory = stats.inventoryDaily?.slice(-10) ?? [];
  const values = inventory.map((p) => p.snapshots);
  const max = Math.max(...values, 1);
  const min = Math.min(...values, max);
  const sparkCoords =
    values.length >= 2
      ? values
          .map((v, i) => {
            const x = 4 + (i / Math.max(values.length - 1, 1)) * 192;
            const y = 44 - ((v - min) / Math.max(max - min, 1)) * 36;
            return `${x},${y}`;
          })
          .join(" ")
      : "";
  const sparkLast =
    inventory.length && liveLoaded
      ? `${inventory[inventory.length - 1].day}: ${inventory[inventory.length - 1].snapshots.toLocaleString()} snapshots`
      : null;

  useEffect(() => {
    const section = sectionRef.current;
    const pin = pinRef.current;
    const stage = actsRef.current;
    const progress = progressRef.current;
    if (!section || !pin || !stage) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) return;

    gsap.registerPlugin(ScrollTrigger);

    const actEls = gsap.utils.toArray<HTMLElement>(".scroll-story-act", stage);
    const dots = gsap.utils.toArray<HTMLElement>(".scroll-story-dot", progress);

    const ctx = gsap.context(() => {
      gsap.set(actEls.slice(1), { opacity: 0, y: 28, pointerEvents: "none" });
      gsap.set(dots[0], { opacity: 1 });

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: section,
          start: "top top",
          end: () => `+=${window.innerHeight * 3}`,
          pin,
          scrub: 0.55,
          anticipatePin: 1,
          snap: {
            snapTo: 1 / (actEls.length - 1),
            duration: { min: 0.15, max: 0.35 },
            delay: 0.05,
          },
        },
      });

      actEls.forEach((el, i) => {
        if (i === 0) return;
        const prev = actEls[i - 1];
        const at = i - 1;
        tl.to(prev, { opacity: 0, y: -24, duration: 1, pointerEvents: "none" }, at).to(
          el,
          { opacity: 1, y: 0, duration: 1, pointerEvents: "auto" },
          at,
        );
        dots.forEach((dot, idx) => {
          tl.to(dot, { opacity: idx === i ? 1 : 0.35, duration: 0.25 }, at);
        });
      });
    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="story"
      ref={sectionRef}
      className="scroll-story brand-mode-terminal scroll-mt-20"
      aria-label={isES ? "Historia del producto en 4 actos" : "Product story in 4 acts"}
    >
      <div ref={pinRef} className="scroll-story-pin">
        <div className="landing-container-wide">
          <p className="section-eyebrow section-eyebrow-action text-center mb-6">
            {isES ? "De la góndola al agente" : "Shelf to agent"}
          </p>

          <div ref={progressRef} className="scroll-story-progress" aria-hidden="true">
            {ACTS.map((act) => (
              <span key={act.id} className="scroll-story-dot">
                <span className="scroll-story-dot-idx">{act.idx}</span>
                <span className="scroll-story-dot-label">{isES ? act.title_es : act.title_en}</span>
              </span>
            ))}
          </div>

          <div ref={actsRef} className="scroll-story-stage">
            {ACTS.map((act, i) => (
              <article
                key={act.id}
                className={`scroll-story-act${i === 0 ? " scroll-story-act-active" : ""}`}
                aria-hidden={i !== 0}
              >
                <div className="scroll-story-act-grid">
                  <div className="scroll-story-copy">
                    <p className="scroll-story-idx">{act.idx}</p>
                    <h2 className="scroll-story-headline">
                      {isES ? act.headline_es : act.headline_en}
                    </h2>
                    <p className="scroll-story-body">{isES ? act.body_es : act.body_en}</p>
                  </div>
                  <div className="scroll-story-visual">
                    {act.id === "gondola" ? <GondolaVisual /> : null}
                    {act.id === "terminal" ? <TerminalVisual isES={isES} /> : null}
                    {act.id === "data" ? (
                      <DataVisual
                        isES={isES}
                        pricesLabel={pricesChip}
                        snapshots={snapshots24h}
                        sparkCoords={sparkCoords}
                        sparkLast={sparkLast}
                      />
                    ) : null}
                    {act.id === "agent" ? <AgentVisual /> : null}
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>

      {/* Reduced motion: show all acts stacked */}
      <div className="scroll-story-static landing-container-wide">
        {ACTS.map((act) => (
          <article key={`static-${act.id}`} className="scroll-story-static-act">
            <p className="scroll-story-idx">{act.idx}</p>
            <h2 className="scroll-story-headline">{isES ? act.headline_es : act.headline_en}</h2>
            <p className="scroll-story-body mb-6">{isES ? act.body_es : act.body_en}</p>
            {act.id === "gondola" ? <GondolaVisual /> : null}
            {act.id === "terminal" ? <TerminalVisual isES={isES} /> : null}
            {act.id === "data" ? (
              <DataVisual
                isES={isES}
                pricesLabel={pricesChip}
                snapshots={snapshots24h}
                sparkCoords={sparkCoords}
                sparkLast={sparkLast}
              />
            ) : null}
            {act.id === "agent" ? <AgentVisual /> : null}
          </article>
        ))}
      </div>
    </section>
  );
}
