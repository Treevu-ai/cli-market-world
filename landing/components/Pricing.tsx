"use client";
import { useLang } from "@/lib/LanguageContext";

const tiers = [
  { key:"free", title_es:"Free", title_en:"Free", price:"$0", period_es:"para siempre", period_en:"forever", color:"#3cffd0",
    f_es:["30 MCP tools","60 req/min · 1,000 req/día","1 API key (read)","Dashboard en tiempo real","Health checks"],
    f_en:["30 MCP tools","60 req/min · 1,000 req/day","1 API key (read)","Live dashboard","Health checks"],
    cta_es:"Empezar gratis", cta_en:"Start free", href:"https://github.com/Treevu-ai/cli-market-world" },
  { key:"pro", title_es:"Pro", title_en:"Pro", price:"$49", period_es:"/ mes", period_en:"/ month", color:"#FFD600",
    f_es:["Todo lo de Free","300 req/min · 10,000 req/día","10 API keys (read + write)","Checkout habilitado","Data moat export (JSON/CSV)","Soporte prioritario"],
    f_en:["Everything in Free","300 req/min · 10,000 req/day","10 API keys (read + write)","Checkout enabled","Data moat export (JSON/CSV)","Priority support"],
    cta_es:"Suscribirse", cta_en:"Subscribe", href:"mailto:hello@cli-market.dev?subject=CLI%20Market%20Pro&body=Hola%2C%20quiero%20activar%20el%20plan%20Pro%20(USD%2049%2Fmes)." },
  { key:"enterprise", title_es:"Enterprise", title_en:"Enterprise", price_es:"Contactanos", price_en:"Contact us", period_es:"a medida", period_en:"custom", color:"#FF6B35",
    f_es:["Todo lo de Pro","Rate limits custom","API keys ilimitadas","Endpoints dedicados","Webhooks","SLA 99.5%"],
    f_en:["Everything in Pro","Custom rate limits","Unlimited API keys","Dedicated endpoints","Webhooks","SLA 99.5%"],
    cta_es:"Contactar", cta_en:"Contact", href:"mailto:hello@cli-market.dev?subject=CLI%20Market%20Enterprise&body=Hola%2C%20me%20interesa%20el%20plan%20Enterprise.%20Mi%20caso%20de%20uso%20es%3A" },
];

export default function Pricing() {
  const { t, lang } = useLang();

  return (
    <section id="pricing" className="flex flex-col w-full bg-[#131313] py-12 px-4 sm:py-16 sm:px-6 md:py-[80px] md:px-[120px] gap-8 sm:gap-10 md:gap-[48px]">
      <div className="flex flex-col gap-[12px] w-full">
        <span className="font-mono text-[9px] sm:text-[10px] md:text-[11px] font-bold text-[#FFD600] tracking-[2px] md:tracking-[3px] uppercase">{t("pricing_label")}</span>
        <h2 className="font-grotesk text-[26px] sm:text-[32px] md:text-[48px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.05]">
          {lang === "es" ? "Tres planes. Para cada etapa." : "Three plans. For every stage."}
        </h2>
        <p className="font-mono text-[12px] sm:text-[13px] md:text-[15px] text-[#666] tracking-[0.5px] leading-[1.6] max-w-[500px]">
          {lang === "es" ? "30 MCP tools. 30 retailers verificados. Data moat real con 4,400+ precios. Elegí el plan que se ajusta a lo que estás construyendo." : "30 MCP tools. 30 verified retailers. Real data moat with 4,400+ prices. Pick the plan that fits what you are building."}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-[900px]">
        {tiers.map((tier) => (
          <div key={tier.key} className="flex flex-col gap-4 p-6 bg-[#1a1a1a] border border-[#1D1D1D] hover:border-[#333] transition-all">
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
        {lang==="es" ? "OPEN SOURCE · MIT · 30 MCP TOOLS · 30 RETAILERS · 8 PAÍSES" : "OPEN SOURCE · MIT · 30 MCP TOOLS · 30 RETAILERS · 8 COUNTRIES"}
      </p>
    </section>
  );
}
