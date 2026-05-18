"use client";
import { useLang } from "@/lib/LanguageContext";
const data=[
  {e:"👕",n:"Moda",c:1560,s:"Louis Vuitton · Gucci · Prada · Zara · H&M · Levi's · Lamborghini",cl:"#FF6B35"},
  {e:"📱",n:"Electro",c:571,s:"Samsung · Apple · Sony · LG · Dell · HP · Yamaha · Dyson",cl:"#00FF88"},
  {e:"🏠",n:"Hogar",c:314,s:"IKEA · Homecenter · Sodimac · Miele · Bosch · Tefal · KitchenAid",cl:"#FFD600"},
  {e:"⚽",n:"Deportes",c:306,s:"Nike · Adidas · Puma · Under Armour · Decathlon · Foot Locker · Patagonia",cl:"#4ADE80"},
  {e:"🛒",n:"Supermercados",c:252,s:"Wong · Carrefour · Jumbo · Coto · Costco · Sainsbury's · Edeka",cl:"#A78BFA"},
  {e:"🍔",n:"Alimentos",c:176,s:"Nestle · Unilever · Coca-Cola · Pepsi · Lindt · Heineken · Nespresso",cl:"#F87171"},
  {e:"💄",n:"Belleza",c:170,s:"Sephora · MAC · Clinique · Estee Lauder · Lancome · Lush",cl:"#F472B6"},
  {e:"🏬",n:"Departamentales",c:136,s:"Mercado Libre · El Corte Ingles · Otto · Miniso · Lego · Americanas",cl:"#38BDF8"},
  {e:"💊",n:"Farmacias",c:51,s:"Droga Raia · Drogasil · Boots · DM · Rossmann",cl:"#FB923C"},
  {e:"🔧",n:"Autopartes",c:50,s:"BMW · Mercedes-Benz · Audi · Tesla · Harley Davidson · Ducati",cl:"#94A3B8"},
  {e:"📚",n:"Libreria",c:11,s:"Staples · Office Depot",cl:"#A3E635"},
  {e:"🐾",n:"Mascotas",c:6,s:"Petco · Petlove · Petz · Tiendanimal",cl:"#E879F9"},
];
export default function Lines() {
  const { t: _t } = useLang();
  return (
    <section id="coverage" className="relative flex flex-col w-full bg-[#080808] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#FFD600]/40"/>{_t("lines_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3.5rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">{_t("lines_title")}</h2>
        <p className="text-white/40 font-mono text-sm leading-relaxed">{_t("lines_subtitle")}</p>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 max-w-[1100px]">
        {data.map(l=>(
          <div key={l.n} className="group bg-[#0A0A0A] border border-[#1A1A1A] p-4 flex flex-col gap-2 hover:border-[#333] transition-all hover:bg-[#0F0F0F]">
            <div className="flex items-center justify-between"><span className="text-xl">{l.e}</span><span className="text-xs font-mono font-bold text-white/20 tabular-nums">{l.c.toLocaleString()}</span></div>
            <span className="text-[11px] font-grotesk font-bold text-white/80">{l.n}</span>
            <p className="text-[9px] font-mono text-[#444] leading-relaxed line-clamp-2 group-hover:text-[#666]">{l.s}</p>
            <div className="mt-1 h-[2px] w-8 group-hover:w-full transition-all duration-300" style={{backgroundColor:l.cl}}/>
          </div>
        ))}
      </div>
      <div className="flex gap-4 max-w-[1100px] flex-wrap">
        <div className="bg-[#0A0A0A] border border-[#1A1A1A] px-6 py-3 flex items-center gap-3"><span className="text-2xl font-grotesk font-bold text-white">3,760+</span><span className="text-[10px] font-mono text-[#555] uppercase tracking-wider">Comercios en 67 paises</span></div>
        <div className="bg-[#0A0A0A] border border-[#1A1A1A] px-6 py-3 flex items-center gap-3"><span className="text-2xl font-grotesk font-bold text-white">1</span><span className="text-[10px] font-mono text-[#555] uppercase tracking-wider">Conector VTEX generico</span></div>
      </div>
    </section>
  );
}
