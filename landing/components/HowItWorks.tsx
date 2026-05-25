"use client";
import { useLang } from "@/lib/LanguageContext";

const tickerES = [
  "pip install cli-market",
  "market search \"leche\" --country PE",
  "market compare \"aceite\"",
  "market checkout --payment yape",
  "market ask \"compra arroz al mejor precio\"",
  "30 retailers · 8 países · 6 líneas",
  "30 MCP tools · API keys · Dashboard",
  "Data moat · 4.4K precios · query expansion",
];
const tickerEN = [
  "pip install cli-market",
  "market search \"milk\" --country AR",
  "market compare \"oil\"",
  "market checkout --payment card",
  "market ask \"buy rice at the best price\"",
  "30 retailers · 8 countries · 6 lines",
  "30 MCP tools · API keys · Dashboard",
  "Data moat · 4.4K prices · query expansion",
];

export default function HowItWorks() {
  const { t: _t, lang } = useLang();
  const items = lang === "es" ? tickerES : tickerEN;

  return (
    <section id="how" className="relative flex flex-col w-full bg-[#090909] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#3cffd0]/40"/>{_t("how_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">{_t("how_title")}</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">{_t("how_subtitle")}</p>
      </div>

      <div className="relative w-full overflow-hidden border-y border-[#2d2d2d] py-3">
        <style>{`
          @keyframes ticker {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
          }
          .ticker-rail {
            display: flex;
            width: max-content;
            animation: ticker 30s linear infinite;
          }
          .ticker-rail:hover { animation-play-state: paused; }
        `}</style>
        <div className="ticker-rail">
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
