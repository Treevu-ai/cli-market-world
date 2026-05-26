"use client";
import { useLang } from "@/lib/LanguageContext";

export default function Footer() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <footer className="bg-white border-t border-[#e5e5e5] py-12">
      <div className="max-w-[720px] mx-auto px-6 flex flex-col items-center gap-6 text-center">

        {/* Logo */}
        <div className="flex items-center gap-2 text-black">
          <svg width="20" height="20" viewBox="0 0 32 32" fill="none" className="text-black">
            <path d="M3 6l2 2 3 12h12l4-8H11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <circle cx="11" cy="24" r="2" stroke="currentColor" strokeWidth="1.5"/>
            <circle cx="20" cy="24" r="2" stroke="currentColor" strokeWidth="1.5"/>
            <rect x="11" y="10" width="7" height="1.5" rx="0.5" fill="currentColor"/>
            <rect x="12" y="13" width="5" height="1.5" rx="0.5" fill="currentColor"/>
          </svg>
          <span className="font-medium text-xs tracking-tight">CLI Market</span>
        </div>

        {/* Links */}
        <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-xs text-[#a3a3a3]">
          <a href="https://github.com/Treevu-ai/cli-market-world" className="hover:text-black transition-colors">GitHub</a>
          <a href="https://pypi.org/project/cli-market/" className="hover:text-black transition-colors">PyPI</a>
          <a href="mailto:hello@cli-market.dev" className="hover:text-black transition-colors">{isES ? "Contacto" : "Contact"}</a>
        </div>

        <p className="text-[10px] text-[#a3a3a3] font-mono">
          {isES ? "60 comercios · 11 países · 3 plataformas · 36 herramientas MCP · MIT License" : "60 retailers · 11 countries · 3 platforms · 36 MCP tools · MIT License"}
        </p>
      </div>
    </footer>
  );
}
