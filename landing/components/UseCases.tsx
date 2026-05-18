export default function UseCases() {
  const cases = [
    { title:"Agentes de IA", desc:"Conecta Claude, DeepSeek o GPT a 12 MCP tools. El agente busca, compara y compra de forma autonoma.", icon:"🤖" },
    { title:"Fintech y Hedge Funds", desc:"Data feed de precios en 67 paises. Competitive intelligence cross-border. API REST con JSON parseable.", icon:"📊" },
    { title:"E-commerce", desc:"Una sola integracion para 3,400+ retailers VTEX. Sin licitar APIs por tienda. Un conector generico.", icon:"🛒" },
    { title:"Desarrolladores", desc:"pip install y estas listo. Open source, MIT license. Contribui al conector VTEX mas grande del mundo.", icon:"💻" },
  ];
  return (
    <section id="usecases" className="relative flex flex-col w-full bg-black py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#60A5FA]/40"/>Casos de uso</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05]">Para quien construye.</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">Infraestructura de comercio para agentes de IA, fintechs, e-commerce y desarrolladores.</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-[900px]">
        {cases.map((c,i)=>(
          <div key={i} className="bg-[#0A0A0A] border border-[#1A1A1A] p-6 flex flex-col gap-3 hover:border-[#333] transition-colors">
            <span className="text-2xl">{c.icon}</span>
            <h3 className="text-white font-grotesk font-bold text-lg">{c.title}</h3>
            <p className="text-[#666] font-mono text-xs leading-relaxed">{c.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
