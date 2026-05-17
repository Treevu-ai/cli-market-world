const lines = [
  { emoji: "🛒", name: "Supermercados", count: 22, color: "#00FF88" },
  { emoji: "💊", name: "Farmacias", count: 5, color: "#FF6B35" },
  { emoji: "📱", name: "Electro", count: 12, color: "#A78BFA" },
  { emoji: "👕", name: "Moda", count: 8, color: "#FFD600" },
  { emoji: "⚽", name: "Deportes", count: 12, color: "#4ADE80" },
  { emoji: "🏠", name: "Hogar", count: 7, color: "#F5F5F0" },
  { emoji: "💄", name: "Belleza", count: 6, color: "#F472B6" },
  { emoji: "🐾", name: "Mascotas", count: 3, color: "#FB923C" },
  { emoji: "📚", name: "Librería", count: 3, color: "#60A5FA" },
  { emoji: "🏬", name: "Departamentales", count: 8, color: "#C084FC" },
  { emoji: "🍔", name: "Alimentos", count: 3, color: "#F87171" },
  { emoji: "🔧", name: "Autopartes", count: 1, color: "#94A3B8" },
];

const countries = [
  { code: "BR", name: "Brasil", stores: 35, color: "#4ADE80" },
  { code: "MX", name: "México", stores: 18, color: "#FF6B35" },
  { code: "CO", name: "Colombia", stores: 13, color: "#FFD600" },
  { code: "AR", name: "Argentina", stores: 12, color: "#60A5FA" },
  { code: "PE", name: "Perú", stores: 10, color: "#00FF88" },
  { code: "CL", name: "Chile", stores: 8, color: "#F87171" },
  { code: "ES", name: "España", stores: 3, color: "#F472B6" },
  { code: "FR", name: "Francia", stores: 3, color: "#A78BFA" },
  { code: "IT", name: "Italia", stores: 2, color: "#FB923C" },
  { code: "GB", name: "Reino Unido", stores: 1, color: "#C084FC" },
];

export default function CoverageDashboard() {
  return (
    <section id="coverage" className="flex flex-col w-full bg-[#060606] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] gap-8 sm:gap-10 md:gap-[48px]">
      <div className="flex flex-col gap-[16px] w-full">
        <span className="font-ibm-mono text-[9px] sm:text-[10px] md:text-[12px] font-bold text-[#FFD600] tracking-[1.5px] md:tracking-[3px]">
          [SYS] // COBERTURA GLOBAL VTEX
        </span>
        <h2 className="font-grotesk text-[28px] sm:text-[36px] md:text-[56px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.05] whitespace-pre-line w-full max-w-[700px]">
          {"100 COMERCIOS.\nUN SOLO CONECTOR."}
        </h2>
        <p className="font-ibm-mono text-[9px] sm:text-[11px] md:text-[13px] text-[#666666] tracking-[0.5px] md:tracking-[1px] leading-[1.6] text-pretty w-full max-w-[600px]">
          TODOS LOS RETAILeRS COMPARTEN LA MISMA API VTEX. EL CONECTOR ES GENÉRICO. AGREGAR UN COMERCIO NUEVO ES UNA LÍNEA DE CONFIGURACIÓN.
        </p>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-[2px] w-full">
        {[
          { value: "100", label: "COMERCIOS", color: "#00FF88" },
          { value: "12", label: "LÍNEAS", color: "#FFD600" },
          { value: "10", label: "PAÍSES", color: "#60A5FA" },
          { value: "12", label: "MCP TOOLS", color: "#FF6B35" },
        ].map((stat) => (
          <div key={stat.label} className="flex flex-col items-center justify-center gap-2 p-6 sm:p-8 bg-[#0D0D0D] border border-[#1A1A1A]">
            <span className="font-grotesk text-[36px] sm:text-[48px] md:text-[64px] font-bold tracking-[-2px] leading-none" style={{ color: stat.color }}>
              {stat.value}
            </span>
            <span className="font-ibm-mono text-[9px] sm:text-[10px] text-[#555] tracking-[2px]">{stat.label}</span>
          </div>
        ))}
      </div>
      <div className="flex flex-col w-full gap-[2px]">
        <span className="font-ibm-mono text-[8px] sm:text-[9px] text-[#444] tracking-[2px] mb-1">DISTRIBUCIÓN POR LÍNEA</span>
        {lines.map((line) => (
          <div key={line.name} className="flex items-center gap-3 h-[22px] sm:h-[24px]">
            <span className="text-[12px] sm:text-[14px] w-[24px] text-center shrink-0">{line.emoji}</span>
            <span className="font-ibm-mono text-[7px] sm:text-[8px] text-[#666] tracking-[1px] w-[60px] sm:w-[80px] shrink-0">{line.name}</span>
            <div className="flex-1 h-[8px] bg-[#0F0F0F] overflow-hidden">
              <div className="h-full" style={{ width: `${(line.count / 35) * 100}%`, backgroundColor: line.color, opacity: 0.5 }} />
            </div>
            <span className="font-ibm-mono text-[8px] sm:text-[9px] font-bold shrink-0 w-[20px] text-right" style={{ color: line.color }}>{line.count}</span>
          </div>
        ))}
      </div>
      <div className="flex flex-col w-full gap-[2px]">
        <span className="font-ibm-mono text-[8px] sm:text-[9px] text-[#444] tracking-[2px] mb-1">DISTRIBUCIÓN POR PAÍS</span>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-[2px]">
          {countries.map((c) => (
            <div key={c.code} className="flex items-center gap-2 p-2 sm:p-3 bg-[#0D0D0D] border border-[#1A1A1A]">
              <div className="w-[4px] h-[4px] rounded-full shrink-0" style={{ backgroundColor: c.color }} />
              <span className="font-grotesk text-[9px] sm:text-[10px] font-bold text-[#AAA] tracking-[0.5px]">{c.name}</span>
              <span className="font-ibm-mono text-[8px] sm:text-[9px] ml-auto" style={{ color: c.color }}>{c.stores}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
