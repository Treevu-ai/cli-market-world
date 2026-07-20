import React, { useState, useEffect } from "react";
import { Cpu, RotateCcw, Database, Shield, Zap, CheckCircle2 } from "lucide-react";
import { motion } from "motion/react";
import ScrollReveal from "./ScrollReveal";

export default function SecretSauce() {
  const [activeStep, setActiveStep] = useState(0);

  // Cycle through the SKU resolution demonstration stages
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 4);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="bg-[#0a0a0a] text-[#f5f5f5] py-20 lg:py-28 relative overflow-hidden border-b border-white/10 terminal-grid" id="tecnologia-section">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 -z-10 h-full w-full max-w-7xl bg-radial-gradient from-[#bef264]/5 via-transparent to-transparent opacity-50 pointer-events-none"></div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Header Block */}
        <ScrollReveal duration={0.8}>
          <div className="mx-auto max-w-3xl text-center">
            <div className="inline-flex items-center space-x-1.5 border border-[#bef264]/20 bg-[#bef264]/5 px-3 py-1 text-[10px] font-bold text-[#bef264] mb-4 uppercase tracking-widest font-mono rounded-sm">
              <Cpu className="h-3.5 w-3.5" />
              <span>Infraestructura de Datos</span>
            </div>
            
            <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              No somos un agregador. Somos un Motor de Resolución de Entidades.
            </h2>
            
            <p className="mt-4 text-sm sm:text-base md:text-lg text-white/60 leading-relaxed font-sans">
              "Mientras otros raspan la web, nosotros construimos la verdad del mercado." 
              Normalizamos cada SKU, cada peso y cada unidad (kg/L) para que tú solo te preocupes por la estrategia, no por la limpieza de la data.
            </p>
          </div>
        </ScrollReveal>

        {/* Dynamic SKU Resolution Visualizer Widget */}
        <ScrollReveal delay={0.15} duration={0.8} distance={40}>
          <div className="mt-16 bg-white/5 rounded-sm border border-white/10 p-6 sm:p-8 max-w-4xl mx-auto shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-6">
              <div className="flex items-center space-x-2">
                <span className="flex h-2 w-2 rounded-full bg-[#bef264] animate-pulse"></span>
                <span className="font-mono text-[10px] text-white/50 font-bold uppercase tracking-widest">Demostración: SKU Resolver Engine</span>
              </div>
              <button 
                onClick={() => setActiveStep(0)}
                className="text-white/40 hover:text-[#bef264] transition-colors rounded-sm p-1.5 border border-white/10 hover:border-[#bef264]/30"
                title="Reiniciar flujo"
              >
                <RotateCcw className="h-3.5 w-3.5" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
              
              {/* Input Messy SKUs Column (Left) */}
              <div className="md:col-span-5 space-y-3">
                <div className="text-[10px] font-mono text-white/40 text-left uppercase tracking-widest mb-2 font-bold">Precios Sucios en Góndola (Scraped Data)</div>
                
                <div className={`p-3 rounded-sm border text-left transition-all duration-300 ${activeStep >= 1 ? "border-[#bef264] bg-[#bef264]/5" : "border-white/10 bg-black/40 text-white/30"}`}>
                  <div className="text-[9px] font-mono text-white/40 font-bold">PLAZA VEA</div>
                  <div className="font-mono text-xs font-semibold text-white/90 mt-0.5">Gloria Evap. 400g</div>
                  <div className="text-[10px] font-mono text-[#bef264] mt-1 font-bold">S/ 4.20</div>
                </div>

                <div className={`p-3 rounded-sm border text-left transition-all duration-300 ${activeStep >= 2 ? "border-[#bef264] bg-[#bef264]/5" : "border-white/10 bg-black/40 text-white/30"}`}>
                  <div className="text-[9px] font-mono text-white/40 font-bold">WONG</div>
                  <div className="font-mono text-xs font-semibold text-white/90 mt-0.5">LECHE EVAP GLORIA AZUL 400 GR</div>
                  <div className="text-[10px] font-mono text-[#bef264] mt-1 font-bold">S/ 4.30</div>
                </div>

                <div className={`p-3 rounded-sm border text-left transition-all duration-300 ${activeStep >= 3 ? "border-[#bef264] bg-[#bef264]/5" : "border-white/10 bg-black/40 text-white/30"}`}>
                  <div className="text-[9px] font-mono text-white/40 font-bold">TOTTUS</div>
                  <div className="font-mono text-xs font-semibold text-white/90 mt-0.5">Glra. Evap. Az. x400g</div>
                  <div className="text-[10px] font-mono text-[#bef264] mt-1 font-bold">S/ 3.90</div>
                </div>
              </div>

              {/* Processing Engine central indicator */}
              <div className="md:col-span-2 flex flex-col items-center justify-center py-4">
                <div className="h-10 w-10 rounded-sm bg-zinc-900 border border-white/10 text-[#bef264] flex items-center justify-center shadow-lg relative">
                  <Database className="h-5 w-5 animate-pulse text-[#bef264]" />
                  <div className="absolute inset-0 rounded-sm bg-[#bef264]/5 animate-ping -z-10"></div>
                </div>
                <div className="h-8 w-[1px] bg-gradient-to-b from-[#bef264]/50 to-transparent my-2 hidden md:block"></div>
                <span className="font-mono text-[9px] text-white/40 font-bold uppercase tracking-widest text-center mt-2">Resolviendo Entidades</span>
              </div>

              {/* Resolved Golden Record Column (Right) */}
              <div className="md:col-span-5 flex flex-col justify-center">
                <div className="text-[10px] font-mono text-white/40 text-left uppercase tracking-widest mb-2 font-bold">Registro de Oro Unificado (Golden Record)</div>
                
                <div className={`rounded-sm border p-5 text-left transition-all duration-500 ${activeStep === 0 ? "border-white/5 bg-black/40 opacity-40" : "border-[#bef264]/40 bg-[#bef264]/5 shadow-lg shadow-[#bef264]/5"}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1.5">
                      <CheckCircle2 className="h-4.5 w-4.5 text-[#bef264] shrink-0" />
                      <span className="font-mono text-[9px] font-bold text-[#bef264] uppercase tracking-widest">Normalizado</span>
                    </div>
                    <span className="font-mono text-[9px] text-white/30">ID: SKU-GLOR-EVA400</span>
                  </div>

                  <h4 className="font-sans text-base font-bold text-white mt-3">
                    Leche Evaporada Gloria Azul 400g
                  </h4>

                  <div className="mt-4 space-y-2 text-[11px] font-mono border-t border-white/10 pt-3 text-white/50">
                    <div className="flex justify-between">
                      <span>Categoría:</span>
                      <span className="text-white font-bold font-sans">Lácteos & Derivados</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Unidad de Medida:</span>
                      <span className="text-white font-bold">400 GR (0.4 kg)</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Precio Promedio Lima:</span>
                      <span className="text-[#bef264] font-bold">S/ 4.13 PEN</span>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </ScrollReveal>

        {/* KPIs Grid (Contadores rápidos) */}
        <div className="mt-20 grid grid-cols-2 gap-6 sm:gap-8 lg:grid-cols-4">
          
          {/* KPI 1 */}
          <ScrollReveal delay={0.05} duration={0.8} className="w-full">
            <div className="bg-white/5 border border-white/10 p-6 rounded-sm text-center hover:border-[#bef264]/30 transition-colors h-full flex flex-col justify-center">
              <div className="font-mono text-3xl sm:text-4xl font-extrabold text-[#bef264]">
                82
              </div>
              <div className="mt-2 text-xs sm:text-sm font-semibold text-white font-sans">
                Retailers Configurados (37 Verificados)
              </div>
              <div className="mt-1 text-[9px] text-white/40 font-mono uppercase tracking-wider">
                Supermercados & Discounters
              </div>
            </div>
          </ScrollReveal>

          {/* KPI 2 */}
          <ScrollReveal delay={0.15} duration={0.8} className="w-full">
            <div className="bg-white/5 border border-white/10 p-6 rounded-sm text-center hover:border-[#bef264]/30 transition-colors h-full flex flex-col justify-center">
              <div className="font-mono text-3xl sm:text-4xl font-extrabold text-[#bef264]">
                70k+
              </div>
              <div className="mt-2 text-xs sm:text-sm font-semibold text-white font-sans">
                Golden Records
              </div>
              <div className="mt-1 text-[9px] text-white/40 font-mono uppercase tracking-wider">
                Productos Normalizados
              </div>
            </div>
          </ScrollReveal>

          {/* KPI 3 */}
          <ScrollReveal delay={0.25} duration={0.8} className="w-full">
            <div className="bg-white/5 border border-white/10 p-6 rounded-sm text-center hover:border-[#bef264]/30 transition-colors h-full flex flex-col justify-center">
              <div className="font-mono text-3xl sm:text-4xl font-extrabold text-[#bef264]">
                4 Horas
              </div>
              <div className="mt-2 text-xs sm:text-sm font-semibold text-white font-sans">
                Refresco de Datos
              </div>
              <div className="mt-1 text-[9px] text-white/40 font-mono uppercase tracking-wider">
                Frecuencia líder regional
              </div>
            </div>
          </ScrollReveal>

          {/* KPI 4 */}
          <ScrollReveal delay={0.35} duration={0.8} className="w-full">
            <div className="bg-white/5 border border-white/10 p-6 rounded-sm text-center hover:border-[#bef264]/30 transition-colors h-full flex flex-col justify-center">
              <div className="font-mono text-3xl sm:text-4xl font-extrabold text-[#bef264]">
                9 Países
              </div>
              <div className="mt-2 text-xs sm:text-sm font-semibold text-white font-sans">
                Cobertura Regional
              </div>
              <div className="mt-1 text-[9px] text-white/40 font-mono uppercase tracking-wider">
                México, Perú, Colombia, etc.
              </div>
            </div>
          </ScrollReveal>

        </div>

      </div>
    </section>
  );
}
