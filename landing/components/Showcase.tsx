"use client";

import { useState } from "react";
import SectionHeader from "./SectionHeader";

const slides = [
  {
    tag: "[DEV EXPERIENCE]",
    tagBg: "#00FF88",
    tagColor: "#0A0A0A",
    idx: "01 / 04",
    idxColor: "#444444",
    title: "STARTUP FINTECH\nINTEGRACIÓN EN 2 DÍAS",
    by: "CONECTARON 3 SUPERMERCADOS USANDO EL CLI. MCP FUNCIONANDO EN 48 HORAS CON CLAUDE CODE.",
    border: "#2D2D2D",
    bg: "#111111",
    tagBorder: "",
  },
  {
    tag: "[AGENTE AUTÓNOMO]",
    tagBg: "#111111",
    tagColor: "#00FF88",
    idx: "02 / 04",
    idxColor: "#00FF88",
    title: "AGENCIA DE IA\nCOMPRAS AUTOMATIZADAS",
    by: "AGENTES QUE COMPARAN PRECIOS ENTRE 5 PAÍSES Y EJECUTAN COMPRAS ÓPTIMAS SIN INTERVENCIÓN HUMANA.",
    border: "#00FF88",
    bg: "#0F0F0F",
    tagBorder: "#00FF88",
  },
  {
    tag: "[RETAIL DATA]",
    tagBg: "#1A1A1A",
    tagColor: "#FF6B35",
    idx: "03 / 04",
    idxColor: "#444444",
    title: "CONSULTORA RETAIL\nANÁLISIS DE PRECIOS",
    by: "MONITOREO DIARIO DE 50,000 PRODUCTOS PARA ANÁLISIS COMPETITIVO. DATOS ENRIQUECIDOS CON OPEN FOOD FACTS.",
    border: "#2D2D2D",
    bg: "#0A0A0A",
    tagBorder: "#FF6B35",
  },
  {
    tag: "[E-COMMERCE]",
    tagBg: "#00FF88",
    tagColor: "#0A0A0A",
    idx: "04 / 04",
    idxColor: "#444444",
    title: "MARKETPLACE\nMULTIPAÍS",
    by: "UN MARKETPLACE CONECTÓ 17 COMERCIOS EN 6 LÍNEAS USANDO LA API UNIFICADA. ESCALÓ EN 3 SEMANAS.",
    border: "#2D2D2D",
    bg: "#111111",
    tagBorder: "",
  },
];

