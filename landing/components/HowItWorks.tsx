"use client";
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLang } from "@/lib/LanguageContext";

gsap.registerPlugin(ScrollTrigger);

const tickerES = [
  "pip install cli-market",
  'market search "leche" --country PE',
  'market compare "aceite"',
  "market checkout --payment yape",
  "60 retailers · 11 países · 3 plataformas",
  "36 MCP tools · API keys · Dashboard",
  "Data moat · precios reales cada 8 horas",
];
const tickerEN = [
  "pip install cli-market",
  'market search "milk" --country AR',
  'market compare "oil"',
  "market checkout --payment card",
  "60 retailers · 11 countries · 3 platforms",
  "36 MCP tools · API keys · Dashboard",
  "Data moat · real prices every 8 hours",
];

export default function HowItWorks() {
  const { t: _t, lang } = useLang();
  const termRef = useRef<HTMLDivElement>(null);
  const tickerRef = useRef<HTMLDivElement>(null);
  const items = lang === "es" ? tickerES : tickerEN;

  useEffect(() => {
    const ctx = gsap.context(() => {
      if (tickerRef.current) {
        const rail = tickerRef.current.querySelector(".ticker-rail");
        if (rail) gsap.to(rail, { xPercent: -50, duration: 30, repeat: -1, ease: "none" });
      }
      const card = termRef.current?.querySelector(".flow-terminal");
      if (card) {
        gsap.fromTo(card, { opacity: 0, y: 24 }, {
          opacity: 1, y: 0, duration: 0.8,
          scrollTrigger: { trigger: termRef.current, start: "top 75%", toggleActions: "play none none none" },
        });
      }
    }, termRef);
    return () => ctx.revert();
  }, []);

  const isES = lang === "es";

  return (
    <section id="how" className="relative flex flex-col w-full bg-[#090909] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#3cffd0]/40" />{_t("how_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">{_t("how_title")}</h2>
      </div>

      <div ref={termRef} className="w-full max-w-[800px]">
        <div className="flow-terminal bg-[#0c0c0c] border border-[#2d2d2d] overflow-hidden">
          <div className="flex items-center gap-1.5 px-3 py-2 bg-[#1a1a1a] border-b border-[#2d2d2d]">
            <div className="w-[8px] h-[8px] rounded-full bg-[#FF5F57]"/><div className="w-[8px] h-[8px] rounded-full bg-[#FEBC2E]"/><div className="w-[8px] h-[8px] rounded-full bg-[#28C840]"/>
            <span className="ml-2 text-[9px] font-mono text-[#555] tracking-wider">cli-market — flow</span>
          </div>
          <div className="p-3 sm:p-4 font-mono text-[9px] sm:text-[10px] leading-[2] text-[#666]">
            <div><span className="text-[#3cffd0]">$ </span><span className="text-white/60">pip install cli-market</span></div>
            <div><span className="text-[#3cffd0]">$ </span><span className="text-white/60">market login</span></div>
            <div className="text-[#555] ml-3">→ Token stored</div>

            <div className="mt-2"><span className="text-[#3cffd0]">$ </span><span className="text-[#FFD600]">market search "leche" --country PE</span></div>
            <div className="text-[#555] ml-3">1. Leche Gloria 400ml  Wong  S/3.50</div>
            <div className="text-[#555] ml-3">2. Leche Ideal 395g   Metro  S/3.20</div>

            <div className="mt-2"><span className="text-[#3cffd0]">$ </span><span className="text-[#4ADE80]">market compare "aceite"</span></div>
            <div className="text-[#555] ml-3">Aceite Primor 1L → S/8.90 Wong 🇵🇪</div>
            <div className="text-[#555] ml-3">Aceite Natura 900ml → ARS 1,250 Carrefour 🇦🇷</div>
            <div className="text-[#4ADE80] ml-3">→ Mejor: Wong 🇵🇪</div>

            <div className="mt-2"><span className="text-[#3cffd0]">$ </span><span className="text-[#FF6B35]">market add 1 --qty 2</span></div>
            <div className="text-[#555] ml-3">✓ Agregado al carrito</div>

            <div className="mt-2"><span className="text-[#3cffd0]">$ </span><span className="text-[#60A5FA]">market checkout --payment yape</span></div>
            <div className="text-[#28C840] ml-3">✓ Pedido ORD-005 confirmado · S/20.10</div>

            <div className="mt-3"><span className="text-[#3cffd0]">$ </span><span className="inline-block w-[6px] h-[11px] bg-[#3cffd0] animate-pulse align-middle"/></div>
          </div>
        </div>
      </div>

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
