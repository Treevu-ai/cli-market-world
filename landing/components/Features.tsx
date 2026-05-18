"use client";
import { useLang } from "@/lib/LanguageContext";

const cards = [
  { i:"🤖", t:"features_mcp_title", d:"features_mcp_desc", c:"#00FF88", tag:"MCP" },
  { i:"📊", t:"features_datafeed_title", d:"features_datafeed_desc", c:"#FFD600", tag:"API" },
  { i:"🌍", t:"features_compare_title", d:"features_compare_desc", c:"#4ADE80", tag:"CROSS" },
  { i:"💳", t:"features_cart_title", d:"features_cart_desc", c:"#FF6B35", tag:"PAY" },
  { i:"{ }", t:"features_json_title", d:"features_json_desc", c:"#60A5FA", tag:"JSON" },
  { i:"📦", t:"features_search_title", d:"features_search_desc", c:"#A78BFA", tag:"DATA" },
];

function Card({ icon, title, desc, color, tag }: { icon:string; title:string; desc:string; color:string; tag:string }) {
  return (
    <div className="bg-[#0A0A0A] border border-[#1A1A1A] p-5 flex flex-col gap-3 group hover:border-[#333] transition-all">
      <div className="flex items-center justify-between">
        <span className="text-xl">{icon}</span>
        <span className="text-[9px] font-mono uppercase tracking-widest px-2 py-0.5 border" style={{color, borderColor:color, background:`${color}08`}}>{tag}</span>
      </div>
      <h3 className="text-sm font-grotesk font-bold text-white whitespace-pre-line leading-tight">{title}</h3>
      <p className="text-[11px] font-mono text-[#555] leading-relaxed">{desc}</p>
    </div>
  );
}

export default function Features() {
  const { t: _t } = useLang();
  return (
    <section id="features" className="relative flex flex-col w-full bg-black py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#00FF88]/40"/>{_t("features_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">{_t("features_title")}</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">{_t("features_subtitle")}</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-w-[1000px]">
        {cards.map((c,i)=><Card key={i} icon={c.i} title={_t(c.t)} desc={_t(c.d)} color={c.c} tag={c.tag}/>)}
      </div>
      <p className="text-white/20 font-mono text-[10px] uppercase tracking-widest max-w-[800px]">MCP NATIVO · API REST · JSON PARSEABLE · CROSS-BORDER · DATA FEED · CHECKOUT LOCAL</p>
    </section>
  );
}
