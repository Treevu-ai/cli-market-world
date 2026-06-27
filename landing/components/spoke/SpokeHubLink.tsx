"use client";

import { useLang } from "@/lib/LanguageContext";

export default function SpokeHubLink() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <div className="landing-container-wide pb-2 -mt-2">
      <a
        href="/"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors"
      >
        <span aria-hidden="true">←</span>
        {isES ? "CLI Market — elegir otro perfil" : "CLI Market — choose another profile"}
      </a>
    </div>
  );
}
