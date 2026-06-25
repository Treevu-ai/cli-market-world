"use client";

import { useLang } from "@/lib/LanguageContext";

const AI_TOOLS = ["Claude", "GPT", "Cursor", "LangChain"];

export default function TrustBar() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <div
      className="w-full border-b border-[#e2e8f0] bg-[#ffffff] py-4 overflow-hidden"
      aria-label={isES ? "Herramientas compatibles" : "Compatible tools"}
    >
      <div className="landing-container-wide flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
        <span className="text-[11px] font-mono uppercase tracking-widest text-[#64748b] shrink-0">
          {isES ? "Usado por equipos que construyen con" : "Trusted by builders using"}
        </span>
        <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
          {AI_TOOLS.map((tool) => (
            <span
              key={tool}
              className="text-sm font-semibold text-[#0f172a] hover:text-[#ea580c] transition-colors cursor-default select-none"
            >
              {tool}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
