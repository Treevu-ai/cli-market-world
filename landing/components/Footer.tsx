"use client";
import { useLang } from "@/lib/LanguageContext";

export default function Footer() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <footer className="bg-[var(--wise-canvas-soft)] border-t border-[#c5edab] py-12">
      <div className="max-w-[720px] mx-auto px-6 flex flex-col items-center gap-6 text-center">

        {/* Logo */}
        <div className="flex items-center gap-2 text-[var(--wise-ink)]">
          <svg width="20" height="20" viewBox="0 0 32 32" fill="none" className="text-[var(--wise-ink)]">
            <path d="M3 6l2 2 3 12h12l4-8H11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <circle cx="11" cy="24" r="2" stroke="currentColor" strokeWidth="1.5"/>
            <circle cx="20" cy="24" r="2" stroke="currentColor" strokeWidth="1.5"/>
            <rect x="11" y="10" width="7" height="1.5" rx="0.5" fill="currentColor"/>
            <rect x="12" y="13" width="5" height="1.5" rx="0.5" fill="currentColor"/>
          </svg>
          <span className="font-medium text-xs tracking-tight">CLI Market</span>
        </div>

        {/* Links */}
        <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-xs text-[var(--wise-body)]">
          <a href="#stats" className="hover:text-[var(--wise-ink)] transition-colors">{isES ? "Escala" : "Scale"}</a>
          <a href="#how" className="hover:text-[var(--wise-ink)] transition-colors">{isES ? "Flujo" : "Flow"}</a>
          <a href="#terminal" className="hover:text-[var(--wise-ink)] transition-colors">{isES ? "Terminal" : "Terminal"}</a>
          <a href="#api" className="hover:text-[var(--wise-ink)] transition-colors">API</a>
          <a href="#features" className="hover:text-[var(--wise-ink)] transition-colors">{isES ? "Capacidades" : "Capabilities"}</a>
          <a href="#coverage" className="hover:text-[var(--wise-ink)] transition-colors">{isES ? "Cobertura" : "Coverage"}</a>
          <a href="#data" className="hover:text-[var(--wise-ink)] transition-colors">Data Moat</a>
          <a href="#pricing" className="hover:text-[var(--wise-ink)] transition-colors">{isES ? "Precios" : "Pricing"}</a>
          <a href="#faq" className="hover:text-[var(--wise-ink)] transition-colors">FAQ</a>
          <a href="#about" className="hover:text-[var(--wise-ink)] transition-colors">{isES ? "Acerca" : "About"}</a>
          <span className="text-[#c5edab]">·</span>
          <a href="/retailers" className="hover:text-[var(--wise-ink)] transition-colors">For Retailers</a>
          <a href="https://github.com/Treevu-ai/cli-market-world" className="hover:text-[var(--wise-ink)] transition-colors">GitHub</a>
          <a href="https://pypi.org/project/cli-market/" className="hover:text-[var(--wise-ink)] transition-colors">PyPI</a>
          <a href="mailto:hello@cli-market.dev" className="hover:text-[var(--wise-ink)] transition-colors">{isES ? "Contacto" : "Contact"}</a>
        </div>

        <p className="text-[10px] text-[var(--wise-body)] font-mono">
          {isES ? "30 comercios · 7 países · 3 plataformas · 13K precios · MIT License" : "30 retailers · 7 countries · 3 platforms · 13K prices · MIT License"}
        </p>
      </div>
    </footer>
  );
}
