"use client";

import SectionHeader from "./SectionHeader";

interface FeatureCardProps {
  iconColor: string;
  title: string;
  description: string;
  tag: string;
  tagColor: string;
  bgColor?: string;
  borderColor?: string;
}

function FeatureCard({
  iconColor,
  title,
  description,
  tag,
  tagColor,
  bgColor = "#111111",
  borderColor = "#2D2D2D",
}: FeatureCardProps) {
  return (
    <div
      className="flex flex-col gap-4 sm:gap-5 p-5 sm:p-8 md:p-[32px] border-l-4 md:border-l md:border w-full md:flex-1"
      style={{ backgroundColor: bgColor, borderLeftColor: iconColor, borderColor: `transparent transparent transparent ${iconColor}` }}
    >
      <div className="w-[36px] h-[36px] sm:w-[40px] sm:h-[40px] shrink-0" style={{ backgroundColor: iconColor }} />
      <h3 className="font-grotesk text-[16px] sm:text-[18px] font-bold text-[#F5F5F0] tracking-[0.5px] sm:tracking-[1px] leading-[1.2] whitespace-pre-line">
        {title}
      </h3>
      <p className="font-ibm-mono text-[11px] sm:text-[12px] text-[#666666] tracking-[0.5px] sm:tracking-[1px] leading-[1.5] sm:leading-[1.6]">
        {description}
      </p>
      <div
        className="flex items-center justify-center h-[26px] sm:h-[28px] px-[10px] sm:px-[12px] bg-[#1A1A1A] border w-fit mt-auto"
        style={{ borderColor: tagColor }}
      >
        <span className="font-ibm-mono text-[10px] sm:text-[11px] tracking-[1.5px] sm:tracking-[2px]" style={{ color: tagColor }}>
          {tag}
        </span>
      </div>
    </div>
  );
}

export default function Features() {
  return (
    <section
      id="features"
      className="flex flex-col w-full bg-[#0A0A0A] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] gap-10 sm:gap-12 md:gap-[64px]"
    >
      <SectionHeader
        label="[01] // COMANDOS"
        title={"UNA CLI.\nOCHO SUPERMERCADOS."}
        subtitle="INFRAESTRUCTURA UNIFICADA PARA BUSCAR, COMPARAR Y COMPRAR DESDE LA TERMINAL."
      />

      <div className="flex flex-col md:flex-row w-full gap-[2px]">
        <FeatureCard
          iconColor="#00FF88"
          title={"BÚSQUEDA\nMULTITIENDA"}
          description="BUSCA PRODUCTOS EN 8 SUPERMERCADOS SIMULTÁNEAMENTE. RESULTADOS EN MILISEGUNDOS, FORMATEADOS COMO JSON O TABLAS."
          tag="SEARCH"
          tagColor="#00FF88"
          borderColor="#00FF88"
        />
        <FeatureCard
          iconColor="#FF6B35"
          title={"COMPARACIÓN\nDE PRECIOS"}
          description="COMPARA EL MISMO PRODUCTO ENTRE TIENDAS Y PAÍSES. TOMA DECISIONES DE COMPRA CON DATOS, NO CON INTUICIÓN."
          tag="COMPARE"
          tagColor="#FF6B35"
          bgColor="#0F0F0F"
          borderColor="#FF6B35"
        />
        <FeatureCard
          iconColor="#60A5FA"
          title={"CARRO Y\nCHECKOUT"}
          description="AGREGA PRODUCTOS AL CARRO, GESTIONA CANTIDADES Y COMPLETA LA COMPRA. FLUJO COMPLETO DESDE LA TERMINAL."
          tag="CART"
          tagColor="#60A5FA"
          borderColor="#60A5FA"
        />
        <FeatureCard
          iconColor="#FFD600"
          title={"MODO AGENTE\nCON IA"}
          description='USA LENGUAJE NATURAL: "COMPRA ARROZ", "COMPARA ACEITE", "REPITE LA ÚLTIMA COMPRA". EL AGENTE RESUELVE POR TI.'
          tag="ASK"
          tagColor="#FFD600"
          borderColor="#FFD600"
        />
      </div>
    </section>
  );
}
