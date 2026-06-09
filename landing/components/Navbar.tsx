"use client";
import { useState, useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { SECTION_NAV } from "@/lib/siteNav";

function Logo() {
  return (
    <svg width="24" height="24" viewBox="0 0 32 32" fill="none" className="text-[var(--cm-mint)] shrink-0" aria-hidden="true">
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
  const mobileCta = isES ? "API gratis →" : "Free API →";

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
      scrolled ? "bg-[var(--cm-background)]/90 backdrop-blur-md border-b border-[var(--cm-outline-variant)]/30" : "bg-[var(--cm-background)] border-b border-transparent"
    }`} aria-label={isES ? "Navegación principal" : "Main navigation"}>
      <div className="landing-container-wide flex items-center justify-between h-14 md:h-16 gap-4">
        <a href="/" className="flex items-center gap-2 shrink-0" aria-label="CLI Market home">
          <Logo />
          <span className="font-medium text-sm text-white tracking-tight">CLI Market</span>
        </a>

        <div className="hidden lg:flex items-center gap-5">
          {SECTION_NAV.map(({ id, es, en }) => (
            <a key={id} href={`/#${id}`}
               className="text-xs font-medium text-[var(--cm-on-surface-variant)] hover:text-white transition-colors whitespace-nowrap">
              {isES ? es : en}
            </a>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-3 shrink-0">
          <a
            href="/account"
            className="text-xs font-medium text-[var(--cm-on-surface-variant)] hover:text-white transition-colors"
          >
            {isES ? "Cuenta" : "Account"}
          </a>
          <a
            href={MARKET_STATS.pypiUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-medium text-[var(--cm-on-surface-variant)] hover:text-white transition-colors"
          >
            PyPI
          </a>
          <button onClick={() => setLang(isES ? "en" : "es")}
            className="text-xs font-medium text-[var(--cm-on-surface-variant)] hover:text-white cursor-pointer">
            {isES ? "EN" : "ES"}
          </button>
          <a
            href="/#api"
            className="inline-flex items-center rounded-3xl bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-xs font-semibold px-4 py-2 hover:brightness-110 transition-all whitespace-nowrap"
          >
            {primaryCta}
          </a>
        </div>

        <button onClick={() => setOpen(!open)} className="md:hidden text-white p-2" aria-expanded={open} aria-label={isES ? "Menú" : "Menu"}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            {open ? <path d="M18 6L6 18M6 6l12 12"/> : <path d="M3 12h18M3 6h18M3 18h18"/>}
          </svg>
        </button>
      </div>

      {open && (
        <div className="landing-mobile-menu md:hidden bg-[var(--cm-surface-low)] border-t border-[var(--cm-outline-variant)]/30 landing-container-wide py-4 flex flex-col gap-2 max-h-[calc(100dvh-3.5rem)] overflow-y-auto overscroll-contain safe-bottom">
          {SECTION_NAV.map(({ id, es, en }) => (
            <a key={id} href={`/#${id}`} onClick={close}
               className="text-sm font-medium text-[var(--cm-on-surface-variant)] hover:text-white transition-colors">
              {isES ? es : en}
            </a>
          ))}
          <a href="/account" onClick={close}
             className="text-sm font-medium text-[var(--cm-on-surface-variant)] hover:text-white transition-colors">
            {isES ? "Cuenta" : "Account"}
          </a>
          <a href={MARKET_STATS.pypiUrl} target="_blank" rel="noopener noreferrer" onClick={close}
             className="text-sm font-medium text-[var(--cm-on-surface-variant)] hover:text-white transition-colors">
            PyPI
          </a>
          <a href="/#api" onClick={close}
             className="inline-flex items-center justify-center rounded-3xl bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold px-6 py-3 mt-1">
            {mobileCta}
          </a>
          <button onClick={() => setLang(isES ? "en" : "es")}
            className="text-xs font-medium text-[var(--cm-on-surface-variant)] cursor-pointer text-left">
            {isES ? "EN" : "ES"}
          </button>
        </div>
      )}
    </nav>
  );
}
