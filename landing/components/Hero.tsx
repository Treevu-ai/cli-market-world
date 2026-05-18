"use client";

import { useEffect, useState } from "react";
import GlitchText from "@/components/GlitchText";
import CollabCursors from "@/components/CollabCursors";
import { useLang } from "./lang";

export default function Hero() {
  const [mounted, setMounted] = useState(false);
  const { t } = useLang();
  useEffect(() => setMounted(true), []);

  return (
    <section className="relative flex flex-col items-center w-full bg-[#0A0A0A] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] overflow-hidden group">
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"
        style={{ background: "radial-gradient(ellipse at 50% 30%, rgba(0,255,136,0.04) 0%, transparent 60%)" }} />
      <div className="flex items-center justify-center gap-[6px] sm:gap-[8px] h-[28px] sm:h-[32px] px-[10px] sm:px-[12px] md:px-[16px] bg-[#1A1A1A] border-2 border-[#00FF88] max-w-full group-hover:border-[#00FF88]/80 transition-colors duration-500">
        <div className="w-[6px] h-[6px] sm:w-[8px] sm:h-[8px] bg-[#00FF88] shrink-0" />
        <span className="font-ibm-mono text-[8px] sm:text-[9px] md:text-[11px] font-bold text-[#00FF88] tracking-[1px] md:tracking-[2px]">{t("hero_badge")}</span>
      </div>
      <div className="h-6 sm:h-8 md:h-[24px]" />
      <div className="flex items-center justify-center gap-[6px] h-[24px] sm:h-[28px] px-[10px] sm:px-[14px] bg-[#FFD600]/10 border border-[#FFD600]/30 mb-2 group-hover:bg-[#FFD600]/15 transition-colors duration-500">
        <span className="w-[5px] h-[5px] bg-[#FFD600] rounded-full animate-pulse" />
        <span className="font-ibm-mono text-[8px] sm:text-[9px] font-bold text-[#FFD600] tracking-[1px]">{t("hero_early")}</span>
      </div>
      <div className="h-6 sm:h-8 md:h-[32px]" />
      <h1 className="font-grotesk text-[clamp(26px,8vw,96px)] font-bold text-[#F5F5F0] tracking-[-0.5px] sm:tracking-[-1px] leading-none text-center w-full max-w-[1100px] group-hover:text-white transition-colors duration-500">
        <GlitchText text={t("hero_headline1")} speed={45} delay={100} /><br />
        <GlitchText text={t("hero_headline2")} speed={45} delay={400} />
      </h1>
      <h1 className="font-grotesk text-[clamp(26px,8vw,96px)] font-bold text-[#00FF88] tracking-[-0.5px] sm:tracking-[-1px] leading-none text-center w-full max-w-[1100px]">
        <GlitchText text={t("hero_headline3")} speed={45} delay={700} />
      </h1>
      <div className="h-6 sm:h-8 md:h-[32px]" />
      <p className="font-ibm-mono text-[11px] sm:text-[13px] md:text-[15px] text-[#888888] tracking-[0.5px] sm:tracking-[1px] leading-[1.5] sm:leading-[1.6] text-center w-full max-w-[800px] px-2 group-hover:text-[#AAAAAA] transition-colors duration-500">
        {t("hero_stats")}<br />{t("hero_sub")}
      </p>
      <div className="h-6 sm:h-8" />
      <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-4 md:gap-[24px] px-2">
        {[
          { label: t("hero_for_devs") ?? "FOR DEVELOPERS", sub: "CLI · REST API · JSON · CSV · MCP Tools", color: "#00FF88" },
          { label: t("hero_for_biz") ?? "FOR BUSINESS", sub: "Data Feed · Price Intelligence · Cross-Border Analytics", color: "#FFD600" },
          { label: t("hero_for_agents") ?? "FOR AI AGENTS", sub: "12 MCP Tools · Autonomous Checkout · Natural Language", color: "#FF6B35" },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-[6px] sm:gap-[8px] h-[32px] sm:h-[36px] px-[10px] sm:px-[14px] bg-[#0F0F0F] border border-[#1D1D1D] group-hover:border-[#2A2A2A] transition-colors">
            <div className="w-[5px] h-[5px] rounded-full shrink-0" style={{ backgroundColor: item.color }} />
            <div className="flex items-baseline gap-[6px] sm:gap-[8px]">
              <span className="font-ibm-mono text-[7px] sm:text-[8px] font-bold tracking-[1px]" style={{ color: item.color }}>{item.label}</span>
              <span className="font-ibm-mono text-[7px] sm:text-[8px] text-[#555] tracking-[0.5px] hidden sm:inline">{item.sub}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="h-8 sm:h-10 md:h-[48px]" />
      <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 md:gap-[16px] w-full sm:w-auto px-2 sm:px-0">
        <a href="https://github.com/Treevu-ai/cli-market-latam"
          className="flex items-center justify-center w-full sm:w-[240px] h-[52px] sm:h-[56px] bg-[#00FF88] hover:bg-[#00cc6a] active:scale-[0.98] transition-all group-hover:shadow-[0_0_24px_rgba(0,255,136,0.2)]">
          <span className="font-grotesk text-[11px] sm:text-[12px] font-bold text-[#0A0A0A] tracking-[1.5px] sm:tracking-[2px]">{t("hero_cta")}</span>
        </a>
        <button onClick={() => { const el = document.getElementById("features"); if (el) el.scrollIntoView({ behavior: "smooth" }); }}
          className="flex items-center justify-center w-full sm:w-[200px] h-[52px] sm:h-[56px] bg-[#0A0A0A] border-2 border-[#3D3D3D] hover:border-[#888888] active:scale-[0.98] transition-all cursor-pointer group-hover:border-[#555]">
          <span className="font-ibm-mono text-[11px] sm:text-[12px] text-[#888888] tracking-[1px] sm:tracking-[2px] group-hover:text-[#BBBBBB] transition-colors">{t("hero_cta2")}</span>
        </button>
      </div>
      <div className="h-5 sm:h-6 md:h-[24px]" />
      <p className="font-ibm-mono text-[10px] sm:text-[11px] text-[#555555] tracking-[1px] sm:tracking-[2px] text-center break-all px-4 max-w-full group-hover:text-[#777] transition-colors duration-500">
        pip install git+https://github.com/Treevu-ai/cli-market-latam.git
      </p>
      <CollabCursors />
    </section>
  );
}
