"use client";
import { useLang } from "@/lib/LanguageContext";
const data=[
  {e:"🛒",n:"Supermercados",c:14,s:"Wong · Metro · Plaza Vea · Carrefour · Exito · Carulla · Olimpica · Chedraui · HEB · Vea · Jumbo · Mambo · Sam's Club",cl:"#A78BFA"},
  {e:"📱",n:"Electro",c:9,s:"Motorola · Electrolux · Whirlpool — AR, BR, MX, CL, IT, FR",cl:"#3cffd0"},
  {e:"💊",n:"Farmacias",c:2,s:"Drogaria Pacheco · Farmatodo MX",cl:"#FB923C"},
  {e:"🏠",n:"Hogar",c:2,s:"Easy Argentina · Promart Perú",cl:"#FFD600"},
  {e:"🏬",n:"Tiendas Dept.",c:1,s:"Coppel Argentina",cl:"#60A5FA"},
  {e:"👕",n:"Moda",c:2,s:"C&A Brasil · Hering Brasil",cl:"#F472B6"},
];
export default function Lines() {
  const { t: _t } = useLang();
  return (
    <section id="coverage" className="relative flex flex-col w-full bg-[#080808] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#FFD600]/40"/>{_t("lines_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3.5rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">{_t("lines_title")}</h2>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-[1100px]">
        {data.map(l=>(
          <div key={l.n} className="bg-[#131313] border border-[#2d2d2d] p-4 flex flex-col gap-3 hover:border-[#333] transition-all">
            <div className="flex items-center gap-2">
              <span className="text-lg">{l.e}</span>
              <span className="text-xs font-grotesk font-bold" style={{color:l.cl}}>{l.n}</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-grotesk font-bold text-white">{l.c}</span>
              <span className="text-[9px] font-mono text-[#555] uppercase">{_t("lines_stores")}</span>
            </div>
            <p className="text-[10px] font-mono text-[#555] leading-relaxed">{l.s}</p>
          </div>
        ))}
      </div>
      <div className="flex gap-4 max-w-[1100px] flex-wrap">
        <div className="bg-[#131313] border border-[#2d2d2d] px-6 py-3 flex items-center gap-3"><span className="text-2xl font-grotesk font-bold text-white">30</span><span className="text-[10px] font-mono text-[#555] uppercase tracking-wider">{_t("lines_stores_badge")}</span></div>
        <div className="bg-[#131313] border border-[#2d2d2d] px-6 py-3 flex items-center gap-3"><span className="text-2xl font-grotesk font-bold text-white">1</span><span className="text-[10px] font-mono text-[#555] uppercase tracking-wider">{_t("lines_connector_badge")}</span></div>
      </div>
    </section>
  );
}
