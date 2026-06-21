"use client";

import { useLang } from "@/lib/LanguageContext";

const AI_TOOLS = ["Claude", "GPT", "Cursor", "LangChain"];

export default function TrustBar() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <div
      className="w-full border-b border-[#27272A] bg-[#111113] py-4 overflow-hidden"
      aria-label={isES ? "Herramientas compatibles" : "Compatible tools"}
    >
      <div className="landing-container-wide flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
        <span className="text-[11px] font-mono uppercase tracking-widest text-[#A1A1AA] shrink-0">
          {isES ? "Usado por equipos que construyen con" : "Trusted by builders using"}
        </span>
        <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
          {AI_TOOLS.map((tool) => (
            <span
              key={tool}
              className="text-sm font-semibold text-[#FAFAFA] hover:text-[#7CFF5B] transition-colors cursor-default select-none"
            >
              {tool}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
