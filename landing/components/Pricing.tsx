"use client";
import { useState } from "react";

interface PlanCardProps {
  tier: string; tierColor?: string; name: string; nameColor?: string;
  description: string; price: string; btnLabel: string; btnLabelColor?: string;
  bgColor?: string; borderColor?: string; borderWidth?: number;
  btnBg?: string; btnBorderColor?: string; tierBg?: string; tierBorderColor?: string;
  features: { label: string; included: boolean }[]; accentColor?: string;
}

function PlanCard(p: PlanCardProps) {
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? p.features : p.features.slice(0, 4);
  const more = p.features.length > 4 && !expanded;
  return (
    <div className="flex flex-col gap-5 sm:gap-6 p-4 sm:p-6 md:p-[32px] w-full md:flex-1"
      style={{ backgroundColor: p.bgColor || "#0F0F0F", border: `${p.borderWidth || 1}px solid ${p.borderColor || "#1D1D1D"}` }}>
      <div className="flex items-center justify-center h-[24px] px-[10px] w-fit"
        style={{ backgroundColor: p.tierBg || "#1A1A1A", border: `1px solid ${p.tierBorderColor || "#2D2D2D"}` }}>
        <span className="font-mono text-[10px] tracking-[2px]" style={{ color: p.tierColor || "#888" }}>{p.tier}</span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="font-grotesk text-[22px] sm:text-[26px] font-bold tracking-[1px]" style={{ color: p.nameColor || "#F5F5F0" }}>{p.name}</span>
        <span className="font-mono text-[11px] text-[#555]">{p.price}</span>
      </div>
      <p className="font-mono text-[10px] sm:text-[11px] text-[#666] tracking-[0.5px] leading-[1.5]">{p.description}</p>
      <div className="flex flex-col gap-[8px] pt-3" style={{ borderTop: "1px solid #1A1A1A" }}>
        {visible.map((f, i) => (
          <div key={i} className="flex items-center gap-3">
            <span className="font-mono text-[12px] leading-none shrink-0" style={{ color: f.included ? (p.accentColor || "#555") : "#333" }}>{f.included ? "+" : "—"}</span>
            <span className="font-mono text-[9px] sm:text-[10px] tracking-[1px]" style={{ color: f.included ? "#A0A09A" : "#3D3D3D" }}>{f.label}</span>
          </div>
        ))}
        {more && (
          <button onClick={() => setExpanded(true)} className="flex items-center gap-2 pt-1 text-left">
            <span className="font-mono text-[9px] tracking-[2px] text-[#555] hover:text-[#888]">+ VER {p.features.length - 4} MÁS</span>
          </button>
        )}
      </div>
      <button className="flex items-center justify-center w-full h-[44px] mt-2" style={{ backgroundColor: p.btnBg || "#1A1A1A", border: `2px solid ${p.btnBorderColor || "#2D2D2D"}` }}>
        <span className="font-mono text-[11px] tracking-[2px]" style={{ color: p.btnLabelColor || "#888" }}>{p.btnLabel}</span>
      </button>
    </div>
  );
}

const STARTER = [
  { label: "100 COMERCIOS EN 12 LÍNEAS", included: true },
  { label: "BÚSQUEDA Y COMPARACIÓN", included: true },
  { label: "API REST + CSV", included: true },
  { label: "1 USUARIO", included: true },
  { label: "1,000 REQ/DÍA", included: true },
  { label: "SOPORTE POR EMAIL", included: true },
  { label: "CIaaS — COMPETITIVE INTEL", included: false },
  { label: "SERVIDOR MCP HOSTEADO", included: false },
];

const GROWTH = [
  { label: "TODO LO DE STARTER", included: true },
  { label: "SERVIDOR MCP (12 TOOLS)", included: true },
  { label: "CHECKOUT UNIFICADO", included: true },
  { label: "HASTA 5 USUARIOS", included: true },
  { label: "10,000 REQ/DÍA", included: true },
  { label: "DATA FEED COMPLETO", included: true },
  { label: "CIaaS — DELTA + ALERTAS", included: true },
  { label: "SOPORTE PRIORITARIO", included: true },
];

const ENTERPRISE = [
  { label: "TODO LO DE GROWTH", included: true },
  { label: "USUARIOS ILIMITADOS", included: true },
  { label: "REQUESTS ILIMITADOS", included: true },
  { label: "SLA 99.5%", included: true },
  { label: "WHITE-LABEL", included: true },
  { label: "WEBHOOKS + STREAMING", included: true },
  { label: "INTEGRACIONES CUSTOM", included: true },
  { label: "SOPORTE DEDICADO 24/7", included: true },
];

export default function Pricing() {
  return (
    <section id="pricing" className="flex flex-col w-full bg-[#060606] py-12 px-4 sm:py-16 sm:px-6 md:py-[80px] md:px-[120px] gap-8 sm:gap-10 md:gap-[48px]">
      <div className="flex flex-col gap-[12px] w-full">
        <span className="font-mono text-[9px] sm:text-[10px] md:text-[11px] font-bold text-[#FFD600] tracking-[2px] md:tracking-[3px] uppercase">Planes</span>
        <h2 className="font-grotesk text-[26px] sm:text-[32px] md:text-[48px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.05] whitespace-pre-line">{"PRECIOS CLAROS.\nPARA CADA ESCALA."}</h2>
        <p className="font-mono text-[10px] sm:text-[11px] md:text-[12px] text-[#666] tracking-[0.5px] leading-[1.6]">Desde developers integrando su primer agente hasta empresas con miles de requests diarios.</p>
      </div>
      <div className="flex flex-col md:flex-row w-full gap-[2px]">
        <PlanCard tier="STARTUP" name="Starter" price="$499/mes"
          description="100 comercios en 12 líneas y 12 países. API REST con búsqueda, comparación y data feed básico. Ideal para integrar agentes de IA."
          btnLabel="Empezar ahora" features={STARTER} accentColor="#555" />
        <PlanCard tier="MÁS POPULAR" tierColor="#0A0A0A" tierBg="#00FF88" tierBorderColor="#00FF88"
          name="Growth" nameColor="#00FF88" price="$1,999/mes"
          description="MCP server hosteado, checkout unificado, CIaaS completo. El plan que usan las agencias y startups de LATAM."
          btnLabel="Agendar demo" btnLabelColor="#0A0A0A" bgColor="#0F0F0F" borderColor="#00FF88" borderWidth={2} btnBg="#00FF88" btnBorderColor="transparent"
          features={GROWTH} accentColor="#00FF88" />
        <PlanCard tier="EMPRESA" tierColor="#FF6B35" tierBorderColor="#FF6B35"
          name="Enterprise" price="Custom"
          description="Requests ilimitados, SLA garantizado, white-label e integraciones a medida. Para organizaciones con escala global."
          btnLabel="Contactar ventas" btnLabelColor="#FF6B35" btnBorderColor="#FF6B35"
          features={ENTERPRISE} accentColor="#FF6B35" />
      </div>
      <p className="font-mono text-[10px] text-[#444] tracking-[2px] text-center">
        PLANES MENSUALES · SIN PERMANENCIA · FREE TIER DISPONIBLE EN API · PRECIOS EN USD
      </p>
    </section>
  );
}
