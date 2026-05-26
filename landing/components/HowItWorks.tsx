"use client";
import { useRef } from "react";
import { useLang } from "@/lib/LanguageContext";

const steps = [
  { cmd: "pip install cli-market", out_es: "cl i-market 1.3.0 instalado correctamente", out_en: "Successfully installed cli-market 1.3.0", label: "Install" },
  { cmd: "market login", out_es: "Autenticado — 60 comercios listos", out_en: "Authenticated — 60 retailers ready", label: "Login" },
  { cmd: "market search \"leche\" --country PE", out_es: "Wong S/4.20 · Metro S/3.90 · Plaza Vea S/4.50", out_en: "Wong S/4.20 · Metro S/3.90 · Plaza Vea S/4.50", label: "Search" },
  { cmd: "market compare \"arroz\"", out_es: "Mejor: Metro S/2.80 · Ahorro: S/0.70/unidad", out_en: "Best: Metro S/2.80 · Savings: S/0.70/unit", label: "Compare" },
  { cmd: "market add 1 --qty 2", out_es: "2x Leche Gloria → carrito", out_en: "2x Milk → cart", label: "Add" },
  { cmd: "market checkout --payment yape", out_es: "✓ Orden confirmada · QR generado", out_en: "✓ Order confirmed · QR generated", label: "Checkout" },
];

export default function HowItWorks() {
  const { t: _t, lang } = useLang();
  const isES = lang === "es";
  const ref = useRef<HTMLDivElement>(null);

  return (
    <section id="how" className="relative bg-[#e8ebe6] py-20 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#868685] font-mono uppercase tracking-[0.15em] mb-8">{_t("how_label")}</p>
        <h2 className="text-[24px] font-medium text-[#0e0f0c] mb-3 tracking-tight">{_t("how_title")}</h2>
        <p className="text-sm text-[#454745] max-w-md mx-auto mb-12">{_t("how_subtitle")}</p>

        {/* Single terminal flow */}
        <div ref={ref} className="bg-[#e8ebe6] border border-[#c5edab] rounded-lg overflow-hidden text-left">
          <div className="flex items-center gap-1.5 px-4 py-2.5 border-b border-[#fafafa]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" />
            <span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
            <span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
            <span className="text-[10px] text-[#868685] font-mono ml-2 uppercase tracking-wider">
              cli-market — bash
            </span>
          </div>
          <div className="p-4 font-mono text-[12px] leading-relaxed space-y-2">
            {steps.map((s, i) => (
              <div key={i} className="group">
                <div className="flex items-start gap-2">
                  <span className="text-[#868685] select-none shrink-0 mt-[1px]">$</span>
                  <span className="text-[#454745]">{s.cmd}</span>
                </div>
                <div className="flex items-start gap-2 mt-0.5">
                  <span className="w-3 shrink-0" />
                  <span className="text-[#868685] text-[11px]">{isES ? s.out_es : s.out_en}</span>
                </div>
              </div>
            ))}
            <div className="flex items-center gap-2 pt-1">
              <span className="text-[#868685]">$</span>
              <span className="inline-block w-[6px] h-[14px] bg-[#a3a3a3] animate-pulse rounded-sm" />
            </div>
          </div>
        </div>

        <p className="mt-8 text-[10px] text-[#868685] font-mono uppercase tracking-[0.15em]">{_t("how_footer")}</p>
      </div>
    </section>
  );
}
