"use client";
import { useLang } from "@/lib/LanguageContext";

export default function FinalCTA() {
  const { t } = useLang();
  return (
    <section className="flex flex-col items-center w-full bg-[#0A0A0A] py-16 px-4 sm:py-20 sm:px-6 md:py-[100px] gap-8 sm:gap-10 border-t border-[#1A1A1A]">
      <div className="flex items-center justify-center gap-[6px] h-[28px] sm:h-[32px] px-[12px] sm:px-[16px] bg-[#1A1A1A] border border-[#00FF88]">
        <span className="font-mono text-[9px] sm:text-[11px] font-bold text-[#00FF88] tracking-[1px]">
          {t("cta_subtitle")}
        </span>
      </div>
      <h2 className="font-grotesk text-[32px] sm:text-[44px] md:text-[72px] font-bold text-[#F5F5F0] tracking-[-1px] leading-none text-center whitespace-pre-line">
        {t("cta_title")}
      </h2>
      <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4">
        <a href="https://github.com/Treevu-ai/cli-market-world"
          className="group inline-flex items-center gap-3 border border-[#333] px-6 py-3 font-mono text-[11px] uppercase tracking-widest text-[#AAA] hover:border-[#00FF88] hover:text-[#00FF88] transition-all">
          {t("cta_button")}
          <span className="transition-transform duration-300 group-hover:translate-x-1">→</span>
        </a>
        <a href="mailto:hello@cli-market.dev?subject=CLI%20Market&body=Hola%2C%20me%20interesa%20CLI%20Market."
          className="font-mono text-[11px] uppercase tracking-widest text-[#555] hover:text-[#888] transition-colors">
          {t("hero_contact")}
        </a>
      </div>
      <p className="font-mono text-[10px] sm:text-[11px] text-[#555] tracking-[1px] text-center break-all px-4 max-w-full">
        pip install cli-market
      </p>
    </section>
  );
}
