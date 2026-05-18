const lines = [
  { emoji: "🛒", name: "Supermercados", count: 27, stores: "Wong · Metro · Plaza Vea · Carrefour · Jumbo · Coto · Dia · Pao de Acucar · Chedraui · HEB · Olimpica · Exito · Lider · Soriana · Carulla", color: "#00FF88" },
  { emoji: "💊", name: "Farmacias", count: 6, stores: "Droga Raia · Drogasil · Pacheco · Farmatodo · Inkafarma · Boticas y Salud", color: "#FF6B35" },
  { emoji: "📱", name: "Electro y Tecnología", count: 14, stores: "Magazine Luiza · Samsung · Motorola · LG · Electrolux · Whirlpool · Alkosto · Fravega · Musimundo · Casas Bahia · Ponto Frio", color: "#A78BFA" },
  { emoji: "👕", name: "Moda y Calzado", count: 8, stores: "Renner · C&A · Marisa · Riachuelo · Arturo Calle · Leonisa · Totto", color: "#FFD600" },
  { emoji: "⚽", name: "Deportes y Fitness", count: 15, stores: "Centauro · Nike · Adidas · Decathlon (10 paises) · Marti", color: "#4ADE80" },
  { emoji: "🏠", name: "Hogar y Construcción", count: 7, stores: "Homecenter · Sodimac · Easy · Promart · Leroy Merlin · Rosen", color: "#F5F5F0" },
  { emoji: "💄", name: "Belleza y Cosmética", count: 6, stores: "O Boticario · Natura (4 paises) · Avon", color: "#F472B6" },
  { emoji: "🐾", name: "Mascotas", count: 3, stores: "Petlove · Petz · Cobasi", color: "#FB923C" },
  { emoji: "📚", name: "Librería y Oficina", count: 3, stores: "Saraiva · Office Depot · Tai Loy", color: "#60A5FA" },
  { emoji: "🏬", name: "Tiendas Departamentales", count: 8, stores: "Liverpool · Palacio · Sears · Sanborns · Oechsle · Paris · La Polar", color: "#C084FC" },
  { emoji: "🍔", name: "Alimentos y Bebidas", count: 3, stores: "Nestle · Unilever · Swift", color: "#F87171" },
  { emoji: "🔧", name: "Autopartes", count: 1, stores: "AutoZone", color: "#94A3B8" },
];

export default function Lines() {
  return (
    <section className="flex flex-col w-full bg-[#080808] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] gap-8 sm:gap-10 md:gap-[48px]">
      <div className="flex flex-col gap-[16px] w-full">
        <span className="font-ibm-mono text-[9px] sm:text-[10px] md:text-[12px] font-bold text-[#FFD600] tracking-[1.5px] md:tracking-[3px]">
          [COBERTURA] // 100 COMERCIOS · 12 LÍNEAS · 12 PAÍSES
        </span>
        <h2 className="font-grotesk text-[28px] sm:text-[36px] md:text-[56px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.05] whitespace-pre-line w-full max-w-[700px]">
          {"UN CONECTOR.\nCIEN COMERCIOS."}
        </h2>
        <p className="font-ibm-mono text-[9px] sm:text-[11px] md:text-[13px] text-[#666666] tracking-[0.5px] md:tracking-[1px] leading-[1.6] text-pretty w-full max-w-[600px]">
          EL CONECTOR VTEX ES GENÉRICO. AGREGAR UN COMERCIO NUEVO ES UNA LÍNEA DE CONFIGURACIÓN. TODOS COMPARTEN LA MISMA API PÚBLICA.
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-[2px] w-full">
        {lines.map((line) => (
          <div key={line.name} className="flex flex-col gap-3 sm:gap-4 p-4 sm:p-5 md:p-[32px] bg-[#0F0F0F] border border-[#1D1D1D]">
            <div className="flex items-center gap-3">
              <span className="text-[24px] sm:text-[28px] leading-none">{line.emoji}</span>
              <div className="flex flex-col gap-[2px]">
                <span className="font-grotesk text-[14px] sm:text-[16px] font-bold tracking-[1px]" style={{ color: line.color }}>{line.name}</span>
                <span className="font-ibm-mono text-[9px] sm:text-[10px] text-[#444] tracking-[1px]">{line.count} retailers</span>
              </div>
            </div>
            <p className="font-ibm-mono text-[9px] sm:text-[10px] text-[#666] tracking-[0.5px] leading-[1.5]">{line.stores}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
