"use client";

const lines = [
  { emoji: "🛒", name: "SUPERMERCADOS", count: 11, stores: "Wong · Metro · Plaza Vea · Carrefour · Jumbo · Chedraui · HEB · Olímpica · Éxito · Carrefour ES", color: "#00FF88" },
  { emoji: "💊", name: "FARMACIAS", count: 2, stores: "Droga Raia · Drogasil", color: "#FF6B35" },
  { emoji: "📱", name: "ELECTRO", count: 2, stores: "Magazine Luiza · Motorola", color: "#A78BFA" },
  { emoji: "👕", name: "MODA", count: 1, stores: "Lojas Renner", color: "#FFD600" },
  { emoji: "⚽", name: "DEPORTES", count: 2, stores: "Centauro · Decathlon FR", color: "#4ADE80" },
  { emoji: "🏠", name: "HOGAR", count: 1, stores: "Homecenter", color: "#F5F5F0" },
];

const countries = [
  { code: "PE", name: "Perú", stores: 3 },
  { code: "AR", name: "Argentina", stores: 2 },
  { code: "BR", name: "Brasil", stores: 7 },
  { code: "MX", name: "México", stores: 2 },
  { code: "CO", name: "Colombia", stores: 2 },
  { code: "ES", name: "España", stores: 1 },
  { code: "FR", name: "Francia", stores: 1 },
];

export default function Ribbon() {
  return (
    <section className="flex flex-col w-full bg-[#0A0A0A] py-8 px-0 sm:py-10 md:py-[56px] overflow-hidden">
      <div className="flex items-center gap-2 px-4 sm:px-6 md:px-[120px] mb-4 sm:mb-5">
        <span className="w-[6px] h-[6px] bg-[#00FF88] rounded-full animate-pulse shrink-0" />
        <span className="font-ibm-mono text-[9px] sm:text-[10px] md:text-[11px] text-[#00FF88] tracking-[2px] md:tracking-[3px]">
          COBERTURA · 19 COMERCIOS · 6 LÍNEAS · 7 PAÍSES
        </span>
      </div>
      <div className="relative w-full overflow-hidden py-2 border-y border-[#1A1A1A]" style={{ height: "48px" }}>
        <style>{`
          @keyframes ribbon-scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
          .ribbon-track { display: flex; width: max-content; animation: ribbon-scroll 30s linear infinite; }
          .ribbon-track:hover { animation-play-state: paused; }
        `}</style>
        <div className="ribbon-track">
          {[...lines, ...lines].map((line, i) => (
            <div key={`${line.name}-${i}`} className="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 md:px-[24px] shrink-0 h-[44px]">
              <span className="text-[16px] sm:text-[18px]">{line.emoji}</span>
              <span className="font-grotesk text-[9px] sm:text-[10px] md:text-[11px] font-bold tracking-[1.5px]" style={{ color: line.color }}>{line.name}</span>
              <span className="font-ibm-mono text-[8px] sm:text-[9px] text-[#444444] tracking-[1px]">{line.count}</span>
              <span className="font-ibm-mono text-[7px] sm:text-[8px] text-[#333] tracking-[0.5px] hidden sm:inline max-w-[320px] truncate">{line.stores}</span>
              <span className="w-[3px] h-[3px] rounded-full mx-1" style={{ backgroundColor: line.color, opacity: 0.4 }} />
            </div>
          ))}
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3 px-4 sm:px-6 pt-4 sm:pt-5">
        {countries.map((c) => (
          <div key={c.code} className="flex items-center gap-[5px] h-[24px] sm:h-[26px] px-[8px] sm:px-[10px] bg-[#0F0F0F] border border-[#1D1D1D]">
            <span className="font-ibm-mono text-[8px] sm:text-[9px] text-[#666] tracking-[1px]">{c.code}</span>
            <span className="font-grotesk text-[9px] sm:text-[10px] font-bold text-[#888] tracking-[0.5px]">{c.name}</span>
            <span className="font-ibm-mono text-[7px] sm:text-[8px] text-[#3D3D3D]">{c.stores}</span>
          </div>
        ))}
        <div className="flex items-center gap-[5px] h-[24px] sm:h-[26px] px-[8px] sm:px-[10px] bg-[#00FF88]/5 border border-[#00FF88]/20">
          <span className="w-[5px] h-[5px] bg-[#00FF88] rounded-full animate-pulse" />
          <span className="font-ibm-mono text-[8px] sm:text-[9px] text-[#00FF88] tracking-[1px]">ONLINE</span>
        </div>
      </div>
    </section>
  );
}
