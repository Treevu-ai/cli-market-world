"use client";
import { useState, useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";

const navItems = [
  { id: "api", es: "API", en: "API" },
  { id: "coverage", es: "Retailers", en: "Retailers" },
  { id: "casos", es: "MCP Tools", en: "MCP Tools" },
  { id: "pricing", es: "Precios", en: "Pricing" },
  { id: "retailers", es: "Listar tienda", en: "List store" },
  { id: "faq", es: "FAQ", en: "FAQ" },
  { id: "docs", href: "/docs", es: "Docs", en: "Docs" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { lang, setLang } = useLang();
  const isES = lang === "es";

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  const close = () => setOpen(false);
  const docsCtaLabel = isES ? "Docs" : "Docs";

  return (
    <header
      className="fixed top-0 w-full z-50 bg-[var(--cm-surface)]/80 backdrop-blur-xl border-b border-[var(--cm-outline-variant)]/30 shadow-[0_0_15px_rgba(58,254,207,0.1)] transition-all duration-300"
      aria-label={isES ? "Navegación principal" : "Main navigation"}
    >
      <div className="landing-container-wide flex justify-between items-center py-4 gap-4">
        <a href="/" className="font-display text-xl font-bold text-white tracking-tighter shrink-0" aria-label="CLI Market home">
          CLI Market
        </a>

        <nav className="hidden lg:flex items-center gap-8" aria-label={isES ? "Secciones" : "Sections"}>
          {navItems.map(({ id, es, en, href }) => (
            <a
              key={id}
              href={href ?? `#${id}`}
              className="font-label-caps text-[var(--cm-on-surface-variant)] hover:text-white transition-colors"
            >
              {isES ? es : en}
            </a>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-4 shrink-0">
          <a
            href="https://github.com/Treevu-ai/cli-market-world"
            target="_blank"
            rel="noopener noreferrer"
            className="font-label-caps text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors"
          >
            GitHub
          </a>
          <button
            type="button"
            onClick={() => setLang(isES ? "en" : "es")}
            className="font-label-caps text-[var(--cm-on-surface-variant)] hover:text-white cursor-pointer"
          >
            {isES ? "EN" : "ES"}
          </button>
          <a
            href="/docs"
            className="bg-[var(--cm-mint)] text-[var(--cm-on-mint)] px-6 py-2 font-label-caps hover:shadow-[0_0_10px_rgba(58,254,207,0.3)] transition-all"
          >
            {docsCtaLabel}
          </a>
        </div>

        <button
          type="button"
          onClick={() => setOpen(!open)}
          className="md:hidden text-white p-2"
          aria-expanded={open}
          aria-label={isES ? "Menú" : "Menu"}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            {open ? <path d="M18 6L6 18M6 6l12 12" /> : <path d="M3 12h18M3 6h18M3 18h18" />}
          </svg>
        </button>
      </div>

      {open && (
        <div className="md:hidden bg-[var(--cm-surface)] border-t border-[var(--cm-outline-variant)]/30 px-6 py-4 flex flex-col gap-3">
          {navItems.map(({ id, es, en, href }) => (
            <a
              key={id}
              href={href ?? `#${id}`}
              onClick={close}
              className="font-label-caps text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors py-1"
            >
              {isES ? es : en}
            </a>
          ))}
          <a
            href="https://github.com/Treevu-ai/cli-market-world"
            target="_blank"
            rel="noopener noreferrer"
            onClick={close}
            className="font-label-caps text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors py-1"
          >
            GitHub
          </a>
          <a
            href="/docs"
            onClick={close}
            className="inline-flex items-center justify-center bg-[var(--cm-mint)] text-[var(--cm-on-mint)] font-label-caps px-6 py-3 cyber-glow-mint"
          >
            {docsCtaLabel}
          </a>
          <button
            type="button"
            onClick={() => setLang(isES ? "en" : "es")}
            className="font-label-caps text-[var(--cm-on-surface-variant)] cursor-pointer text-left py-1"
          >
            {isES ? "EN" : "ES"}
          </button>
        </div>
      )}
    </header>
  );
}