export default function Showcase() {
  const [active, setActive] = useState(1);

  const prev = () => setActive((p) => Math.max(0, p - 1));
  const next = () => setActive((p) => Math.min(slides.length - 1, p + 1));

  const slide = slides[active];

  return (
    <section id="showcase" className="flex flex-col w-full bg-[#080808] pt-16 md:pt-[100px] pb-0 gap-8 md:gap-[48px]">
      <div className="flex items-end justify-between px-6 md:px-[120px]">
        <SectionHeader
          label="[06] // CASOS DE USO"
          title={"RESULTADOS\nCOMPROBADOS."}
          titleWidth="w-full max-w-[600px]"
        />
        <div className="flex items-center gap-[8px] shrink-0">
          <button
            onClick={prev}
            className="flex items-center justify-center w-[48px] h-[48px] bg-[#111111] border-2 border-[#3D3D3D] hover:border-[#888888] transition-colors"
          >
            <span className="font-grotesk text-[18px] font-bold text-[#888888]">&lt;</span>
          </button>
          <button
            onClick={next}
            className="flex items-center justify-center w-[48px] h-[48px] bg-[#00FF88] hover:bg-[#00cc6a] transition-colors"
          >
            <span className="font-grotesk text-[18px] font-bold text-[#0A0A0A]">&gt;</span>
          </button>
        </div>
      </div>

      {/* Mobile */}
      <div className="md:hidden px-4 sm:px-6">
        <div
          className="flex flex-col gap-3 sm:gap-4 p-4 sm:p-5 border-2 w-full"
          style={{ backgroundColor: slide.bg, borderColor: slide.border }}
        >
          <div className="flex items-center justify-center h-[80px] sm:h-[120px] bg-[#1A1A1A] border border-[#2D2D2D]">
            <span className="font-ibm-mono text-[9px] sm:text-[10px] text-[#333333] tracking-[1px] sm:tracking-[2px]">[CASO DE USO]</span>
          </div>
          <div className="flex items-center justify-between w-full">
            <div
              className="flex items-center justify-center h-[22px] sm:h-[24px] px-[8px] sm:px-[10px] border"
              style={{ backgroundColor: slide.tagBg, borderColor: slide.tagBorder || "transparent" }}
            >
              <span className="font-ibm-mono text-[8px] sm:text-[9px] font-bold tracking-[0.5px]" style={{ color: slide.tagColor }}>
                {slide.tag}
              </span>
            </div>
            <span className="font-ibm-mono text-[10px] sm:text-[11px] tracking-[1px] sm:tracking-[2px]" style={{ color: slide.idxColor }}>
              {slide.idx}
            </span>
          </div>
          <h3 className="font-grotesk text-[18px] sm:text-[20px] font-bold text-[#F5F5F0] tracking-[0.5px] sm:tracking-[1px] leading-[1.15] whitespace-pre-line">
            {slide.title}
          </h3>
          <p className="font-ibm-mono text-[10px] sm:text-[11px] text-[#555555] tracking-[0.5px] sm:tracking-[1px] leading-[1.5]">{slide.by}</p>
        </div>
      </div>

      {/* Desktop carousel */}
      <div className="hidden md:overflow-hidden h-[416px] md:block px-[120px]">
        <div
          className="flex gap-[2px] transition-transform duration-500 ease-in-out"
          style={{ transform: `translateX(calc(-${active} * (560px + 2px)))` }}
        >
          {slides.map((s, i) => (
            <div
              key={i}
              className="flex flex-col gap-[24px] p-[40px] h-[412px] w-[560px] shrink-0 border-2"
              style={{ backgroundColor: s.bg, borderColor: s.border }}
            >
              <div className="flex items-center justify-center h-[200px] bg-[#1A1A1A] border border-[#2D2D2D]">
                <span className="font-ibm-mono text-[11px] text-[#333333] tracking-[2px]">[CASO DE USO]</span>
              </div>
              <div className="flex items-center justify-between w-full">
                <div
                  className="flex items-center justify-center h-[24px] px-[10px] border"
                  style={{ backgroundColor: s.tagBg, borderColor: s.tagBorder || "transparent" }}
                >
                  <span className="font-ibm-mono text-[9px] font-bold tracking-[1px]" style={{ color: s.tagColor }}>
                    {s.tag}
                  </span>
                </div>
                <span className="font-ibm-mono text-[11px] tracking-[2px]" style={{ color: s.idxColor }}>
                  {s.idx}
                </span>
              </div>
              <h3 className="font-grotesk text-[20px] font-bold text-[#F5F5F0] tracking-[1px] leading-[1.2] whitespace-pre-line">
                {s.title}
              </h3>
              <p className="font-ibm-mono text-[11px] text-[#555555] tracking-[1px]">{s.by}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Dots */}
      <div className="flex items-center gap-[8px] px-6 md:px-[120px]">
        {slides.map((_, i) => (
          <button
            key={i}
            onClick={() => setActive(i)}
            className="h-[4px] transition-all"
            style={{ width: i === active ? 32 : 8, backgroundColor: i === active ? "#00FF88" : "#333333" }}
          />
        ))}
      </div>

      <div className="flex items-center justify-between px-6 md:px-[120px] pb-16 md:pb-[100px]">
        <span className="font-ibm-mono text-[11px] text-[#444444] tracking-[2px]">
          MOSTRANDO 0{active + 1} DE 04 CASOS
        </span>
        <span className="font-ibm-mono text-[11px] text-[#00FF88] tracking-[2px] cursor-pointer hover:underline">
          VER TODOS &gt;
        </span>
      </div>
    </section>
  );
}
