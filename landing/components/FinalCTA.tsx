"use client";
import GlitchText from "@/components/GlitchText";

export default function FinalCTA() {
  return (
    <section className="flex flex-col items-center w-full bg-[#0A0A0A] py-16 px-4 sm:py-20 sm:px-6 md:py-[100px] gap-8 sm:gap-10 border-t border-[#1A1A1A]">
      <div className="flex items-center justify-center gap-[6px] h-[28px] sm:h-[32px] px-[12px] sm:px-[16px] bg-[#1A1A1A] border border-[#00FF88]">
        <span className="font-mono text-[9px] sm:text-[11px] font-bold text-[#00FF88] tracking-[1px]">
          <GlitchText text="[¿Listo para conectar tus agentes?]" speed={30} />
        </span>
      </div>
      <h2 className="font-grotesk text-[32px] sm:text-[44px] md:text-[72px] font-bold text-[#F5F5F0] tracking-[-1px] leading-none text-center whitespace-pre-line">
        <GlitchText text={"Comercio\npara agentes IA."} speed={40} delay={200} />
      </h2>
      <p className="font-mono text-[11px] sm:text-[12px] md:text-[14px] text-[#666] tracking-[0.5px] leading-[1.6] text-center max-w-[560px] px-2">
        El CLI es open source. La API tiene free tier. Si estás construyendo agentes de IA, este es tu punto de partida.
      </p>
      <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4">
        <a href="https://github.com/Treevu-ai/cli-market-latam"
          className="group inline-flex items-center gap-3 border border-[#333] px-6 py-3 font-mono text-[11px] uppercase tracking-widest text-[#AAA] hover:border-[#00FF88] hover:text-[#00FF88] transition-all">
          Instalar CLI
          <span className="transition-transform duration-300 group-hover:translate-x-1">→</span>
        </a>
        <a href="https://t.me/climarketbot"
          className="font-mono text-[11px] uppercase tracking-widest text-[#555] hover:text-[#888] transition-colors">
          Contactar
        </a>
      </div>
      <p className="font-mono text-[10px] sm:text-[11px] text-[#555] tracking-[1px] text-center break-all px-4 max-w-full">
        pip install git+https://github.com/Treevu-ai/cli-market-latam.git
      </p>
    </section>
  );
}
