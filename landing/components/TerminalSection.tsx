"use client";
export default function TerminalSection() {
  return (
    <section id="terminal" className="relative flex flex-col w-full bg-black py-16 px-6 lg:px-12 md:py-[80px] gap-10">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#00FF88]/40"/>Terminal</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05]">Una CLI. Miles de comercios.</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">Instalá, autenticate y empezá a buscar en 3,200+ retailers VTEX desde la terminal. Sin interfaz. Sin navegador. Pura infraestructura.</p>
      </div>
      <div className="w-full max-w-[800px] bg-[#0A0A0A] border border-[#1A1A1A] overflow-x-auto font-mono text-[10px] sm:text-[11px] md:text-[12px] leading-[1.7]">
        <div className="flex items-center gap-2 px-4 py-2 bg-[#0F0F0F] border-b border-[#1A1A1A]">
          <div className="w-[10px] h-[10px] rounded-full bg-[#FF5F57]"/><div className="w-[10px] h-[10px] rounded-full bg-[#FEBC2E]"/><div className="w-[10px] h-[10px] rounded-full bg-[#28C840]"/>
          <span className="ml-3 text-[10px] text-[#555] tracking-wider">cli-market — bash</span>
        </div>
        <div className="p-4 sm:p-6 space-y-3 text-[#888]">
          <div className="break-all"><span className="text-[#555]">$</span> <span className="text-[#00FF88]">pip install</span> <span className="text-[#FFD600]">git+https://github.com/Treevu-ai/cli-market-world.git</span></div>
          <div className="text-[#444] text-[10px] pl-4">→ Instalá el CLI en tu sistema</div>
          <div className="pt-2"><span className="text-[#555]">$</span> <span className="text-[#00FF88]">market-server</span> <span className="text-[#555]">&</span></div>
          <div className="text-[#444] text-[10px] pl-4">→ Levantá el backend en localhost:8765</div>
          <div className="pt-2"><span className="text-[#555]">$</span> <span className="text-[#00FF88]">market login</span></div>
          <div className="text-[#444] text-[10px] pl-4">→ Autenticate para acceder a 3,200+ retailers</div>
          <div className="pt-2"><span className="text-[#555]">$</span> <span className="text-[#FF6B35]">market search</span> <span className="text-[#AAA]">"leche"</span> <span className="text-[#888]">--country PE</span></div>
          <div className="pl-4 text-[10px]"><span className="text-[#00FF88]">1.</span> <span className="text-[#CCC]">Leche Gloria 400ml</span> <span className="text-[#888]">Wong</span> <span className="text-[#FFD600]">S/3.50</span></div>
          <div className="pt-2"><span className="text-[#555]">$</span> <span className="text-[#4ADE80]">market compare</span> <span className="text-[#AAA]">"aceite"</span></div>
          <div className="pl-4 text-[10px]"><span className="text-[#888]">Aceite Primor 1L → S/8.90 Wong 🇵🇪</span><br/><span className="text-[#888]">Aceite Natura 900ml → ARS 1,250 Carrefour 🇦🇷</span><br/><span className="text-[#888]">Aceite Liza 900ml → R$6.50 Carrefour BR 🇧🇷</span></div>
          <div className="pt-2"><span className="text-[#555]">$</span> <span className="text-[#F5F5F0]">market add 1 --qty 2</span></div>
          <div className="text-[#444] text-[10px] pl-4">→ Agregá al carrito desde el resultado de búsqueda</div>
          <div className="pt-2"><span className="text-[#555]">$</span> <span className="text-[#F5F5F0]">market checkout --payment yape</span></div>
          <div className="text-[#444] text-[10px] pl-4">→ Completá la compra con métodos de pago locales</div>
          <div className="pt-4"><span className="text-[#555]">$</span> <span className="inline-block w-[8px] h-[14px] bg-[#00FF88] animate-pulse align-middle"/></div>
        </div>
      </div>
      <p className="text-white/30 font-mono text-[10px] uppercase tracking-widest max-w-[800px]">OPEN SOURCE · MIT LICENSE · pip install · 3,200+ COMERCIOS · 67 PAÍSES</p>
    </section>
  );
}
