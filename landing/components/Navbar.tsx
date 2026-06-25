"use client";
import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { TOP_NAV, TOP_NAV_GROUP } from "@/lib/siteNav";
import { CTA } from "@/lib/ctaCopy";
import { useActiveSection } from "@/hooks/useActiveSection";

function Logo() {
  return (
    <svg width="24" height="24" viewBox="0 0 32 32" fill="none" className="text-[#ea580c] shrink-0" aria-hidden="true">
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
  const { active } = useActiveSection();
  const pathname = usePathname();
  const isES = lang === "es";
  const activeGroup =
    pathname?.startsWith("/docs")
      ? "docs"
      : pathname === "/"
        ? (TOP_NAV_GROUP[active] ?? active)
        : undefined;

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.classList.toggle("mobile-nav-open", open);
    return () => document.body.classList.remove("mobile-nav-open");
  }, [open]);

  const close = () => setOpen(false);
  const signUpCta = isES ? CTA.signUp.es : CTA.signUp.en;
  const signInCta = isES ? CTA.signIn.es : CTA.signIn.en;

  return (
    <nav
      className={`fixed top-0 w-full ${open ? "z-[110]" : "z-50"} transition-all duration-300`}
      style={{
        backgroundColor: scrolled ? "rgba(255,255,255,0.97)" : "rgba(255,255,255,0.95)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        borderBottom: "1px solid #e2e8f0",
      }}
      aria-label={isES ? "Navegación principal" : "Main navigation"}
    >
      <div className="landing-container-wide flex items-center justify-between h-14 md:h-20 gap-4">
        <a href="/" className="flex items-center gap-2 shrink-0" aria-label="CLI Market home">
          <Logo />
          <span className="font-mono text-sm text-[#0f172a] font-semibold" style={{ letterSpacing: "-0.5px" }}>CLI Market</span>
        </a>

        <div className="hidden lg:flex items-center gap-5">
          {TOP_NAV.map((item) => (
            <a
              key={item.id}
              href={item.href}
              aria-current={activeGroup === item.id ? "true" : undefined}
              className={`kimi-nav-link text-xs whitespace-nowrap transition-colors ${
                activeGroup === item.id ? "text-[#ea580c] font-semibold" : "text-[#64748b] hover:text-[#0f172a]"
              }`}
            >
              {isES ? item.es : item.en}
            </a>
          ))}
          <a
            href="/contact"
            className="kimi-nav-link text-xs whitespace-nowrap transition-colors text-[#64748b] hover:text-[#0f172a]"
          >
            {isES ? "Contacto" : "Contact"}
          </a>
        </div>

        <div className="hidden md:flex items-center gap-3 shrink-0">
          <a
            href={CTA.forRetailers.href}
            className="kimi-nav-link text-xs text-[#ea580c] font-medium whitespace-nowrap hover:text-[#f97316] transition-colors"
          >
            {isES ? CTA.forRetailers.es : CTA.forRetailers.en}
          </a>
          <button type="button" onClick={() => setLang(isES ? "en" : "es")}
            aria-label={isES ? "Switch to English" : "Cambiar a Español"}
            className="kimi-nav-link text-xs text-[#64748b] hover:text-[#0f172a] cursor-pointer transition-colors">
            {isES ? "EN" : "ES"}
          </button>
          <a
            href={CTA.signIn.href}
            className="kimi-nav-link text-xs text-[#64748b] hover:text-[#0f172a] whitespace-nowrap transition-colors"
          >
            {signInCta}
          </a>
          <a
            href={CTA.signUp.href}
            className="inline-flex items-center rounded-[10px] bg-[#ea580c] text-[#f8fafc] text-xs font-semibold px-4 py-2 hover:bg-[#f97316] transition-colors whitespace-nowrap shadow-sm"
          >
            {signUpCta}
          </a>
        </div>

        <button type="button" onClick={() => setOpen(!open)} className="md:hidden text-[#64748b] p-3" aria-expanded={open} aria-label={isES ? "Menú" : "Menu"}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            {open ? <path d="M18 6L6 18M6 6l12 12"/> : <path d="M3 12h18M3 6h18M3 18h18"/>}
          </svg>
        </button>
      </div>

      {open && (
        <div className="landing-mobile-menu md:hidden border-t border-[#e2e8f0] landing-container-wide py-4 flex flex-col gap-2 max-h-[calc(100dvh-3.5rem)] overflow-y-auto overscroll-contain safe-bottom bg-[#f8fafc]">
          {TOP_NAV.map((item) => (
            <a
              key={item.id}
              href={item.href}
              onClick={close}
              aria-current={activeGroup === item.id ? "true" : undefined}
              className={`text-sm font-medium transition-colors ${
                activeGroup === item.id ? "text-[#ea580c]" : "text-[#64748b] hover:text-[#0f172a]"
              }`}
            >
              {isES ? item.es : item.en}
            </a>
          ))}
          <a href={CTA.forRetailers.href} onClick={close}
             className="text-sm font-medium text-[#ea580c] hover:text-[#f97316] transition-colors">
            {isES ? CTA.forRetailers.es : CTA.forRetailers.en}
          </a>
          <a href={CTA.contact.href} onClick={close}
             className="text-sm font-medium text-[#64748b] hover:text-[#0f172a] transition-colors">
            {isES ? CTA.contact.es : CTA.contact.en}
          </a>
          <a href={CTA.signIn.href} onClick={close}
             className="text-sm font-medium text-[#64748b] hover:text-[#0f172a] transition-colors">
            {signInCta}
          </a>
          <a href={CTA.signUp.href} onClick={close}
             className="inline-flex items-center justify-center rounded-[10px] bg-[#ea580c] text-[#f8fafc] text-sm font-semibold px-6 py-3 mt-1 hover:bg-[#f97316] transition-colors">
            {signUpCta}
          </a>
          <button type="button" onClick={() => setLang(isES ? "en" : "es")}
            aria-label={isES ? "Switch to English" : "Cambiar a Español"}
            className="text-xs font-medium text-[#64748b] cursor-pointer text-left hover:text-[#0f172a] transition-colors">
            {isES ? "EN" : "ES"}
          </button>
        </div>
      )}
    </nav>
  );
}
