"use client";

import { useLang } from "@/lib/LanguageContext";

export default function LangToggle({ className = "" }: { className?: string }) {
  const { lang, setLang } = useLang();

  return (
    <div
      className={`inline-flex rounded-full border border-[var(--cm-outline-variant)]/60 p-0.5 text-xs font-semibold ${className}`}
      role="group"
      aria-label="Language"
    >
      <button
        type="button"
        onClick={() => setLang("es")}
        className={`px-2.5 py-1 rounded-full transition-colors ${
          lang === "es" ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)]" : "text-[var(--cm-on-surface-variant)]"
        }`}
      >
        ES
      </button>
      <button
        type="button"
        onClick={() => setLang("en")}
        className={`px-2.5 py-1 rounded-full transition-colors ${
          lang === "en" ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)]" : "text-[var(--cm-on-surface-variant)]"
        }`}
      >
        EN
      </button>
    </div>
  );
}
