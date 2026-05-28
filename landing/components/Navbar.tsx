"use client";
import { useState, useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";

const linkKeys = ["nav_stats", "nav_terminal", "nav_retailers", "nav_coverage", "nav_pricing", "nav_faq"];
const linkLabels: Record<string, { es: string; en: string }> = {
  nav_stats: { es: "Escala", en: "Scale" },
  nav_how: { es: "Flujo", en: "Flow" },
  nav_terminal: { es: "Terminal", en: "Terminal" },
  nav_api: { es: "API", en: "API" },
  nav_features: { es: "Capacidades", en: "Capabilities" },
  nav_retailers: { es: "Retailers", en: "Retailers" },
  nav_coverage: { es: "Cobertura", en: "Coverage" },
  nav_data: { es: "Data Moat", en: "Data Moat" },
  nav_pricing: { es: "Precios", en: "Pricing" },
  nav_faq: { es: "FAQ", en: "FAQ" },
  nav_about: { es: "Acerca", en: "About" },
};

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { lang, setLang, t: _t } = useLang();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const close = () => setOpen(false);

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 md:hidden ${
      scrolled ? "bg-[var(--wise-canvas-soft)]/90 backdrop-blur-md border-b border-[var(--wise-green-pale)]" : "bg-[var(--wise-canvas-soft)] border-b border-transparent"
    }`}>
      <div className="max-w-[720px] mx-auto px-6 flex items-center justify-between h-14">
        <a href="/" className="flex items-center gap-2 text-[var(--wise-ink)]">
          <svg width="24" height="24" viewBox="0 0 32 32" fill="none" className="text-[var(--wise-ink)]">
            <path d="M3 6l2 2 3 12h12l4-8H11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <circle cx="11" cy="24" r="2" stroke="currentColor" strokeWidth="1.5"/>
            <circle cx="20" cy="24" r="2" stroke="currentColor" strokeWidth="1.5"/>
            <rect x="11" y="10" width="7" height="1.5" rx="0.5" fill="currentColor"/>
            <rect x="12" y="13" width="5" height="1.5" rx="0.5" fill="currentColor"/>
            <rect x="13" y="16" width="3" height="1.5" rx="0.5" fill="currentColor"/>
            <rect x="19" y="10" width="1" height="1.5" rx="0.5" fill="currentColor">
              <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
            </rect>
          </svg>
          <span className="font-medium text-sm tracking-tight">CLI Market</span>
        </a>

        <div className="hidden md:flex items-center gap-5">
          {linkKeys.map((k) => (
            <a key={k} href={`#${k.replace("nav_", "")}`} onClick={close}
               className="text-[11px] font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors">
              {lang === "es" ? linkLabels[k].es : linkLabels[k].en}
            </a>
          ))}
          <span className="text-[var(--wise-mute)]">|</span>
          <button onClick={() => setLang(lang === "es" ? "en" : "es")}
            className="text-[11px] font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors cursor-pointer">
            {lang === "es" ? "EN" : "ES"}
          </button>
        </div>

        <button onClick={() => setOpen(!open)} className="md:hidden text-[var(--wise-ink)] p-2">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {open ? <path d="M18 6L6 18M6 6l12 12"/> : <path d="M3 12h18M3 6h18M3 18h18"/>}
          </svg>
        </button>
      </div>

      {open && (
        <div className="md:hidden bg-[var(--wise-canvas-soft)] border-t border-[var(--wise-green-pale)] px-6 py-4 flex flex-col gap-3">
          {linkKeys.map((k) => (
            <a key={k} href={`#${k.replace("nav_", "")}`} onClick={close}
               className="text-sm font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors">
              {lang === "es" ? linkLabels[k].es : linkLabels[k].en}
            </a>
          ))}
          <button onClick={() => setLang(lang === "es" ? "en" : "es")}
            className="text-[11px] font-medium text-[var(--wise-body)] cursor-pointer">
            {lang === "es" ? "EN" : "ES"}
          </button>
        </div>
      )}
    </nav>
  );
}
