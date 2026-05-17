"use client";

import GlitchText from "@/components/GlitchText";

export default function FinalCTA() {
  return (
    <section className="flex flex-col items-center w-full bg-[#0A0A0A] py-12 px-4 sm:py-16 sm:px-6 md:p-[120px] gap-8 sm:gap-10 md:gap-[48px] border-t-2 border-t-[#00FF88]">
      <div className="flex items-center justify-center gap-[6px] sm:gap-[8px] h-[28px] sm:h-[32px] px-[12px] sm:px-[16px] bg-[#1A1A1A] border-2 border-[#00FF88]">
        <span className="font-ibm-mono text-[9px] sm:text-[11px] font-bold text-[#00FF88] tracking-[1px] sm:tracking-[2px]">
          <GlitchText text="[¿LISTO PARA CONECTAR TUS AGENTES?]" speed={30} />
        </span>
      </div>

      <h2 className="font-grotesk text-[32px] sm:text-[44px] md:text-[80px] font-bold text-[#F5F5F0] tracking-[-1px] sm:tracking-[-2px] leading-none text-center w-full max-w-[1000px] whitespace-pre-line">
        <GlitchText text={"SUPERMERCADOS\nCOMO APIs."} speed={40} delay={200} />
      </h2>

      <p className="font-ibm-mono text-[9px] sm:text-[10px] md:text-[14px] text-[#666666] tracking-[0.5px] md:tracking-[2px] text-center text-pretty w-full max-w-[700px] px-2 leading-[1.5]">
        <GlitchText text="ÚNETE A LAS EMPRESAS QUE YA USAN CLI MARKET PARA CONECTAR AGENTES DE IA CON SUPERMERCADOS DE LATAM." speed={20} delay={450} />
      </p>

      <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 md:gap-[16px] w-full sm:w-auto px-2 sm:px-0">
        <a
          href="https://github.com/Treevu-ai/cli-market-latam"
          className="flex items-center justify-center w-full sm:w-[280px] h-[56px] sm:h-[64px] bg-[#00FF88] hover:bg-[#00cc6a] active:scale-[0.98] transition-all"
        >
          <span className="font-grotesk text-[12px] sm:text-[13px] font-bold text-[#0A0A0A] tracking-[1.5px] sm:tracking-[2px]">
            INSTALAR AHORA
          </span>
        </a>
        <a
          href="#pricing"
          className="flex items-center justify-center w-full sm:w-[220px] h-[56px] sm:h-[64px] bg-[#0A0A0A] border-2 border-[#3D3D3D] hover:border-[#888888] active:scale-[0.98] transition-all"
        >
          <span className="font-ibm-mono text-[11px] sm:text-[12px] text-[#666666] tracking-[1.5px] sm:tracking-[2px]">
            VER PLANES
          </span>
        </a>
      </div>

      <p className="font-ibm-mono text-[10px] sm:text-[11px] text-[#555555] tracking-[1px] sm:tracking-[2px] text-center break-all px-2 max-w-full">
        pip install git+https://github.com/Treevu-ai/cli-market-latam.git
      </p>
    </section>
  );
}
