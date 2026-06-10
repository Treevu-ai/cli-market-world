"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLang } from "@/lib/LanguageContext";
import { useLiveStats, formatMarketingPrices, refreshLabel } from "@/hooks/useLiveStats";
import { MARKET_STATS } from "@/lib/marketStats";

const SCROLL_VIEWPORTS = 5.5;

const ACTS = [
  {
    id: "gondola",
    idx: "01",
    title_es: "Góndola",
    title_en: "Shelf",
    headline_es: "El precio vive en la góndola.",
    headline_en: "Price lives on the shelf.",
    body_es:
      "Cada etiqueta en Metro, Wong o Plaza Vea es un dato aislado: sin API, sin historial, sin comparar entre cadenas.",
    body_en:
      "Every tag at Metro, Wong, or Plaza Vea is isolated data — no API, no history, no cross-chain compare.",
  },
  {
    id: "terminal",
    idx: "02",
    title_es: "Terminal",
    title_en: "Terminal",
    headline_es: "Un comando. Todas las cadenas.",
    headline_en: "One command. Every chain.",
    body_es:
      "market compare normaliza por kg/L y devuelve el mejor precio en segundos — la misma superficie que tu agente ejecuta en producción.",
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
      "Snapshots en PostgreSQL, spreads reales y serie histórica del moat. Sin estimaciones de encuestas con 30 días de retraso.",
    body_en:
      "PostgreSQL snapshots, real spreads, and moat time series. No survey estimates lagging 30 days.",
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

const GONDOLA_ROWS = [
  { name: "Arroz Extra 1kg", store: "Metro", price: "S/ 3.20" },
  { name: "Arroz Extra 1kg", store: "Wong", price: "S/ 3.45" },
  { name: "Arroz Extra 1kg", store: "Plaza Vea", price: "S/ 2.90", best: true },
  { name: "Leche Gloria 900ml", store: "Metro", price: "S/ 4.80" },
  { name: "Aceite 900ml", store: "Wong", price: "S/ 9.10" },
];

const TERM_ROWS = [
  { store: "Metro", price: 2.9, best: false },
  { store: "Wong", price: 3.1, best: false },
  { store: "Plaza Vea", price: 2.85, best: true },
];

function GondolaVisual() {
  return (
    <div className="scroll-story-visual-panel scroll-story-visual-gondola" aria-hidden="true">
      <div className="scroll-story-panel-head">
        <span className="scroll-story-panel-tag">RETAIL FÍSICO</span>
        <span className="scroll-story-panel-meta">PE · supermercados</span>
      </div>
      <div className="scroll-story-gondola-rack">
        {GONDOLA_ROWS.map((row) => (
          <div
            key={`${row.name}-${row.store}`}
            className={`scroll-story-shelf${row.best ? " scroll-story-shelf-best" : ""}`}
          >
            <div className="scroll-story-shelf-meta">
              <span className="scroll-story-shelf-name">{row.name}</span>
              <span className="scroll-story-shelf-store">{row.store}</span>
            </div>
            <span className="scroll-story-shelf-price">{row.price}</span>
          </div>
        ))}
      </div>
      <p className="scroll-story-panel-foot">▸ mismos SKU · precios distintos · sin unificar</p>
    </div>
  );
}

function TerminalVisual({ isES }: { isES: boolean }) {
  const max = Math.max(...TERM_ROWS.map((r) => r.price));
  return (
    <div className="scroll-story-visual-panel scroll-story-visual-terminal" aria-hidden="true">
      <div className="scroll-story-term-chrome">
        <span />
        <span />
        <span />
        <p>cli-market — compare</p>
      </div>
      <div className="scroll-story-term-body">
        <p className="scroll-story-term-cmd">$ market compare &quot;arroz&quot; --country PE</p>
        {TERM_ROWS.map((r) => {
          const w = max > 0 ? Math.round((r.price / max) * 100) : 0;
          return (
            <div
              key={r.store}
              className={`scroll-story-term-row${r.best ? " scroll-story-term-row-best" : ""}`}
            >
              <span className="scroll-story-term-lb">{r.store}</span>
              <div className="scroll-story-term-track">
                <div
                  className="scroll-story-term-fill"
                  style={{ ["--term-fill" as string]: `${w}%` }}
                />
              </div>
              <span className="scroll-story-term-price">
                S/ {r.price.toFixed(2)}
                {r.best ? (
                  <span className="scroll-story-term-tag">{isES ? "MEJOR" : "BEST"}</span>
                ) : null}
              </span>
            </div>
          );
        })}
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
  refreshText,
}: {
  isES: boolean;
  pricesLabel: string;
  snapshots: string | null;
  sparkCoords: string;
  sparkLast: string | null;
  refreshText: string;
}) {
  return (
    <div className="scroll-story-visual-panel scroll-story-visual-data" aria-hidden="true">
      <div className="scroll-story-panel-head">
        <span className="scroll-story-panel-tag scroll-story-panel-tag-live">● LIVE</span>
        <span className="scroll-story-panel-meta">{refreshText}</span>
      </div>
      <div className="scroll-story-stat-grid">
        <div className="scroll-story-stat-card">
          <p className="scroll-story-stat-n">{pricesLabel}</p>
          <p className="scroll-story-stat-l">{isES ? "precios indexados" : "indexed prices"}</p>
        </div>
        <div className="scroll-story-stat-card">
          <p className="scroll-story-stat-n">{MARKET_STATS.retailersVerified}</p>
          <p className="scroll-story-stat-l">{isES ? "retailers activos" : "active retailers"}</p>
        </div>
        <div className="scroll-story-stat-card">
          <p className="scroll-story-stat-n">{snapshots ?? "—"}</p>
          <p className="scroll-story-stat-l">{isES ? "snapshots 24h" : "snapshots 24h"}</p>
        </div>
        <div className="scroll-story-stat-card">
          <p className="scroll-story-stat-n">{MARKET_STATS.countries}</p>
          <p className="scroll-story-stat-l">{isES ? "países" : "countries"}</p>
        </div>
      </div>
      {sparkCoords ? (
        <div className="scroll-story-spark-wrap">
          <p className="scroll-story-spark-label">
            {isES ? "Serie del moat (10d)" : "Moat series (10d)"}
          </p>
          <svg viewBox="0 0 320 80" className="scroll-story-spark" preserveAspectRatio="none">
            <polyline
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinejoin="round"
              strokeLinecap="round"
              points={sparkCoords}
            />
          </svg>
          {sparkLast ? <p className="scroll-story-spark-meta">{sparkLast}</p> : null}
        </div>
      ) : null}
    </div>
  );
}

function AgentVisual({ isES }: { isES: boolean }) {
  const tools = ["market_search", "market_compare", "market_basket", "market_checkout"];
  return (
    <div className="scroll-story-visual-panel scroll-story-visual-agent" aria-hidden="true">
      <div className="scroll-story-agent-flow">
        <div className="scroll-story-agent-node">
          <span className="scroll-story-agent-node-k">01</span>
          <span>Agent</span>
        </div>
        <span className="scroll-story-agent-arrow">→</span>
        <div className="scroll-story-agent-node scroll-story-agent-node-mcp">
          <span className="scroll-story-agent-node-k">02</span>
          <span>MCP · {MARKET_STATS.mcpTools}</span>
        </div>
        <span className="scroll-story-agent-arrow">→</span>
        <div className="scroll-story-agent-node scroll-story-agent-node-api">
          <span className="scroll-story-agent-node-k">03</span>
          <span>API</span>
        </div>
        <span className="scroll-story-agent-arrow">→</span>
        <div className="scroll-story-agent-node">
          <span className="scroll-story-agent-node-k">04</span>
          <span>VTEX</span>
        </div>
      </div>
      <div className="scroll-story-tool-grid">
        {tools.map((t) => (
          <div key={t} className="scroll-story-tool-chip">
            <span className="text-[var(--cm-data)]">▸</span> {t}
          </div>
        ))}
      </div>
      <p className="scroll-story-panel-foot">
        {isES ? "▸ pip install cli-market-world" : "▸ pip install cli-market-world"}
      </p>
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
  const cueRef = useRef<HTMLParagraphElement>(null);
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
            const x = 8 + (i / Math.max(values.length - 1, 1)) * 304;
            const y = 72 - ((v - min) / Math.max(max - min, 1)) * 56;
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
    const cue = cueRef.current;
    if (!section || !pin || !stage) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) return;

    gsap.registerPlugin(ScrollTrigger);

    const actEls = gsap.utils.toArray<HTMLElement>(".scroll-story-act", stage);
    const dots = gsap.utils.toArray<HTMLElement>(".scroll-story-dot", progress);
    const HOLD = 1;
    const SWAP = 0.22;

    const setActiveDot = (idx: number) => {
      dots.forEach((dot, i) => {
        dot.classList.toggle("scroll-story-dot-active", i === idx);
      });
    };

    const markAct = (idx: number) => {
      actEls.forEach((el, i) => {
        el.classList.toggle("scroll-story-act-active", i === idx);
        el.setAttribute("aria-hidden", i === idx ? "false" : "true");
      });
      setActiveDot(idx);
    };

    const ctx = gsap.context(() => {
      gsap.set(actEls[0], { autoAlpha: 1, y: 0, pointerEvents: "auto" });
      gsap.set(actEls.slice(1), { autoAlpha: 0, y: 18, pointerEvents: "none" });
      markAct(0);

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: section,
          start: "top top",
          end: () => `+=${window.innerHeight * SCROLL_VIEWPORTS}`,
          pin,
          scrub: 0.65,
          anticipatePin: 1,
          snap: {
            snapTo: (value) => {
              const step = 1 / (actEls.length - 1);
              return Math.round(value / step) * step;
            },
            duration: { min: 0.2, max: 0.45 },
            delay: 0.08,
          },
          onUpdate: (self) => {
            if (cue) {
              gsap.set(cue, { autoAlpha: self.progress < 0.08 ? 1 : 0 });
            }
          },
        },
      });

      let cursor = HOLD;
      for (let i = 1; i < actEls.length; i++) {
        const prev = actEls[i - 1];
        const cur = actEls[i];
        const swapAt = cursor;

        tl.to(
          prev,
          { autoAlpha: 0, y: -14, duration: SWAP, pointerEvents: "none", ease: "power2.in" },
          swapAt,
        )
          .to(
            cur,
            {
              autoAlpha: 1,
              y: 0,
              duration: SWAP,
              pointerEvents: "auto",
              ease: "power2.out",
            },
            swapAt + SWAP,
          )
          .call(() => markAct(i), undefined, swapAt + SWAP);

        cursor += SWAP * 2 + HOLD;
      }
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
        <div className="scroll-story-atmosphere" aria-hidden="true" />
        <div className="landing-container-wide scroll-story-inner">
          <header className="scroll-story-header">
            <p className="section-eyebrow section-eyebrow-action">
              {isES ? "De la góndola al agente" : "Shelf to agent"}
            </p>
            <p className="scroll-story-sub">
              {isES
                ? "Cuatro actos · datos reales · una sola infraestructura"
                : "Four acts · real data · one infrastructure"}
            </p>
          </header>

          <div ref={progressRef} className="scroll-story-progress" role="tablist" aria-hidden="true">
            <div className="scroll-story-progress-rail" />
            {ACTS.map((act) => (
              <span key={act.id} className={`scroll-story-dot${act.idx === "01" ? " scroll-story-dot-active" : ""}`}>
                <span className="scroll-story-dot-idx">{act.idx}</span>
                <span className="scroll-story-dot-label">{isES ? act.title_es : act.title_en}</span>
              </span>
            ))}
          </div>

          <div ref={actsRef} className="scroll-story-stage">
            {ACTS.map((act, i) => (
              <article
                key={act.id}
                className={`scroll-story-act scroll-story-act-${act.id}${i === 0 ? " scroll-story-act-active" : ""}`}
                {...(i !== 0 ? { "aria-hidden": true } : {})}
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
                        refreshText={refreshLabel(isES)}
                      />
                    ) : null}
                    {act.id === "agent" ? <AgentVisual isES={isES} /> : null}
                  </div>
                </div>
              </article>
            ))}
          </div>

          <p ref={cueRef} className="scroll-story-cue" aria-hidden="true">
            {isES ? "Scroll para continuar ↓" : "Scroll to continue ↓"}
          </p>
        </div>
      </div>

      <div className="scroll-story-static landing-container-wide">
        {ACTS.map((act) => (
          <article key={`static-${act.id}`} className="scroll-story-static-act">
            <p className="scroll-story-idx">{act.idx}</p>
            <h2 className="scroll-story-headline">{isES ? act.headline_es : act.headline_en}</h2>
            <p className="scroll-story-body mb-8">{isES ? act.body_es : act.body_en}</p>
            {act.id === "gondola" ? <GondolaVisual /> : null}
            {act.id === "terminal" ? <TerminalVisual isES={isES} /> : null}
            {act.id === "data" ? (
              <DataVisual
                isES={isES}
                pricesLabel={pricesChip}
                snapshots={snapshots24h}
                sparkCoords={sparkCoords}
                sparkLast={sparkLast}
                refreshText={refreshLabel(isES)}
              />
            ) : null}
            {act.id === "agent" ? <AgentVisual isES={isES} /> : null}
          </article>
        ))}
      </div>
    </section>
  );
}
