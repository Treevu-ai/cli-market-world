"use client";
import { useLang } from "@/lib/LanguageContext";
export default function HowItWorks() {
  const { t: _t } = useLang();
  return (
    <section id="how" className="relative flex flex-col w-full bg-[#090909] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#00FF88]/40"/>{_t("how_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">{_t("how_title")}</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">{_t("how_subtitle")}</p>
      </div>
      <p className="text-white/20 font-mono text-[10px] uppercase tracking-widest">{_t("how_footer")}</p>
    </section>
  );
}
