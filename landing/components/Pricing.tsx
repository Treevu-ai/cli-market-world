"use client";
import { useLang } from "@/lib/LanguageContext";

export default function Pricing() {
  const { t } = useLang();
  return (
    <section id="pricing" className="flex flex-col w-full bg-[#060606] py-12 px-4 sm:py-16 sm:px-6 md:py-[80px] md:px-[120px] gap-8 sm:gap-10 md:gap-[48px]">
      <div className="flex flex-col gap-[12px] w-full">
        <span className="font-mono text-[9px] sm:text-[10px] md:text-[11px] font-bold text-[#FFD600] tracking-[2px] md:tracking-[3px] uppercase">{t("pricing_label")}</span>
        <h2 className="font-grotesk text-[26px] sm:text-[32px] md:text-[48px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.05]">
          {t("pricing_title")}
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full max-w-[800px]">
        {/* Free */}
        <div className="flex flex-col gap-4 p-6 bg-[#0F0F0F] border border-[#1D1D1D]">
          <span className="font-mono text-[11px] font-bold text-[#00FF88] tracking-[2px] uppercase">{t("pricing_free_title")}</span>
          <div className="flex items-baseline gap-1">
            <span className="font-grotesk text-4xl font-bold text-white">{t("pricing_free_price")}</span>
            <span className="font-mono text-xs text-[#555]">{t("pricing_free_period")}</span>
          </div>
          <ul className="flex flex-col gap-2 font-mono text-xs text-[#888]">
            <li>· {t("pricing_free_1")}</li>
            <li>· {t("pricing_free_2")}</li>
            <li>· {t("pricing_free_3")}</li>
            <li>· {t("pricing_free_4")}</li>
            <li>· {t("pricing_free_5")}</li>
          </ul>
          <a href="https://github.com/Treevu-ai/cli-market-world"
            className="inline-flex items-center justify-center gap-2 border border-[#00FF88]/40 px-6 py-3 font-mono text-[11px] uppercase tracking-widest text-[#00FF88] hover:bg-[#00FF88]/10 transition-all mt-2">
            {t("pricing_free_cta")}
          </a>
        </div>

        {/* Enterprise */}
        <div className="flex flex-col gap-4 p-6 bg-[#0F0F0F] border border-[#1D1D1D]">
          <span className="font-mono text-[11px] font-bold text-[#FFD600] tracking-[2px] uppercase">{t("pricing_pro_title")}</span>
          <div className="flex items-baseline gap-1">
            <span className="font-grotesk text-4xl font-bold text-white">{t("pricing_pro_price")}</span>
            <span className="font-mono text-xs text-[#555]">{t("pricing_pro_period")}</span>
          </div>
          <ul className="flex flex-col gap-2 font-mono text-xs text-[#888]">
            <li>· {t("pricing_pro_1")}</li>
            <li>· {t("pricing_pro_2")}</li>
            <li>· {t("pricing_pro_3")}</li>
            <li>· {t("pricing_pro_4")}</li>
            <li>· {t("pricing_pro_5")}</li>
          </ul>
          <a href="mailto:hello@cli-market.dev"
            className="inline-flex items-center justify-center gap-2 border border-[#FFD600]/40 px-6 py-3 font-mono text-[11px] uppercase tracking-widest text-[#FFD600] hover:bg-[#FFD600]/10 transition-all mt-2">
            {t("pricing_pro_cta")}
          </a>
        </div>
      </div>
    </section>
  );
}
