"use client";
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLang } from "@/lib/LanguageContext";

gsap.registerPlugin(ScrollTrigger);

const steps = [
  {
    step: "01", title_es: "Search", title_en: "Search", color: "#3cffd0",
    cmd: 'market search "leche" --country PE',
    results: ["1. Leche Gloria 400ml  Wong  S/3.50", "2. Leche Ideal 395g  Metro  S/3.20"],
  },
  {
    step: "02", title_es: "Compare", title_en: "Compare", color: "#4ADE80",
    cmd: 'market compare "aceite"',
    results: ["Aceite Primor 1L → S/8.90 Wong 🇵🇪", "Aceite Natura 900ml → ARS 1250 Carrefour 🇦🇷", "→ Mejor: Wong 🇵🇪"],
  },
  {
    step: "03", title_es: "Checkout", title_en: "Checkout", color: "#FF6B35",
    cmd: "market checkout --payment yape",
    results: ["Total: S/20.10 · Yape", "✓ Pedido ORD-005 confirmado"],
  },
  {
    step: "04", title_es: "Agent mode", title_en: "Agent mode", color: "#A78BFA",
    cmd: 'market ask "compra arroz al mejor precio"',
    results: ["→ Buscando en 30 retailers...", "→ Mejor: Arroz Costeño 1kg Metro S/4.20", "✓ Agregado al carrito"],
  },
];

const tickerES = [
  "pip install cli-market",
  'market search "leche" --country PE',
  'market compare "aceite"',
  "market checkout --payment yape",
  'market ask "compra arroz al mejor precio"',
  "30 retailers · 8 países · 6 líneas",
  "30 MCP tools · API keys · Dashboard",
  "Data moat · 4.4K precios · query expansion",
];
const tickerEN = [
  "pip install cli-market",
  'market search "milk" --country AR',
  'market compare "oil"',
  "market checkout --payment card",
  'market ask "buy rice at the best price"',
  "30 retailers · 8 countries · 6 lines",
  "30 MCP tools · API keys · Dashboard",
  "Data moat · 4.4K prices · query expansion",
];

export default function HowItWorks() {
  const { t: _t, lang } = useLang();
  const stepsRef = useRef<HTMLDivElement>(null);
  const tickerRef = useRef<HTMLDivElement>(null);
  const items = lang === "es" ? tickerES : tickerEN;

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Ticker tape animation
      if (tickerRef.current) {
        const rail = tickerRef.current.querySelector(".ticker-rail");
        if (rail) {
          gsap.to(rail, { xPercent: -50, duration: 30, repeat: -1, ease: "none" });
        }
      }

      // Step reveals on scroll
      const cards = stepsRef.current?.querySelectorAll(".how-step");
      if (cards) {
        gsap.fromTo(cards, { opacity: 0, y: 32 }, {
          opacity: 1, y: 0, duration: 0.8, stagger: 0.2,
          scrollTrigger: { trigger: stepsRef.current, start: "top 70%", toggleActions: "play none none none" },
        });
      }

      // Subtle parallax on the ticker
      ScrollTrigger.create({
        trigger: tickerRef.current,
        start: "top bottom",
        end: "bottom top",
        onUpdate: (self) => {
          const rail = tickerRef.current?.querySelector(".ticker-rail");
          if (rail) gsap.set(rail, { y: self.progress * 10 });
        },
      });
    }, stepsRef);
    return () => ctx.revert();
  }, []);

  return (
    <section id="how" className="relative flex flex-col w-full bg-[#090909] py-16 px-6 lg:px-12 md:py-[80px] gap-10">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#3cffd0]/40" />{_t("how_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">{_t("how_title")}</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">{_t("how_subtitle")}</p>
      </div>

      {/* Scroll-through flow cards */}
      <div ref={stepsRef} className="w-full max-w-[1100px] grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {steps.map((s) => (
          <div key={s.step} className="how-step bg-[#0c0c0c] border border-[#1f1f1f] p-4 flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold tracking-widest" style={{ color: s.color }}>{s.step}</span>
              <span className="text-[11px] font-mono text-white/60">{lang === "es" ? s.title_es : s.title_en}</span>
            </div>
            <div className="bg-[#080808] p-3 font-mono text-[9px] leading-[1.8] text-[#888]">
              <span className="text-[#3cffd0]">$ </span>
              <span style={{ color: s.color }}>{s.cmd}</span>
              {s.results.map((r, i) => (
                <div key={i} className="mt-1" style={{ color: i === s.results.length - 1 && s.color === "#4ADE80" ? "#4ADE80" : "#666" }}>{r}</div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Scrolling ticker tape */}
      <div ref={tickerRef} className="relative w-full overflow-hidden border-y border-[#2d2d2d] py-3">
        <div className="ticker-rail flex w-max">
          {[0, 1].map((dup) => (
            <span key={dup} className="flex items-center gap-10 font-mono text-[11px] tracking-[3px] uppercase whitespace-nowrap pr-10">
              {items.map((item, i) => (
                <span key={i} className="flex items-center gap-6">
                  <span className="text-[#3cffd0]">▸</span>
                  <span className={i < 4 ? "text-white/40" : "text-white/15"}>{item}</span>
                </span>
              ))}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
