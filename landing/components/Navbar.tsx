"use client";
import { useState, useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";

const navItems = [
  { id: "how", es: "Flujo", en: "Flow" },
  { id: "api", es: "API", en: "API" },
  { id: "coverage", es: "Cobertura", en: "Coverage" },
  { id: "casos", es: "Casos", en: "Use cases" },
  { id: "pricing", es: "Planes", en: "Pricing" },
  { id: "retailers", es: "Retailers", en: "Retailers" },
  { id: "faq", es: "FAQ", en: "FAQ" },
  { id: "contact", es: "Contacto", en: "Contact" },
];

function Logo() {
  return (
    <svg width="24" height="24" viewBox="0 0 32 32" fill="none" className="text-[var(--wise-ink)] shrink-0" aria-hidden="true">
      <path d="M3 6l2 2 3 12h12l4-8H11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="11" cy="24" r="2" stroke="currentColor" strokeWidth="1.5"/>
      <circle cx="20" cy="24" r="2" stroke="currentColor" strokeWidth="1.5"/>
      <rect x="11" y="10" width="7" height="1.5" rx="0.5" fill="currentColor"/>
      <rect x="12" y="13" width="5" height="1.5" rx="0.5" fill="currentColor"/>
      <rect x="13" y="16" width="3" height="1.5" rx="0.5" fill="currentColor"/>
    </svg>
  );
}

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { lang, setLang } = useLang();
  const isES = lang === "es";

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const close = () => setOpen(false);
  const primaryCta = isES ? "Empezar con la API — gratis →" : "Start with the API — free →";

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
      scrolled ? "bg-[var(--wise-canvas-soft)]/90 backdrop-blur-md border-b border-[var(--wise-green-pale)]" : "bg-[var(--wise-canvas-soft)] border-b border-transparent"
    }`} aria-label={isES ? "Navegación principal" : "Main navigation"}>
      <div className="landing-container flex items-center justify-between h-14 md:h-16 gap-4">
        <a href="/" className="flex items-center gap-2 text-[var(--wise-ink)] shrink-0" aria-label="CLI Market home">
          <Logo />
          <span className="font-medium text-sm tracking-tight">CLI Market</span>
        </a>

        <div className="hidden lg:flex items-center gap-5">
          {navItems.map(({ id, es, en }) => (
            <a key={id} href={`#${id}`}
               className="text-xs font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors whitespace-nowrap">
              {isES ? es : en}
            </a>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-3 shrink-0">
          <a
            href="https://github.com/Treevu-ai/cli-market-world"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors"
          >
            GitHub
          </a>
          <button onClick={() => setLang(isES ? "en" : "es")}
            className="text-xs font-medium text-[var(--wise-mute)] hover:text-[var(--wise-ink)] cursor-pointer">
            {isES ? "EN" : "ES"}
          </button>
          <a
            href="https://pypi.org/project/cli-market/"
            className="inline-flex items-center rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-xs font-semibold px-4 py-2 hover:bg-[var(--wise-green-hover)] transition-colors whitespace-nowrap"
          >
            {primaryCta}
          </a>
        </div>

        <button onClick={() => setOpen(!open)} className="md:hidden text-[var(--wise-ink)] p-2" aria-expanded={open} aria-label={isES ? "Menú" : "Menu"}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            {open ? <path d="M18 6L6 18M6 6l12 12"/> : <path d="M3 12h18M3 6h18M3 18h18"/>}
          </svg>
        </button>
      </div>

      {open && (
        <div className="md:hidden bg-[var(--wise-canvas-soft)] border-t border-[var(--wise-green-pale)] px-6 py-4 flex flex-col gap-3">
          {navItems.map(({ id, es, en }) => (
            <a key={id} href={`#${id}`} onClick={close}
               className="text-sm font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors">
              {isES ? es : en}
            </a>
          ))}
          <a href="https://github.com/Treevu-ai/cli-market-world" target="_blank" rel="noopener noreferrer" onClick={close}
             className="text-sm font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors">
            GitHub
          </a>
          <a href="https://pypi.org/project/cli-market/" onClick={close}
             className="inline-flex items-center justify-center rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-sm font-semibold px-6 py-3">
            {primaryCta}
          </a>
          <button onClick={() => setLang(isES ? "en" : "es")}
            className="text-xs font-medium text-[var(--wise-body)] cursor-pointer text-left">
            {isES ? "EN" : "ES"}
          </button>
        </div>
      )}
    </nav>
  );
}
