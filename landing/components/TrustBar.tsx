"use client";

import { useLang } from "@/lib/LanguageContext";

const INTEGRATIONS = [
  { name: "Claude", category: "ai" },
  { name: "Cursor", category: "ai" },
  { name: "GPT-4o", category: "ai" },
  { name: "LangChain", category: "ai" },
  { name: "VTEX", category: "platform" },
  { name: "Shopify", category: "platform" },
  { name: "Any HTTP", category: "platform" },
];

export default function TrustBar() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <div
      className="w-full border-b border-[#e3e8ee] bg-white py-4 overflow-hidden"
      aria-label={isES ? "Integraciones compatibles" : "Compatible integrations"}
    >
      <div className="landing-container-wide flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
        <span className="text-[11px] font-mono uppercase tracking-widest text-[#a8c3de] shrink-0">
          {isES ? "Compatible con" : "Works with"}
        </span>
        <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
          {INTEGRATIONS.map((item) => (
            <span
              key={item.name}
              className="text-sm font-semibold text-[#64748d] hover:text-[#0d253d] transition-colors cursor-default select-none"
            >
              {item.name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
