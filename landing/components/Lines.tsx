const lines = [
  {
    emoji: "🛒",
    name: "Supermercados",
    count: 9,
    stores: "Wong · Metro · Plaza Vea · Carrefour · Jumbo · Chedraui · HEB · Olímpica",
    color: "#00FF88",
  },
  {
    emoji: "💊",
    name: "Farmacias y Salud",
    count: 2,
    stores: "Droga Raia · Drogasil",
    color: "#60A5FA",
  },
  {
    emoji: "📱",
    name: "Electro y Tecnología",
    count: 2,
    stores: "Magazine Luiza · Motorola",
    color: "#FF6B35",
  },
  {
    emoji: "👕",
    name: "Moda y Calzado",
    count: 1,
    stores: "Lojas Renner",
    color: "#FFD600",
  },
  {
    emoji: "⚽",
    name: "Deportes y Fitness",
    count: 1,
    stores: "Centauro",
    color: "#4ADE80",
  },
  {
    emoji: "🏠",
    name: "Hogar y Construcción",
    count: 1,
    stores: "Homecenter",
    color: "#A78BFA",
  },
];

export default function Lines() {
  return (
    <section className="flex flex-col w-full bg-[#080808] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] gap-8 sm:gap-10 md:gap-[48px]">
      <div className="flex flex-col gap-[16px] w-full">
        <span className="font-ibm-mono text-[9px] sm:text-[10px] md:text-[12px] font-bold text-[#FFD600] tracking-[1.5px] md:tracking-[3px]">
          [LÍNEAS] // 6 VERTICALES DE NEGOCIO
        </span>
        <h2 className="font-grotesk text-[28px] sm:text-[36px] md:text-[56px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.05] whitespace-pre-line w-full max-w-[700px]">
          {"UN CONECTOR.\nMÚLTIPLES INDUSTRIAS."}
        </h2>
        <p className="font-ibm-mono text-[9px] sm:text-[11px] md:text-[13px] text-[#666666] tracking-[0.5px] md:tracking-[1px] leading-[1.6] text-pretty w-full max-w-[600px]">
          EL CONECTOR VTEX FUNCIONA IGUAL PARA CUALQUIER RETAILER. AGREGAR UNA LÍNEA NUEVA ES AGREGAR UN NUEVO TENANT VTEX AL REGISTRO.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-[2px] w-full">
        {lines.map((line) => (
          <div
            key={line.name}
            className="flex flex-col gap-3 sm:gap-4 p-4 sm:p-5 md:p-[32px] bg-[#0F0F0F] border border-[#1D1D1D]"
          >
            <div className="flex items-center gap-3">
              <span className="text-[24px] sm:text-[28px] leading-none">{line.emoji}</span>
              <div className="flex flex-col gap-[2px]">
                <span
                  className="font-grotesk text-[14px] sm:text-[16px] font-bold tracking-[1px]"
                  style={{ color: line.color }}
                >
                  {line.name}
                </span>
                <span className="font-ibm-mono text-[9px] sm:text-[10px] text-[#444444] tracking-[1px]">
                  {line.count} retailer{line.count > 1 ? "s" : ""}
                </span>
              </div>
            </div>
            <p className="font-ibm-mono text-[9px] sm:text-[10px] text-[#666666] tracking-[0.5px] leading-[1.5]">
              {line.stores}
            </p>
            <div
              className="h-[2px] w-full mt-auto"
              style={{ backgroundColor: line.color, opacity: 0.3 }}
            />
          </div>
        ))}
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-[24px] pt-4">
        <div className="flex items-center gap-[6px]">
          <span className="font-grotesk text-[20px] sm:text-[24px] font-bold text-[#00FF88]">16</span>
          <span className="font-ibm-mono text-[9px] sm:text-[10px] text-[#888888] tracking-[1px]">COMERCIOS VTEX</span>
        </div>
        <div className="flex items-center gap-[6px]">
          <span className="font-grotesk text-[20px] sm:text-[24px] font-bold text-[#FFD600]">6</span>
          <span className="font-ibm-mono text-[9px] sm:text-[10px] text-[#888888] tracking-[1px]">LÍNEAS DE NEGOCIO</span>
        </div>
        <div className="flex items-center gap-[6px]">
          <span className="font-grotesk text-[20px] sm:text-[24px] font-bold text-[#60A5FA]">5</span>
          <span className="font-ibm-mono text-[9px] sm:text-[10px] text-[#888888] tracking-[1px]">PAÍSES</span>
        </div>
      </div>
    </section>
  );
}
