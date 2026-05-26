"use client";
import { useState, useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";

const linkKeys = ["nav_stats","nav_terminal","nav_how","nav_features","nav_pricing","nav_faq"];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { lang, setLang, t: _t } = useLang();
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("theme");
    const prefers = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = stored === "dark" || (!stored && prefers);
    setDark(isDark);
    document.documentElement.classList.toggle("dark", isDark);
  }, []);

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const navLabels: Record<string,string> = {
    nav_stats: _t("nav_stats"), nav_terminal: _t("nav_terminal"), nav_how: _t("nav_how"),
    nav_features: _t("nav_features"), nav_pricing: _t("nav_pricing"), nav_faq: _t("nav_faq"),
  };

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
      scrolled ? "bg-[var(--wise-canvas-soft)]/90 backdrop-blur-md border-b border-[#c5edab]" : "bg-[var(--wise-canvas-soft)] border-b border-transparent"
    }`}>
      <div className="max-w-[720px] mx-auto px-6 flex items-center justify-between h-14">
        {/* Logo */}
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

        {/* Nav links */}
        <div className="hidden md:flex items-center gap-5">
          {linkKeys.map(k => (
            <a key={k} href={`#${k.replace("nav_","")}`}
               className="text-[11px] font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors">
              {navLabels[k]}
            </a>
          ))}
          <span className="text-[#d4d4d4]">|</span>
          <button onClick={toggleTheme}
            className="text-sm font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors cursor-pointer"
            title={dark ? "Light" : "Dark"}>
            {dark ? "☀" : "☾"}
          </button>
          <span className="text-[#d4d4d4]">|</span>
          <button onClick={() => setLang(lang === "es" ? "en" : "es")}
            className="text-[11px] font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors cursor-pointer">
            {lang === "es" ? "EN" : "ES"}
          </button>
        </div>

        {/* Mobile menu */}
        <div className="md:hidden flex items-center gap-3">
          <button onClick={() => setLang(lang === "es" ? "en" : "es")}
            className="text-[11px] font-medium text-[var(--wise-body)] cursor-pointer">
            {lang === "es" ? "EN" : "ES"}
          </button>
          <button onClick={() => setOpen(!open)}
            className="text-[var(--wise-ink)] text-lg cursor-pointer font-medium">
            {open ? "×" : "☰"}
          </button>
        </div>
      </div>

      {/* Mobile dropdown */}
      {open && (
        <div className="md:hidden bg-[var(--wise-canvas-soft)] border-t border-[#c5edab] px-6 py-4 flex flex-col gap-3">
          {linkKeys.map(k => (
            <a key={k} href={`#${k.replace("nav_","")}`} onClick={() => setOpen(false)}
               className="text-sm text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors">
              {navLabels[k]}
            </a>
          ))}
        </div>
      )}
    </nav>
  );
}
