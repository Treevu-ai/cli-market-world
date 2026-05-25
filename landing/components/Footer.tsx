"use client";
import { useLang } from "@/lib/LanguageContext";

const productosES = ["Market Search", "Market Compare", "Market Checkout", "Market Ask", "Dashboard"];
const productosEN = ["Market Search", "Market Compare", "Market Checkout", "Market Ask", "Dashboard"];
const coberturaES = ["38 retailers", "9 países", "6 líneas", "36 MCP tools", "API keys + scopes"];
const coberturaEN = ["38 retailers", "9 countries", "6 lines", "36 MCP tools", "API keys + scopes"];
const recursos = [
  { label: "GitHub", href: "https://github.com/Treevu-ai/cli-market-world" },
  { label: "Docs", href: "https://cli-market-api.onrender.com/docs" },
  { label: "API", href: "https://cli-market-api.onrender.com" },
  { label: "Dashboard", href: "https://cli-market-api.onrender.com/dashboard" },
  { label: "MCP Registry", href: "https://registry.modelcontextprotocol.io" },
];

export default function Footer() {
  const { lang } = useLang();
  const productos = lang === "es" ? productosES : productosEN;
  const cobertura = lang === "es" ? coberturaES : coberturaEN;

  return (
    <footer className="flex flex-col w-full bg-[#0c0c0c] safe-bottom">
      <div className="flex flex-col md:flex-row gap-8 sm:gap-10 md:gap-[80px] px-4 sm:px-6 md:px-[120px] py-8 sm:py-10 md:py-[64px]">
        <div className="flex flex-col gap-4 md:w-[260px] md:shrink-0">
          <span className="font-grotesk text-[16px] font-bold text-white tracking-tight">CLI Market</span>
          <p className="font-mono text-[10px] text-[#666] leading-[1.6] max-w-[240px]">
            {lang === "es"
              ? "Infraestructura de comercio para agentes de IA. 38 retailers VTEX en 9 países. Una sola API."
              : "Commerce infrastructure for AI agents. 30 VTEX retailers in 9 countries. One API."}
          </p>
          <div className="flex gap-2">
            {[
              { label: "GH", href: "https://github.com/Treevu-ai/cli-market-world" },
              { label: "PH", href: "https://www.producthunt.com/products/cli-market" },
              { label: "PY", href: "https://pypi.org/project/cli-market/" },
            ].map((s) => (
              <a key={s.label} href={s.href} target="_blank" rel="noopener"
                className="flex items-center justify-center w-[36px] h-[36px] bg-[#111] border border-[#2d2d2d] hover:border-[#888] transition-colors">
                <span className="font-mono text-[10px] font-bold text-[#aaa]">{s.label}</span>
              </a>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-3 md:flex md:flex-1 gap-6 sm:gap-8 md:gap-[80px]">
          <div className="flex flex-col gap-3">
            <span className="font-mono text-[10px] font-bold text-white/50 tracking-[2px] uppercase">
              {lang === "es" ? "Producto" : "Product"}
            </span>
            {productos.map((p) => (
              <span key={p} className="font-mono text-[11px] text-[#888] py-0.5">{p}</span>
            ))}
          </div>
          <div className="flex flex-col gap-3">
            <span className="font-mono text-[10px] font-bold text-white/50 tracking-[2px] uppercase">
              {lang === "es" ? "Cobertura" : "Coverage"}
            </span>
            {cobertura.map((c) => (
              <span key={c} className="font-mono text-[11px] text-[#888] py-0.5">{c}</span>
            ))}
          </div>
          <div className="flex flex-col gap-3">
            <span className="font-mono text-[10px] font-bold text-white/50 tracking-[2px] uppercase">
              {lang === "es" ? "Recursos" : "Resources"}
            </span>
            {recursos.map((r) => (
              <a key={r.label} href={r.href} target="_blank" rel="noopener"
                className="font-mono text-[11px] text-[#888] hover:text-white transition-colors py-0.5">
                {r.label}
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between w-full px-4 sm:px-6 md:px-[120px] py-4 border-t border-[#1d1d1d] gap-3 sm:gap-0">
        <span className="font-mono text-[10px] text-[#555] tracking-[0.5px]">
          © 2026 CLI Market · MIT License
        </span>
        <div className="flex items-center gap-4 sm:gap-6">
          <a href="https://github.com/Treevu-ai/cli-market-world/blob/main/legal/Privacy.md" target="_blank" rel="noopener"
            className="font-mono text-[10px] text-[#555] hover:text-[#aaa] transition-colors">Privacy</a>
          <a href="https://github.com/Treevu-ai/cli-market-world/blob/main/legal/ToS.md" target="_blank" rel="noopener"
            className="font-mono text-[10px] text-[#555] hover:text-[#aaa] transition-colors">Terms</a>
          <a href="https://github.com/Treevu-ai/cli-market-world/blob/main/legal/Data_License_Agreement.md" target="_blank" rel="noopener"
            className="font-mono text-[10px] text-[#555] hover:text-[#aaa] transition-colors">Data</a>
          <span className="font-mono text-[10px] font-bold text-[#3cffd0]">v1.2.0</span>
        </div>
      </div>
    </footer>
  );
}
