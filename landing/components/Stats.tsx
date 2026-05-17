const stats = [
  { value: "8",   label: "SUPERMERCADOS CONECTADOS", border: true },
  { value: "5",   label: "PAÍSES DE LATAM",          border: true },
  { value: "3M+", label: "PRODUCTOS INDEXADOS",      border: true },
  { value: "9",   label: "HERRAMIENTAS MCP",          border: false },
];

export default function Stats() {
  return (
    <section className="flex flex-col w-full bg-[#00FF88] py-10 px-4 sm:py-12 sm:px-6 md:py-[80px] md:px-[120px]">
      <span className="font-ibm-mono text-[12px] font-bold text-[#0A0A0A] tracking-[3px]">
        [03] // IMPACTO REAL
      </span>
      <div className="h-8 md:h-[32px]" />
      <div className="grid grid-cols-2 md:flex w-full gap-[2px] md:gap-0">
        {stats.map((stat, i) => (
          <div
            key={stat.label}
            className={`flex flex-col gap-2 items-center justify-center py-6 md:py-0 md:h-[160px] md:flex-1
              ${stat.border ? "md:border-r-2 md:border-r-[#0A0A0A]" : ""}
              ${i === 0 ? "md:pr-[40px] pr-3" : i === stats.length - 1 ? "md:pl-[40px] pl-3" : "md:px-[40px] px-3"}
              ${i >= 2 ? "border-t-2 border-t-[#0A0A0A] pt-4 md:border-t-0 md:pt-0" : ""}
            `}
          >
            <span className="font-grotesk text-[40px] md:text-[64px] font-bold text-[#0A0A0A] tracking-[-2px] leading-none">
              {stat.value}
            </span>
            <span className="font-ibm-mono text-[10px] md:text-[12px] font-bold text-[#1A1A1A] tracking-[2px] text-center">
              {stat.label}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
