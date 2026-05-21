"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";

const faqKeys = [
  { qKey: "faq1_q", aKey: "faq1_a", defaultOpen: true },
  { qKey: "faq2_q", aKey: "faq2_a" },
  { qKey: "faq3_q", aKey: "faq3_a" },
  { qKey: "faq4_q", aKey: "faq4_a" },
  { qKey: "faq5_q", aKey: "faq5_a" },
  { qKey: "faq6_q", aKey: "faq6_a" },
];

export default function FAQ() {
  const { t } = useLang();
  const [open, setOpen] = useState(0);

  return (
    <section id="faq" className="relative flex flex-col w-full bg-black py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#00FF88]/40"/>FAQ</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05]">{t("faq_title")}</h2>
      </div>
      <div className="flex flex-col gap-4 max-w-[800px]">
        {faqKeys.map((f, i) => (
          <div key={i} className="bg-[#0A0A0A] border border-[#1A1A1A] overflow-hidden">
            <button onClick={() => setOpen(open === i ? -1 : i)} className="w-full flex justify-between items-center px-6 py-4 text-left">
              <span className="font-grotesk text-sm font-bold text-white">{t(f.qKey)}</span>
              <span className="text-[#00FF88] text-lg" style={{transform: open===i ? "rotate(45deg)" : "rotate(0)", transition: "transform 0.2s"}}>+</span>
            </button>
            {open === i && (
              <div className="px-6 pb-5">
                <p className="text-[#888] text-sm font-sans leading-relaxed">{t(f.aKey)}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
