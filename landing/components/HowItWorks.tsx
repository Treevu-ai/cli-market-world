import SectionHeader from "./SectionHeader";

interface StepCardProps {
  number: string;
  title: string;
  description: string;
  bgColor?: string;
  borderColor?: string;
  borderWidth?: number;
}

function StepCard({
  number,
  title,
  description,
  bgColor = "#0A0A0A",
  borderColor = "#2D2D2D",
  borderWidth = 1,
}: StepCardProps) {
  return (
    <div
      className="flex flex-col gap-3 sm:gap-4 p-5 sm:p-8 md:p-[40px] border w-full md:flex-1"
      style={{ backgroundColor: bgColor, borderColor, borderWidth }}
    >
      <span className="font-grotesk text-[48px] font-bold text-[#00FF88] tracking-[-2px]">
        {number}
      </span>
      <h3 className="font-grotesk text-[20px] font-bold text-[#F5F5F0] tracking-[1px] leading-[1.2] whitespace-pre-line">
        {title}
      </h3>
      <p className="font-ibm-mono text-[11px] text-[#555555] tracking-[1px] leading-[1.5]">
        {description}
      </p>
    </div>
  );
}

export default function HowItWorks() {
  return (
    <section className="flex flex-col w-full bg-[#0D0D0D] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] gap-10 sm:gap-12 md:gap-[64px]">
      <SectionHeader
        label="[02] // CÓMO FUNCIONA"
        title={"TRES PASOS.\nTU SUPERMERCADO EN APIs."}
      />

      <div className="flex flex-col md:flex-row w-full gap-[2px]">
        <StepCard
          number="01"
          title={"CONECTA\nTUS TIENDAS"}
          description="INSTALA EL CLI Y AUTENTÍCATE. ACCEDE A 17 COMERCIOS EN 6 LÍNEAS Y 5 PAÍSES CON UNA SOLA HERRAMIENTA. COMPATIBLE CON VTEX."
        />
        <StepCard
          number="02"
          title={"BUSCA, COMPARA\nY COMPRA"}
          description="BUSCA PRODUCTOS, COMPARA PRECIOS ENTRE TIENDAS, AGREGA AL CARRO Y COMPLETA LA COMPRA. TODO DESDE LA TERMINAL."
          bgColor="#111111"
          borderColor="#00FF88"
          borderWidth={1}
        />
        <StepCard
          number="03"
          title={"CONECTA TUS\nAGENTES IA"}
          description="USA EL SERVIDOR MCP PARA QUE TUS AGENTES DE IA COMPREN POR TI. 12 HERRAMIENTAS LISTAS PARA DEEPSEEK, CLAUDE Y MÁS."
        />
      </div>
    </section>
  );
}
