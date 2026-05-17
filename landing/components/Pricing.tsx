"use client";

import { useState } from "react";
import SectionHeader from "./SectionHeader";

interface PlanCardProps {
  tier: string;
  tierColor?: string;
  name: string;
  nameColor?: string;
  description: string;
  btnLabel: string;
  btnLabelColor?: string;
  bgColor?: string;
  borderColor?: string;
  borderWidth?: number;
  btnBg?: string;
  btnBorderColor?: string;
  tierBg?: string;
  tierBorderColor?: string;
  features: { label: string; included: boolean }[];
  accentColor?: string;
}

function PlanCard({
  tier,
  tierColor = "#888888",
  name,
  nameColor = "#F5F5F0",
  description,
  btnLabel,
  btnLabelColor = "#888888",
  bgColor = "#0F0F0F",
  borderColor = "#2D2D2D",
  borderWidth = 1,
  btnBg = "#1A1A1A",
  btnBorderColor = "#3D3D3D",
  tierBg = "#1A1A1A",
  tierBorderColor = "#3D3D3D",
  features,
  accentColor = "#555555",
}: PlanCardProps) {
  const [expanded, setExpanded] = useState(false);
  const visibleFeatures = expanded ? features : features.slice(0, 4);
  const hasMore = features.length > 4;

  return (
    <div
      className="flex flex-col gap-5 sm:gap-6 md:gap-8 p-4 sm:p-6 md:p-[40px] w-full md:flex-1"
      style={{ backgroundColor: bgColor, border: `${borderWidth}px solid ${borderColor}` }}
    >
      <div
        className="flex items-center justify-center h-[28px] px-[12px] w-fit"
        style={{ backgroundColor: tierBg, border: `1px solid ${tierBorderColor}` }}
      >
        <span className="font-ibm-mono text-[11px] tracking-[2px]" style={{ color: tierColor }}>
          {tier}
        </span>
      </div>
      <span className="font-grotesk text-[24px] sm:text-[28px] font-bold tracking-[1px]" style={{ color: nameColor }}>
        {name}
      </span>
      <p className="font-ibm-mono text-[11px] sm:text-[12px] text-[#666666] tracking-[1px] leading-[1.6]">
        {description}
      </p>

      <div className="flex flex-col gap-[10px]" style={{ borderTop: `1px solid ${borderColor === "#0F0F0F" ? "#2D2D2D" : borderColor}` }}>
        <div className="pt-4 sm:pt-6 flex flex-col gap-[8px] sm:gap-[10px]">
          {visibleFeatures.map((f, i) => (
            <div key={i} className="flex items-center gap-3">
              <span
                className="font-ibm-mono text-[14px] leading-none shrink-0"
                style={{ color: f.included ? accentColor : "#333333" }}
              >
                {f.included ? "+" : "—"}
              </span>
              <span
                className="font-ibm-mono text-[10px] sm:text-[11px] tracking-[1px]"
                style={{ color: f.included ? "#A0A09A" : "#3D3D3D" }}
              >
                {f.label}
              </span>
            </div>
          ))}
          {hasMore && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-2 pt-2 text-left"
            >
              <span className="font-ibm-mono text-[10px] tracking-[2px] text-[#555555] hover:text-[#888888] transition-colors">
                {expanded ? "— MOSTRAR MENOS" : `+ VER ${features.length - 4} MÁS`}
              </span>
            </button>
          )}
        </div>
      </div>

      <button
        className="flex items-center justify-center w-full h-[48px] mt-auto"
        style={{ backgroundColor: btnBg, border: `2px solid ${btnBorderColor}` }}
      >
        <span className="font-ibm-mono text-[12px] tracking-[2px]" style={{ color: btnLabelColor }}>
          {btnLabel}
        </span>
      </button>
    </div>
  );
}

const STARTER_FEATURES = [
  { label: "ACCESO A 8 SUPERMERCADOS",        included: true  },
  { label: "BÚSQUEDA Y COMPARACIÓN",          included: true  },
  { label: "API REST BÁSICA",                 included: true  },
  { label: "1 USUARIO",                       included: true  },
  { label: "SOPORTE POR EMAIL",               included: true  },
  { label: "MODO AGENTE (ASK)",               included: false },
  { label: "SERVIDOR MCP",                    included: false },
  { label: "CHECKOUT UNIFICADO",              included: false },
];

