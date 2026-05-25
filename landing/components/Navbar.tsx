"use client";
import { useState, useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";

const linkKeys = ["nav_stats","nav_terminal","nav_how","nav_features","nav_coverage","nav_pricing","nav_faq"];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { lang, setLang, t: _t } = useLang();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const navLabels: Record<string,string> = {
    nav_stats: _t("nav_stats"), nav_terminal: _t("nav_terminal"), nav_how: _t("nav_how"),
    nav_features: _t("nav_features"), nav_coverage: _t("nav_coverage"), nav_pricing: _t("nav_pricing"), nav_faq: _t("nav_faq"),
  };

  return (
    <nav className={`fixed top-0 w-full z-50 transition-colors duration-300 ${scrolled ? "bg-black/80 backdrop-blur-md border-b border-[#2d2d2d]" : "bg-transparent"}`}>
      <div className="max-w-[1200px] mx-auto px-6 lg:px-12 flex items-center justify-between h-14">
        <a href="/" className="font-grotesk font-bold text-white text-lg tracking-tight">CLI Market</a>
        <div className="hidden md:flex items-center gap-6">
          {linkKeys.map(k => (
            <a key={k} href={`#${k.replace("nav_","")}`} className="text-[11px] font-mono text-[#555] hover:text-white transition-colors uppercase tracking-wider">{navLabels[k]}</a>
          ))}
          <button onClick={() => setLang(lang === "es" ? "en" : "es")} className="text-[11px] font-mono text-[#3cffd0] border border-[#3cffd0]/30 px-2 py-0.5 hover:bg-[#3cffd0]/10 transition-colors uppercase cursor-pointer">
            {lang === "es" ? "EN" : "ES"}
          </button>
          <a href="https://github.com/Treevu-ai/cli-market-world" className="text-[11px] font-mono text-[#888] hover:text-white transition-colors uppercase tracking-wider">{_t("nav_agents") === "Agentes" ? "GitHub" : "GitHub"}</a>
        </div>
        <div className="md:hidden flex items-center gap-3">
          <button onClick={() => setLang(lang === "es" ? "en" : "es")} className="text-[11px] font-mono text-[#3cffd0] border border-[#3cffd0]/30 px-2 py-0.5 cursor-pointer">{lang === "es" ? "EN" : "ES"}</button>
          <button onClick={() => setOpen(!open)} className="text-white text-xl cursor-pointer">{open ? "×" : "☰"}</button>
        </div>
      </div>
      {open && (
        <div className="md:hidden bg-black border-t border-[#2d2d2d] px-6 py-4 flex flex-col gap-3">
          {linkKeys.map(k => <a key={k} href={`#${k.replace("nav_","")}`} onClick={() => setOpen(false)} className="text-[11px] font-mono text-[#888] hover:text-white transition-colors uppercase tracking-wider">{navLabels[k]}</a>)}
        </div>
      )}
    </nav>
  );
}
