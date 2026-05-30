"use client";
import { useState, useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";

const items = [
  { id: "hero", es: "Inicio", en: "Home" },
  { id: "how", es: "Flujo", en: "Flow" },
  { id: "api", es: "API", en: "API" },
  { id: "coverage", es: "Cobertura", en: "Coverage" },
  { id: "casos", es: "Casos", en: "Use cases" },
  { id: "pricing", es: "Planes", en: "Pricing" },
  { id: "retailers", es: "Retailers", en: "Retailers" },
  { id: "faq", es: "FAQ", en: "FAQ" },
  { id: "contact", es: "Contacto", en: "Contact" },
];

export default function SideNav() {
  const [active, setActive] = useState("hero");
  const { lang, setLang } = useLang();
  const isES = lang === "es";

  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive(e.target.id);
        });
      },
      { threshold: 0.2 },
    );
    items.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) obs.observe(el);
    });
    return () => obs.disconnect();
  }, []);

  return (
    <nav
      className="fixed left-0 top-0 z-40 h-screen w-12 hidden md:flex flex-col justify-center bg-[var(--cm-background)]/60 backdrop-blur-sm border-r border-[var(--cm-outline-variant)]/20"
      aria-label={isES ? "Navegación de secciones" : "Section navigation"}
    >
      <div className="flex flex-col gap-4 px-3">
        {items.map(({ id, es, en }) => (
          <button
            key={id}
            type="button"
            onClick={() => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" })}
            className="group relative flex items-center"
            aria-label={isES ? es : en}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full transition-all duration-300 ${
                active === id
                  ? "bg-[var(--cm-mint)] scale-125 shadow-[0_0_8px_rgba(58,254,207,0.6)]"
                  : "bg-white/15 group-hover:bg-white/30"
              }`}
            />
            <span
              className={`absolute left-6 font-mono text-[9px] uppercase tracking-widest opacity-0 group-hover:opacity-100 group-hover:left-7 transition-all duration-200 whitespace-nowrap ${
                active === id ? "text-[var(--cm-mint)]" : "text-[var(--cm-on-surface-variant)]"
              }`}
            >
              {isES ? es : en}
            </span>
          </button>
        ))}
        <button
          type="button"
          onClick={() => setLang(isES ? "en" : "es")}
          className="mt-4 text-[8px] font-mono text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors"
        >
          {isES ? "EN" : "ES"}
        </button>
      </div>
    </nav>
  );
}