const GROWTH_FEATURES = [
  { label: "TODO LO DE STARTER",              included: true  },
  { label: "SERVIDOR MCP (9 HERRAMIENTAS)",   included: true  },
  { label: "CHECKOUT UNIFICADO",              included: true  },
  { label: "HASTA 5 USUARIOS",                included: true  },
  { label: "SOPORTE PRIORITARIO",             included: true  },
  { label: "MODO AGENTE (ASK)",               included: true  },
  { label: "OPEN FOOD FACTS",                 included: true  },
  { label: "API PERSONALIZADA",               included: false },
];

const ENTERPRISE_FEATURES = [
  { label: "TODO LO DE GROWTH",               included: true  },
  { label: "USUARIOS ILIMITADOS",             included: true  },
  { label: "SOPORTE DEDICADO 24/7",           included: true  },
  { label: "WHITE-LABEL",                     included: true  },
  { label: "INTEGRACIONES PERSONALIZADAS",    included: true  },
  { label: "SLA GARANTIZADO",                 included: true  },
  { label: "MÉTRICAS AVANZADAS",              included: true  },
  { label: "ONBOARDING DEDICADO",             included: true  },
];

export default function Pricing() {
  return (
    <section id="pricing" className="flex flex-col w-full bg-[#080808] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] gap-10 sm:gap-12 md:gap-[64px]">
      <SectionHeader
        label="[08] // PLANES"
        title={"PRECIOS CLAROS.\nPARA CADA ESCALA."}
        subtitle="DESDE STARTUPS HASTA GRANDES RETAILERS. COTIZAMOS SEGÚN TUS NECESIDADES."
      />

      <div className="flex flex-col md:flex-row w-full gap-[2px]">
        <PlanCard
          tier="STARTUPS Y DEVS"
          name="STARTER"
          description="IDEAL PARA COMENZAR A INTEGRAR SUPERMERCADOS EN TUS PROYECTOS. ACCEDE A 8 TIENDAS CON UNA SOLA API."
          btnLabel="EMPEZAR AHORA"
          features={STARTER_FEATURES}
          accentColor="#555555"
        />
        <PlanCard
          tier="MÁS POPULAR"
          tierColor="#0A0A0A"
          tierBg="#00FF88"
          tierBorderColor="#00FF88"
          name="GROWTH"
          nameColor="#00FF88"
          description="AGENTES DE IA QUE COMPRAN POR TI. MCP, CHECKOUT UNIFICADO Y MODO AGENTE. EL PLAN FAVORITO DE AGENCIAS Y STARTUPS."
          btnLabel="AGENDAR DEMO"
          btnLabelColor="#0A0A0A"
          bgColor="#111111"
          borderColor="#00FF88"
          borderWidth={2}
          btnBg="#00FF88"
          btnBorderColor="transparent"
          features={GROWTH_FEATURES}
          accentColor="#00FF88"
        />
        <PlanCard
          tier="GRANDES EMPRESAS"
          tierColor="#FF6B35"
          tierBorderColor="#FF6B35"
          name="ENTERPRISE"
          description="SOLUCIÓN COMPLETA Y PERSONALIZADA PARA RETAILERS, MARKETPLACES Y GRANDES ORGANIZACIONES CON NECESIDADES DE ESCALA."
          btnLabel="CONTACTAR VENTAS"
          btnLabelColor="#FF6B35"
          btnBorderColor="#FF6B35"
          features={ENTERPRISE_FEATURES}
          accentColor="#FF6B35"
        />
      </div>

      <p className="font-ibm-mono text-[11px] text-[#444444] tracking-[2px] text-center">
        PLANES MENSUALES // SIN PERMANENCIA // COMISIÓN 1-5% POR TRANSACCIÓN // PRECIOS API POR USO
      </p>
    </section>
  );
}
