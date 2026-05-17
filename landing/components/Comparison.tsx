import SectionHeader from "./SectionHeader";

const rows = [
  { feature: "BÚSQUEDA MULTITIENDA",       market: "[✓]", humano: "[✗]", app: "[✗]", api: "[—]" },
  { feature: "COMPARACIÓN DE PRECIOS",      market: "[✓]", humano: "[—]", app: "[✓]", api: "[✗]" },
  { feature: "CHECKOUT UNIFICADO",          market: "[✓]", humano: "[✗]", app: "[✗]", api: "[✗]" },
  { feature: "COMPATIBLE CON MCP",          market: "[✓]", humano: "[✗]", app: "[✗]", api: "[—]" },
  { feature: "LENGUAJE NATURAL (ASK)",      market: "[✓]", humano: "[✗]", app: "[✗]", api: "[✗]" },
  { feature: "ESCALA A 8 TIENDAS",          market: "[✓]", humano: "[✗]", app: "[—]", api: "[✓]" },
];

function cellStyle(val: string) {
  if (val === "[✓]") return "font-bold text-[14px]";
  if (val === "[✗]") return "text-[#3D3D3D] text-[13px]";
  if (val === "[—]") return "text-[#444444] text-[13px]";
  return "text-[#444444] text-[10px]";
}

export default function Comparison() {
  return (
    <section id="comparison" className="flex flex-col w-full bg-[#050505] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] gap-10 sm:gap-12 md:gap-[64px]">
      <SectionHeader
        label="[05] // CLI MARKET VS. ALTERNATIVAS"
        title={"POR QUÉ CLI MARKET\nES DIFERENTE."}
        subtitle="COMPARA EL IMPACTO REAL. SIN RODEOS. SIN LETRA PEQUEÑA."
      />

      {/* Desktop table */}
      <div className="hidden md:flex flex-col w-full border border-[#2D2D2D]">
        <div className="flex w-full h-[56px] bg-[#111111] border-b-2 border-b-[#00FF88]">
          <div className="flex items-center w-[320px] shrink-0 px-[32px] border-r border-r-[#2D2D2D]">
            <span className="font-grotesk text-[11px] font-bold text-[#888888] tracking-[2px]">CAPACIDAD</span>
          </div>
          <div className="flex items-center flex-1 px-[32px] bg-[#1A1A1A] border-r border-r-[#2D2D2D]">
            <span className="font-grotesk text-[11px] font-bold text-[#00FF88] tracking-[2px]">CLI MARKET</span>
          </div>
          {["COMPRA MANUAL", "APP DEL SUPER", "API VTEX DIRECTA"].map((tool, i) => (
            <div key={tool} className={`flex items-center flex-1 px-[24px] ${i < 2 ? "border-r border-r-[#2D2D2D]" : ""}`}>
              <span className="font-grotesk text-[11px] font-bold text-[#555555] tracking-[2px]">{tool}</span>
            </div>
          ))}
        </div>

        {rows.map((row, i) => (
          <div key={row.feature} className={`flex w-full h-[56px] ${i < rows.length - 1 ? "border-b border-b-[#1D1D1D]" : ""}`}>
            <div className="flex items-center w-[320px] shrink-0 px-[32px] border-r border-r-[#2D2D2D]">
              <span className="font-ibm-mono text-[12px] text-[#CCCCCC] tracking-[1px]">{row.feature}</span>
            </div>
            <div className="flex items-center flex-1 px-[32px] bg-[#0D0D0D] border-r border-r-[#2D2D2D]">
              <span className="font-ibm-mono tracking-[1px] text-[#00FF88] font-bold text-[14px]">{row.market}</span>
            </div>
            {[row.humano, row.app, row.api].map((val, j) => (
              <div key={j} className={`flex items-center flex-1 px-[24px] ${j < 2 ? "border-r border-r-[#2D2D2D]" : ""}`}>
                <span className={`font-ibm-mono tracking-[1px] ${cellStyle(val)}`}>{val}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Mobile — card layout */}
      <div className="flex flex-col md:hidden w-full gap-2">
        <div className="flex items-center gap-2 bg-[#111111] border-b-2 border-b-[#00FF88] px-3 py-3 rounded-t-sm">
          <span className="font-grotesk text-[11px] font-bold text-[#00FF88] tracking-[1.5px]">CLI MARKET</span>
          <span className="font-ibm-mono text-[9px] text-[#555555] tracking-[1px]">vs Manual · App · API VTEX</span>
        </div>
        {rows.map((row, i) => (
          <div key={row.feature} className={`flex items-center justify-between px-4 py-3 border border-[#1D1D1D] bg-[#0D0D0D] gap-2 ${i === rows.length - 1 ? "rounded-b-sm" : ""}`}>
            <span className="font-grotesk text-[11px] font-bold text-[#CCCCCC] tracking-[0.5px] shrink-0">{row.feature}</span>
            <div className="flex items-center gap-3 shrink-0">
              <span className="font-ibm-mono text-[11px] text-[#555555] tracking-[1px]">Otr: <span className={row.humano === "[✓]" ? "text-[#00FF88] font-bold" : "text-[#3D3D3D]"}>{row.humano}</span></span>
              <span className="font-ibm-mono text-[14px] font-bold text-[#00FF88] tracking-[1px]">{row.market}</span>
            </div>
          </div>
        ))}
        <div className="flex items-center justify-center gap-3 py-2">
          <span className="font-ibm-mono text-[9px] text-[#333333] tracking-[1px]">
            <span className="text-[#00FF88]">[✓]</span> Soportado · <span className="text-[#3D3D3D]">[✗]</span> No · <span className="text-[#444444]">[—]</span> Parcial
          </span>
        </div>
      </div>
    </section>
  );
}
