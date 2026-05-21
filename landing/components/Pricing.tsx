"use client";
import { useLang } from "@/lib/LanguageContext";

const tiers = [
  { key:"free", title_es:"Free", title_en:"Free", price:"$0", period_es:"para siempre", period_en:"forever", color:"#00FF88",
    f_es:["CLI + 15 MCP tools","100 requests / dia","Busquedas ilimitadas","Carrito + checkout","Acceso API cloud"],
    f_en:["CLI + 15 MCP tools","100 requests / day","Unlimited searches","Cart + checkout","Cloud API access"],
    cta_es:"Empezar gratis", cta_en:"Start free", href:"https://github.com/Treevu-ai/cli-market-world" },
  { key:"pro", title_es:"Pro", title_en:"Pro", price:"$29", period_es:"/ mes", period_en:"/ month", color:"#FFD600",
    f_es:["Todo lo de Free","1,000 requests / dia","Data moat: historico de precios","Export CSV / JSON","Inflation tracker (API)","Soporte email prioritario"],
    f_en:["Everything in Free","1,000 requests / day","Data moat: price history","CSV / JSON export","Inflation tracker (API)","Priority email support"],
    cta_es:"Suscribirse", cta_en:"Subscribe", href:"mailto:hello@cli-market.dev?subject=Pro" },
  { key:"enterprise", title_es:"Enterprise", title_en:"Enterprise", price_es:"Contactanos", price_en:"Contact us", period_es:"a medida", period_en:"custom", color:"#FF6B35",
    f_es:["Todo lo de Pro","Rate limits custom","SLA 99.5%","Endpoints dedicados","Data feed tiempo real","White-label","Integracion custom"],
    f_en:["Everything in Pro","Custom rate limits","SLA 99.5%","Dedicated endpoints","Real-time data feed","White-label","Custom integration"],
    cta_es:"Contactar", cta_en:"Contact", href:"mailto:hello@cli-market.dev?subject=Enterprise" },
];

export default function Pricing() {
  const { t, lang } = useLang();

  return (
    <section id="pricing" className="flex flex-col w-full bg-[#060606] py-12 px-4 sm:py-16 sm:px-6 md:py-[80px] md:px-[120px] gap-8 sm:gap-10 md:gap-[48px]">
      <div className="flex flex-col gap-[12px] w-full">
        <span className="font-mono text-[9px] sm:text-[10px] md:text-[11px] font-bold text-[#FFD600] tracking-[2px] md:tracking-[3px] uppercase">{t("pricing_label")}</span>
        <h2 className="font-grotesk text-[26px] sm:text-[32px] md:text-[48px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.05]">
          {lang === "es" ? "Tres planes. Para cada etapa." : "Three plans. For every stage."}
        </h2>
        <p className="font-mono text-[12px] sm:text-[13px] md:text-[15px] text-[#666] tracking-[0.5px] leading-[1.6] max-w-[500px]">
          {lang === "es" ? "15 MCP tools. 27 retailers verificados. Data moat real. Elige el plan que se ajusta a lo que estas construyendo." : "15 MCP tools. 27 verified retailers. Real data moat. Pick the plan that fits what you are building."}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-[900px]">
        {tiers.map((tier) => (
          <div key={tier.key} className="flex flex-col gap-4 p-6 bg-[#0F0F0F] border border-[#1D1D1D] hover:border-[#333] transition-all">
            <span className="font-mono text-[11px] font-bold tracking-[2px] uppercase" style={{ color: tier.color }}>
              {lang==="es" ? tier.title_es : tier.title_en}
            </span>
            <div className="flex items-baseline gap-1">
              <span className="font-grotesk text-4xl font-bold text-white">{tier.price}</span>
              <span className="font-mono text-xs text-[#555]">{lang==="es" ? tier.period_es : tier.period_en}</span>
            </div>
            <ul className="flex flex-col gap-2 font-mono text-xs text-[#888] flex-1">
              {(lang==="es" ? tier.f_es : tier.f_en).map((f,i) => (
                <li key={i} className="flex items-start gap-2"><span className="text-[10px] mt-0.5 shrink-0" style={{color:tier.color}}>·</span><span>{f}</span></li>
              ))}
            </ul>
            <a href={tier.href} className="inline-flex items-center justify-center gap-2 border px-6 py-3 font-mono text-[11px] uppercase tracking-widest transition-all mt-2" style={{borderColor:`${tier.color}40`,color:tier.color}}>
              {lang==="es" ? tier.cta_es : tier.cta_en}
            </a>
          </div>
        ))}
      </div>

      <p className="font-mono text-[10px] text-[#444] tracking-[2px] text-center mt-4">
        {lang==="es" ? "OPEN SOURCE · MIT · 15 MCP TOOLS · 27 RETAILERS · 8 PAISES" : "OPEN SOURCE · MIT · 15 MCP TOOLS · 27 RETAILERS · 8 COUNTRIES"}
      </p>
    </section>
  );
}
