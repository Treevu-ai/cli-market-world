"use client";
import { createContext, useContext, useState, useCallback } from "react";

export type Lang = "es" | "en";
type Dict = Record<string, string>;

const es: Dict = {
  nav_comandos: "COMANDOS", nav_arquitectura: "ARQUITECTURA", nav_casos: "COBERTURA", nav_faq: "FAQ", nav_precios: "PRECIOS", nav_instalar: "INSTALAR CLI",
  hero_badge: "[CLI] // INFRAESTRUCTURA PARA AGENTES IA", hero_early: "EARLY ADOPTER — LANZAMIENTO MAYO 2026",
  hero_headline1: "SUPERMERCADOS", hero_headline2: "COMO APIs.", hero_headline3: "PARA AGENTES IA.",
  hero_stats: "100 COMERCIOS · 12 LÍNEAS · 12 PAÍSES · 1 API UNIFICADA.",
  hero_sub: "UN PRODUCTO PENSADO PARA HUMANOS. DISEÑADO PARA AGENTES.",
  hero_for_devs: "FOR DEVELOPERS", hero_for_biz: "FOR BUSINESS", hero_for_agents: "FOR AI AGENTS",
  hero_cta: "INSTALAR AHORA", hero_cta2: "VER COMANDOS →",
  ribbon_header: "COBERTURA · 100 COMERCIOS · 12 LÍNEAS · 12 PAÍSES", ribbon_online: "ONLINE",
  coverage_label: "[SYS] // COBERTURA GLOBAL VTEX", coverage_title: "100 COMERCIOS.\nUN SOLO CONECTOR.",
  coverage_sub: "TODOS LOS RETAILERS COMPARTEN LA MISMA API VTEX. EL CONECTOR ES GENÉRICO. AGREGAR UN COMERCIO NUEVO ES UNA LÍNEA DE CONFIGURACIÓN.",
  final_badge: "[¿LISTO PARA CONECTAR TUS AGENTES?]", final_title: "SUPERMERCADOS\nCOMO APIs.",
  final_sub: "ÚNETE A LAS EMPRESAS QUE YA ESTÁN CONECTANDO AGENTES DE IA CON EL COMERCIO DE LATAM. PRECIO DE LANZAMIENTO DISPONIBLE POR TIEMPO LIMITADO.",
  final_cta: "INSTALAR AHORA", final_cta2: "VER PLANES",
  footer_copy: "© 2026 CLI MARKET · SINAPSIS INNOVADORA. TODOS LOS DERECHOS RESERVADOS.",
};

const en: Dict = {
  nav_comandos: "COMMANDS", nav_arquitectura: "ARCHITECTURE", nav_casos: "COVERAGE", nav_faq: "FAQ", nav_precios: "PRICING", nav_instalar: "INSTALL CLI",
  hero_badge: "[CLI] // INFRASTRUCTURE FOR AI AGENTS", hero_early: "EARLY ADOPTER — LAUNCH MAY 2026",
  hero_headline1: "SUPERMARKETS", hero_headline2: "AS APIs.", hero_headline3: "FOR AI AGENTS.",
  hero_stats: "100 RETAILERS · 12 LINES · 12 COUNTRIES · 1 UNIFIED API.",
  hero_sub: "A PRODUCT BUILT FOR HUMANS. DESIGNED FOR AGENTS.",
  hero_for_devs: "FOR DEVELOPERS", hero_for_biz: "FOR BUSINESS", hero_for_agents: "FOR AI AGENTS",
  hero_cta: "INSTALL NOW", hero_cta2: "SEE COMMANDS →",
  ribbon_header: "COVERAGE · 100 RETAILERS · 12 LINES · 12 COUNTRIES", ribbon_online: "ONLINE",
  coverage_label: "[SYS] // GLOBAL VTEX COVERAGE", coverage_title: "100 RETAILERS.\nONE CONNECTOR.",
  coverage_sub: "ALL RETAILERS SHARE THE SAME VTEX API. THE CONNECTOR IS GENERIC. ADDING A NEW RETAILER IS ONE LINE OF CONFIG.",
  final_badge: "[READY TO CONNECT YOUR AGENTS?]", final_title: "SUPERMARKETS\nAS APIs.",
  final_sub: "JOIN THE COMPANIES ALREADY CONNECTING AI AGENTS WITH LATAM COMMERCE. LAUNCH PRICING AVAILABLE FOR A LIMITED TIME.",
  final_cta: "INSTALL NOW", final_cta2: "SEE PLANS",
  footer_copy: "© 2026 CLI MARKET · SINAPSIS INNOVADORA. ALL RIGHTS RESERVED.",
};

const dicts: Record<Lang, Dict> = { es, en };

const LangContext = createContext<{ lang: Lang; t: (k: string) => string; toggleLang: () => void }>({ lang: "es", t: (k) => k, toggleLang: () => {} });

export function LangProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>("es");
  const toggleLang = useCallback(() => setLang((l) => (l === "es" ? "en" : "es")), []);
  const t = useCallback((key: string) => dicts[lang][key] ?? key, [lang]);
  return <LangContext.Provider value={{ lang, t, toggleLang }}>{children}</LangContext.Provider>;
}

export function useLang() { return useContext(LangContext); }

export function LangToggle() {
  const { lang, toggleLang } = useLang();
  return (
    <button onClick={toggleLang} className="font-ibm-mono text-[10px] tracking-[1.5px] text-[#555] hover:text-[#00FF88] transition-colors bg-transparent border border-[#2D2D2D] px-[8px] py-[3px] cursor-pointer" aria-label="Toggle language">
      {lang === "es" ? "EN" : "ES"}
    </button>
  );
}
