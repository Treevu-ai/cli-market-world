"use client";
import { useLang } from "@/lib/LanguageContext";

export default function Hero() {
  const { t: _t } = useLang();

  return (
    <section className="relative min-h-screen flex flex-col justify-center items-center bg-white overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-px bg-[#e5e5e5]" />
      <div className="relative z-10 w-full max-w-[720px] mx-auto px-6 py-20 lg:py-32 text-center">

        {/* Install snippet — signature element */}
        <div className="mb-8 inline-flex items-center gap-2 rounded-full bg-[#fafafa] px-5 py-2.5">
          <span className="w-3 h-3 rounded-full bg-[#27c93f]" />
          <span className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
          <span className="w-3 h-3 rounded-full bg-[#ff5f56]" />
          <code className="font-mono text-sm text-[#525252] ml-3">pip install cli-market</code>
          <button
            onClick={() => navigator.clipboard.writeText("pip install cli-market")}
            className="ml-2 text-[#a3a3a3] hover:text-black transition-colors"
            title="Copiar"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          </button>
        </div>

        {/* Headline */}
        <h1 className="text-[36px] leading-[1.11] font-medium text-black mb-6 tracking-tight">
          {_t("hero_h1")}
        </h1>

        {/* Subhead */}
        <p className="text-base text-[#737373] max-w-md mx-auto mb-10 leading-relaxed">
          {_t("hero_sub")}
        </p>

        {/* CTA pills */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <a href="https://github.com/Treevu-ai/cli-market-world"
             className="inline-flex items-center gap-2 rounded-full bg-black text-white text-sm font-medium px-5 py-2.5 h-9 hover:bg-[#090909] transition-colors">
            {_t("hero_install")}
            <span className="opacity-50">→</span>
          </a>
          <a href="#terminal"
             className="inline-flex items-center gap-2 rounded-full bg-white text-black text-sm font-medium px-5 py-2.5 h-9 border border-[#e5e5e5] hover:bg-[#fafafa] transition-colors">
            {_t("hero_cov")}
          </a>
        </div>

        {/* Stats row */}
        <div className="mt-16 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-[#737373] font-mono">
          <span><strong className="text-black">60</strong> retailers</span>
          <span className="text-[#d4d4d4] hidden sm:inline">·</span>
          <span><strong className="text-black">11</strong> países</span>
          <span className="text-[#d4d4d4] hidden sm:inline">·</span>
          <span><strong className="text-black">36</strong> MCP tools</span>
          <span className="text-[#d4d4d4] hidden sm:inline">·</span>
          <span><strong className="text-black">3</strong> plataformas</span>
        </div>
      </div>
    </section>
  );
}
