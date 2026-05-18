import { useLang } from "@/lib/LanguageContext";
"use client";

export default function Pricing() {
  const { t: _t } = useLang();
  return (
    <section id="pricing" className="flex flex-col w-full bg-[#060606] py-12 px-4 sm:py-16 sm:px-6 md:py-[80px] md:px-[120px] gap-8 sm:gap-10 md:gap-[48px]">
      <div className="flex flex-col gap-[12px] w-full">
        <span className="font-mono text-[9px] sm:text-[10px] md:text-[11px] font-bold text-[#FFD600] tracking-[2px] md:tracking-[3px] uppercase">Acceso</span>
        <h2 className="font-grotesk text-[26px] sm:text-[32px] md:text-[48px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.05]">
          Free tier disponible.
        </h2>
        <p className="font-mono text-[12px] sm:text-[13px] md:text-[15px] text-[#666] tracking-[0.5px] leading-[1.6] max-w-[500px]">
          La API está viva. El CLI es open source. Si estás construyendo agentes de IA, empieza hoy. Planes pagos para escala enterprise disponibles pronto.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
        <a href="https://github.com/Treevu-ai/cli-market-latam"
          className="group inline-flex items-center gap-3 border border-[#333] px-6 py-3 font-mono text-[11px] uppercase tracking-widest text-[#AAA] hover:border-[#00FF88] hover:text-[#00FF88] transition-all duration-200 w-fit"
        >
          Instalar CLI
          <span className="transition-transform duration-300 group-hover:translate-x-1">→</span>
        </a>
        <a href="https://t.me/climarketbot"
          className="group inline-flex items-center gap-3 border border-[#333] px-6 py-3 font-mono text-[11px] uppercase tracking-widest text-[#666] hover:border-[#888] hover:text-[#888] transition-all duration-200 w-fit"
        >
          Contactar
        </a>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-[2px] w-full mt-4">
        {[
          { label: "Developers", sub: "CLI · REST API · JSON · CSV · MCP Tools. Open source. Gratis para empezar.", color: "#00FF88" },
          { label: "Business", sub: "Data Feed · Competitive Intelligence · Cross-Border Analytics. Planes pagos.", color: "#FFD600" },
          { label: "AI Agents", sub: "12 MCP Tools · Autonomous Checkout · Natural Language. La capa que los agentes necesitan.", color: "#FF6B35" },
        ].map((item) => (
          <div key={item.label} className="flex flex-col gap-3 p-5 sm:p-6 bg-[#0F0F0F] border border-[#1D1D1D]">
            <div className="flex items-center gap-2">
              <div className="w-[5px] h-[5px] rounded-full shrink-0" style={{ backgroundColor: item.color }} />
              <span className="font-mono text-[11px] font-bold tracking-[1px]" style={{ color: item.color }}>{item.label}</span>
            </div>
            <p className="font-mono text-[11px] text-[#666] leading-[1.5]">{item.sub}</p>
          </div>
        ))}
      </div>

      <p className="font-mono text-[10px] text-[#444] tracking-[2px] text-center mt-6">
        OPEN SOURCE · MIT LICENSE · CLI GRATIS · API FREE TIER · PLANES PAGOS PRONTO
      </p>
    </section>
  );
}
