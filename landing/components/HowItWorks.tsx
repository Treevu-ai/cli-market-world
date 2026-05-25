"use client";
import { useLang } from "@/lib/LanguageContext";

export default function HowItWorks() {
  const { t: _t } = useLang();

  return (
    <section id="how" className="relative flex flex-col w-full bg-[#090909] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#3cffd0]/40"/>{_t("how_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">{_t("how_title")}</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">{_t("how_subtitle")}</p>
      </div>

      {/* Scrolling ticker tape */}
      <div className="relative w-full overflow-hidden border-y border-[#2d2d2d] py-3">
        <style>{`
          @keyframes ticker-move {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
          }
          .ticker-rail {
            display: flex;
            width: max-content;
            animation: ticker-move 22s linear infinite;
          }
          .ticker-rail:hover {
            animation-play-state: paused;
          }
        `}</style>
        <div className="ticker-rail">
          {[0, 1, 2, 3].map((i) => (
            <span key={i} className="flex items-center gap-6 font-mono text-[11px] tracking-[4px] uppercase whitespace-nowrap pr-8">
              <span className="text-[#3cffd0]">▸</span>
              <span className="text-white/30">{_t("how_footer")}</span>
              <span className="text-[#3cffd0]">▸</span>
              <span className="text-white/10">pip install cli-market</span>
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
