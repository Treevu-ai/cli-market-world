import SectionHeader from "./SectionHeader";

export default function Bento() {
  return (
    <section className="flex flex-col w-full bg-[#0D0D0D] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] gap-8 sm:gap-10 md:gap-[48px]">
      <SectionHeader
        label="[04] // CAPACIDADES TÉCNICAS"
        title={"TECNOLOGÍA.\nPARA AGENTES IA."}
        titleWidth="w-full max-w-[800px]"
      />

      <div className="flex flex-col w-full gap-[2px]">
        {/* Row 1 */}
        <div className="flex flex-col md:flex-row w-full gap-[2px]">
          <div className="flex flex-col gap-4 sm:gap-5 p-5 sm:p-8 md:p-[40px] bg-[#00FF88] w-full md:flex-1">
            <span className="font-ibm-mono text-[11px] font-bold text-[#1A1A1A] tracking-[2px]">[01]</span>
            <h3 className="font-grotesk text-[24px] md:text-[28px] font-bold text-[#0A0A0A] tracking-[-1px] leading-[1.1] whitespace-pre-line">
              {"API UNIFICADA\nMULTITIENDA"}
            </h3>
            <p className="font-ibm-mono text-[12px] text-[#1A1A1A] tracking-[1px] leading-[1.6]">
              UNA SOLA API PARA 17 COMERCIOS EN 6 LÍNEAS Y 5 PAÍSES. ABSTRAE LAS DIFERENCIAS ENTRE VTEX, APIs PROPIETARIAS Y OPEN FOOD FACTS.
            </p>
            <div className="flex items-center justify-center h-[28px] px-[12px] bg-[#0A0A0A] w-fit">
              <span className="font-ibm-mono text-[10px] font-bold text-[#00FF88] tracking-[2px]">[VTEX]</span>
            </div>
          </div>

          <div className="flex flex-col gap-4 sm:gap-5 p-5 sm:p-8 md:p-[40px] bg-[#111111] border border-[#2D2D2D] w-full md:flex-1">
            <span className="font-ibm-mono text-[11px] font-bold text-[#00FF88] tracking-[2px]">[02]</span>
            <h3 className="font-grotesk text-[24px] md:text-[28px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.1] whitespace-pre-line">
              {"COMPATIBLE\nCON MCP"}
            </h3>
            <p className="font-ibm-mono text-[12px] text-[#666666] tracking-[1px] leading-[1.6]">
              12 HERRAMIENTAS MCP LISTAS PARA USAR. CONECTA TUS AGENTES DE IA EN MINUTOS. COMPATIBLE CON DEEPSEEK, CLAUDE Y CUALQUIER CLIENTE MCP.
            </p>
          </div>

          <div className="flex flex-col gap-4 sm:gap-5 p-5 sm:p-8 md:p-[40px] bg-[#0A0A0A] border border-[#2D2D2D] w-full md:flex-1">
            <span className="font-ibm-mono text-[11px] font-bold text-[#00FF88] tracking-[2px]">[03]</span>
            <h3 className="font-grotesk text-[24px] md:text-[28px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.1] whitespace-pre-line">
              {"REST API\nNATIVA"}
            </h3>
            <p className="font-ibm-mono text-[12px] text-[#666666] tracking-[1px] leading-[1.6]">
              ENDPOINTS REST COMPLETOS PARA INTEGRACIÓN TRADICIONAL. TODOS LOS COMANDOS DEL CLI EXPUESTOS COMO API HTTP.
            </p>
            <div className="flex items-center justify-center h-[28px] px-[12px] bg-[#1A1A1A] border border-[#FF6B35] w-fit">
              <span className="font-ibm-mono text-[10px] font-bold text-[#FF6B35] tracking-[2px]">[REST]</span>
            </div>
          </div>
        </div>

        {/* Row 2 */}
        <div className="flex flex-col md:flex-row w-full gap-[2px]">
          <div className="flex flex-col gap-4 sm:gap-5 p-5 sm:p-8 md:p-[40px] bg-[#111111] border border-[#2D2D2D] w-full md:flex-1">
            <span className="font-ibm-mono text-[11px] font-bold text-[#00FF88] tracking-[2px]">[04]</span>
            <h3 className="font-grotesk text-[24px] md:text-[28px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.1] whitespace-pre-line">
              {"RESPUESTAS\nEN JSON"}
            </h3>
            <p className="font-ibm-mono text-[12px] text-[#666666] tracking-[1px] leading-[1.6]">
              USA EL FLAG --json PARA OBTENER RESULTADOS PARSEABLES POR LLMs. DISEÑADO PARA EL CONSUMO AUTÓNOMO POR AGENTES DE IA.
            </p>
          </div>

          <div className="flex flex-col gap-4 sm:gap-5 p-5 sm:p-8 md:p-[40px] bg-[#0F0F0F] border-2 border-[#FF6B35] w-full md:flex-1">
            <span className="font-ibm-mono text-[11px] font-bold text-[#FF6B35] tracking-[2px]">[05]</span>
            <h3 className="font-grotesk text-[24px] md:text-[28px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.1] whitespace-pre-line">
              {"OPEN FOOD\nFACTS"}
            </h3>
            <p className="font-ibm-mono text-[12px] text-[#666666] tracking-[1px] leading-[1.6]">
              ACCEDE A MÁS DE 3 MILLONES DE PRODUCTOS GLOBALES. INFORMACIÓN NUTRICIONAL, CÓDIGOS DE BARRAS Y ENRIQUECIMIENTO DE DATOS.
            </p>
            <div className="flex items-center justify-center h-[28px] px-[12px] bg-[#1A1A1A] border border-[#FF6B35] w-fit">
              <span className="font-ibm-mono text-[10px] font-bold text-[#FF6B35] tracking-[2px]">[DATA]</span>
            </div>
          </div>

          <div className="flex flex-col gap-4 sm:gap-5 p-5 sm:p-8 md:p-[40px] bg-[#0A0A0A] border border-[#2D2D2D] w-full md:flex-1">
            <span className="font-ibm-mono text-[11px] font-bold text-[#00FF88] tracking-[2px]">[06]</span>
            <h3 className="font-grotesk text-[24px] md:text-[28px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.1] whitespace-pre-line">
              {"MODO AGENTE\nAUTÓNOMO"}
            </h3>
            <p className="font-ibm-mono text-[12px] text-[#666666] tracking-[1px] leading-[1.6]">
              COMANDO "MARKET ASK" CON LENGUAJE NATURAL. EL AGENTE DECIDE QUÉ HERRAMIENTAS USAR PARA CUMPLIR TU SOLICITUD.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
