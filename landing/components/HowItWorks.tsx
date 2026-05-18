"use client";
import { useLang } from "@/lib/LanguageContext";
export default function HowItWorks() {
  const { t: _t } = useLang();
  const steps=[
    {n:"01",cmd:"pip install git+https://github.com/Treevu-ai/cli-market-world.git",dk:"how_step1_desc",color:"#00FF88"},
    {n:"02",cmd:"market-server &",dk:"how_step2_desc",color:"#00FF88"},
    {n:"03",cmd:"market login",dk:"how_step3_desc",color:"#00FF88"},
    {n:"04",cmd:'market search "leche" --country PE',dk:"how_step4_desc",color:"#FF6B35"},
    {n:"05",cmd:'market compare "aceite"',dk:"how_step5_desc",color:"#4ADE80"},
    {n:"06",cmd:"market checkout --payment yape",dk:"how_step6_desc",color:"#F5F5F0"},
  ];
  return (
    <section id="how" className="relative flex flex-col w-full bg-[#090909] py-16 px-6 lg:px-12 md:py-[80px] gap-10">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#00FF88]/40"/>{_t("how_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">{_t("how_title")}</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">{_t("how_subtitle")}</p>
      </div>
      <div className="flex flex-wrap gap-4 max-w-[1000px]">
        {steps.map((s,i)=>(
          <div key={i} className="flex items-start gap-4 bg-[#0A0A0A] border border-[#1A1A1A] p-5 min-w-[280px] flex-1 group hover:border-[#333] transition-colors">
            <span className="text-2xl font-grotesk font-bold text-white/10 group-hover:text-white/20">{s.n}</span>
            <div className="flex flex-col gap-1 min-w-0">
              <span className="text-[11px] font-mono break-all" style={{color:s.color}}>{s.cmd}</span>
              <span className="text-[10px] font-mono text-[#444]">{_t(s.dk)}</span>
            </div>
          </div>
        ))}
      </div>
      <p className="text-white/20 font-mono text-[10px] uppercase tracking-widest">INSTALL → SEARCH → COMPARE → CHECKOUT · TODO EN LA TERMINAL</p>
    </section>
  );
}
