"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";

export default function AgentDispatch() {
  const { t } = useLang();
  const [open, setOpen] = useState(0); // 0 = all closed

  const steps = [
    { titleKey: "agent_step1_title", descKey: "agent_step1_desc", num: "01" },
    { titleKey: "agent_step2_title", descKey: "agent_step2_desc", num: "02" },
    { titleKey: "agent_step3_title", descKey: "agent_step3_desc", num: "03" },
  ];

  return (
    <section id="agents" className="relative flex flex-col w-full bg-black py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#3cffd0]/40"/>{t("agent_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05]">{t("agent_title")}</h2>
      </div>
      <div className="flex flex-col gap-4 max-w-[900px]">
        {steps.map((s, i) => (
          <div key={i} className="bg-[#131313] border border-[#2d2d2d] overflow-hidden">
            <button onClick={() => setOpen(open === i ? -1 : i)} className="w-full flex items-center gap-4 px-6 py-4 text-left">
              <span className="text-[#3cffd0] font-mono text-sm font-bold">{s.num}</span>
              <h3 className="font-grotesk text-base font-bold text-white">{t(s.titleKey)}</h3>
              <span className="ml-auto text-[#3cffd0] text-lg" style={{transform: open===i ? "rotate(45deg)" : "rotate(0)", transition: "transform 0.2s"}}>+</span>
            </button>
            {open === i && (
              <div className="px-6 pb-5 pl-14">
                <p className="text-[#888] text-sm font-sans leading-relaxed">{t(s.descKey)}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
