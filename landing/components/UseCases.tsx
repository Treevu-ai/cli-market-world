import { useLang } from "@/lib/LanguageContext";
export default function UseCases() {
  const { t: _t } = useLang();
  const cases = [
    { dk:"Agentes de IA" , dd:"Conecta Claude, DeepSeek o GPT a 12 MCP tools. El agente busca, compara y compra de forma autonoma.", icon:"🤖" },
    { dk:"Fintech y Hedge Funds" , dd:"Data feed de precios en 67 paises. Competitive intelligence cross-border. API REST con JSON parseable.", icon:"📊" },
    { dk:"E-commerce" , dd:"Una sola integracion para 3,600+ retailers VTEX. Sin licitar APIs por tienda. Un conector generico.", icon:"🛒" },
    { dk:"Desarrolladores" , dd:"pip install y estas listo. Open source, MIT license. Contribui al conector VTEX mas grande del mundo.", icon:"💻" },
  ];
  return (
    <section id="usecases" className="relative flex flex-col w-full bg-black py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#60A5FA]/40"/>{_t("usecases_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05]">{_t("usecases_title")}</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">{_t("usecases_subtitle")}</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-[900px]">
        {cases.map((c,i)=>(
          <div key={i} className="bg-[#0A0A0A] border border-[#1A1A1A] p-6 flex flex-col gap-3 hover:border-[#333] transition-colors">
            <span className="text-2xl">{c.icon}</span>
            <h3 className="text-white font-grotesk font-bold text-lg">{_t(c.dk)}</h3>
            <p className="text-[#666] font-mono text-xs leading-relaxed">{_t(c.dd)}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
