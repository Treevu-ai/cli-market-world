"use client";
import { useState, useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLang } from "@/lib/LanguageContext";

gsap.registerPlugin(ScrollTrigger);

type CmdLine = { text: string; color?: string; delay: number };
type Cell = { title: string; color: string; lines: CmdLine[]; results?: {text:string;color:string}[] };

const cells: Cell[] = [
  {
    title: "Search",
    color: "#3cffd0",
    lines: [
      { text: "market login", delay: 0 },
      { text: 'market search "leche" --country PE', delay: 800, color: "#FFD600" },
    ],
    results: [
      { text: "1. Leche Gloria 400ml  Wong  S/3.50", color: "#888" },
      { text: "2. Leche Ideal 395g  Metro  S/3.20", color: "#888" },
      { text: "3. Leche Laive 1L  PlazaVea  S/3.80", color: "#888" },
    ],
  },
  {
    title: "Compare",
    color: "#4ADE80",
    lines: [
      { text: 'market compare "aceite"', delay: 1200 },
      { text: "", delay: 400 },
    ],
    results: [
      { text: "Aceite Primor 1L → S/8.90 Wong  🇵🇪", color: "#888" },
      { text: "Aceite Natura 900ml → ARS 1250 Carrefour  🇦🇷", color: "#888" },
      { text: "Aceite Liza 900ml → R$6.50 Carrefour BR  🇧🇷", color: "#888" },
      { text: "→ Mejor precio: Wong 🇵🇪", color: "#4ADE80" },
    ],
  },
  {
    title: "Cart & Checkout",
    color: "#FF6B35",
    lines: [
      { text: "market add 1 --qty 2", delay: 600 },
      { text: "market cart", delay: 600 },
      { text: "market checkout --payment yape", delay: 600 },
    ],
    results: [
      { text: "✓ Agregado: 2x Leche Gloria 400ml", color: "#888" },
      { text: "Total: S/7.00", color: "#888" },
      { text: "✓ Pedido ORD-005 confirmado", color: "#28C840" },
    ],
  },
  {
    title: "Agent mode",
    color: "#A78BFA",
    lines: [
      { text: 'market ask "compra arroz al mejor precio"', delay: 1000, color: "#A78BFA" },
      { text: "", delay: 300 },
    ],
    results: [
      { text: "→ Buscando arroz en 30 retailers...", color: "#888" },
      { text: "→ Comparando precios en 8 países...", color: "#888" },
      { text: "→ Mejor: Arroz Costeño 1kg Metro S/4.20", color: "#A78BFA" },
      { text: "✓ Agregado al carrito", color: "#28C840" },
    ],
  },
];

function MiniTerminal({ cell, active }: { cell: Cell; active: boolean }) {
  const [visibleLines, setVisibleLines] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    if (!active) { setVisibleLines(0); setShowResults(false); return; }
    const timers: ReturnType<typeof setTimeout>[] = [];
    cell.lines.forEach((l, i) => {
      timers.push(setTimeout(() => setVisibleLines(i + 1), l.delay));
    });
    const lastDelay = cell.lines.reduce((s, l) => s + l.delay + 400, 0);
    timers.push(setTimeout(() => setShowResults(true), lastDelay));
    timerRef.current = timers;
    return () => timers.forEach(clearTimeout);
  }, [active]);

  const prompt = "$";

  return (
    <div className="bg-[#0c0c0c] border border-[#2d2d2d] overflow-hidden w-full">
      <div className="flex items-center gap-1.5 px-3 py-2 bg-[#1a1a1a] border-b border-[#2d2d2d]">
        <div className="w-[8px] h-[8px] rounded-full bg-[#FF5F57]"/>
        <div className="w-[8px] h-[8px] rounded-full bg-[#FEBC2E]"/>
        <div className="w-[8px] h-[8px] rounded-full bg-[#28C840]"/>
        <span className="ml-2 text-[9px] font-mono text-[#555] tracking-wider">{cell.title}</span>
        <span className="ml-auto w-[6px] h-[6px] rounded-full" style={{background: active ? cell.color : "#333", boxShadow: active ? `0 0 6px ${cell.color}40` : "none", transition: "all 0.5s ease"}}/>
      </div>
      <div className="p-3 sm:p-4 font-mono text-[9px] sm:text-[10px] leading-[1.8] min-h-[180px] text-[#666]">
        {cell.lines.slice(0, visibleLines).map((l, i) => (
          <div key={i} style={{ color: l.color || "#ccc" }}>
            {l.text ? <><span style={{ color: "#3cffd0" }}>{prompt} </span>{l.text}</> : <>&nbsp;</>}
          </div>
        ))}
        {showResults && cell.results?.map((r, i) => (
          <div key={`r${i}`} style={{ color: r.color, animation: "fadeIn 0.5s ease forwards", opacity: 0, animationDelay: `${i * 0.15}s` }}>
            {r.text}
          </div>
        ))}
        {!showResults && visibleLines > 0 && (
          <span className="inline-block w-[6px] h-[11px] bg-[#3cffd0] animate-pulse align-middle mt-0.5"/>
        )}
        {showResults && (
          <div className="mt-1"><span className="text-[#3cffd0]">{prompt} </span><span className="inline-block w-[6px] h-[11px] bg-[#3cffd0] animate-pulse align-middle"/></div>
        )}
      </div>
    </div>
  );
}

export default function TerminalSection() {
  const { t } = useLang();
  const ref = useRef<HTMLDivElement>(null);
  const gridRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const cells = gridRef.current?.querySelectorAll(".term-cell");
      if (cells) {
        gsap.fromTo(cells, { opacity: 0, y: 24, scale: 0.97 }, {
          opacity: 1, y: 0, scale: 1, duration: 0.6, stagger: 0.15,
          scrollTrigger: { trigger: gridRef.current, start: "top 75%", toggleActions: "play none none none" },
        });
      }
    }, gridRef);
    return () => ctx.revert();
  }, []);

  return (
    <section ref={ref} id="terminal" className="relative flex flex-col w-full bg-[#090909] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#3cffd0]/40"/>{t("terminal_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05]">{t("terminal_title")}</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">{t("terminal_desc")}</p>
      </div>

      <div ref={gridRef} className="w-full max-w-[1100px] grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        {cells.map((cell, i) => (
          <div key={i} className="term-cell">
            <MiniTerminal cell={cell} active={true} />
          </div>
        ))}
      </div>

      <p className="text-white/20 font-mono text-[10px] uppercase tracking-widest max-w-[800px]">{t("terminal_footer")}</p>
    </section>
  );
}
