"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";

export default function AgentDispatch() {
  const { t: _t, lang } = useLang();
  const isES = lang === "es";
  const [open, setOpen] = useState(0);

  const steps = [
    { titleKey: "agent_step1_title", descKey: "agent_step1_desc", num: "01" },
    { titleKey: "agent_step2_title", descKey: "agent_step2_desc", num: "02" },
    { titleKey: "agent_step3_title", descKey: "agent_step3_desc", num: "03" },
  ];

  return (
    <section className="relative bg-[#e8ebe6] py-20 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6">
        <div className="text-center mb-12">
          <p className="text-xs text-[#454745] font-medium uppercase tracking-[0.15em] mb-8">
            {isES ? "Para agentes" : "For agents"}
          </p>
          <h2 className="text-[24px] font-medium text-[#0e0f0c] tracking-tight">
            {isES ? "Infraestructura de comercio y precios para agentes." : "Commerce and pricing infrastructure for agents."}
          </h2>
        </div>

        <div className="space-y-2 max-w-[560px] mx-auto">
          {steps.map((s, i) => (
            <div key={i}>
              <button
                onClick={() => setOpen(open === i ? -1 : i)}
                className="w-full flex items-center gap-4 px-4 py-3 bg-white rounded-3xl border border-[#c5edab] hover:bg-[#e2f6d5] transition-colors text-left"
              >
                <span className="text-xs font-bold text-[#9fe870] font-mono w-6">{s.num}</span>
                <span className="text-sm font-medium text-[#0e0f0c] flex-1">{_t(s.titleKey)}</span>
                <svg className={`w-4 h-4 text-[#868685] transition-transform ${open === i ? "rotate-180" : ""}`}
                  fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </button>
              {open === i && (
                <div className="mt-1 px-4 py-3 text-sm text-[#454745] leading-relaxed">
                  {_t(s.descKey)}
                </div>
              )}
            </div>
          ))}
        </div>

        <p className="mt-8 text-center text-sm text-[#0e0f0c] font-semibold">
          {isES ? "Tu agente puede comparar precios, optimizar canastas y comprar solo. Hoy." : "Your agent can compare prices, optimize baskets, and buy on its own. Today."}
        </p>
      </div>
    </section>
  );
}
