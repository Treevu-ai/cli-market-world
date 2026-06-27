"use client";

import { useLang } from "@/lib/LanguageContext";
import { CTA } from "@/lib/ctaCopy";

export default function BuildSpokeHeader() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section className="landing-section pt-24 pb-4 scroll-mt-24">
      <div className="landing-container-wide text-center landing-section-header">
        <p className="section-eyebrow mb-4">CLI BUILD</p>
        <h1 className="section-title text-[var(--cm-on-surface)]">
          {isES ? "Inteligencia de retail programable" : "Programmable retail intelligence"}
        </h1>
        <p className="section-intro max-w-xl mx-auto">
          {isES
            ? "API, MCP y CLI sobre precios normalizados por kg/L — para agentes y productos con código."
            : "API, MCP, and CLI on kg/L-normalized prices — for agents and code-first products."}
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <a href={CTA.getApiKey.href} className="btn-mint">
            {isES ? CTA.getApiKey.es : CTA.getApiKey.en}
          </a>
          <a href={CTA.watchDemo.href} className="btn-outline">
            {isES ? CTA.watchDemo.es : CTA.watchDemo.en}
          </a>
        </div>
      </div>
    </section>
  );
}
