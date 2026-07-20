import React from "react";
import { EyeOff, Shuffle, Clock, FileSpreadsheet, ArrowRight, Ban } from "lucide-react";
import ScrollReveal from "./ScrollReveal";

export default function PainSection() {
  return (
    <section className="bg-[#0a0a0a] py-20 lg:py-28 border-y border-white/10" id="dolores-section">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Header container */}
        <ScrollReveal duration={0.8}>
          <div className="mx-auto max-w-3xl text-center">
            <div className="inline-flex items-center space-x-1.5 border border-[#bef264]/20 bg-[#bef264]/5 px-3 py-1 text-[10px] font-bold text-[#bef264] mb-4 uppercase tracking-widest font-mono rounded-sm">
              <Ban className="h-3.5 w-3.5" />
              <span>La Realidad del Retail</span>
            </div>
            
            <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl font-sans">
              ¿Sigues gestionando tu estrategia de precios en un Excel?
            </h2>
            
            <p className="mt-4 text-sm sm:text-base md:text-lg text-white/60 leading-relaxed">
              En una economía informal y acelerada como la de LATAM, la información tradicional llega tarde. 
              Para cuando el reporte de precios llega a tu mesa, el mercado ya cambió. Estás operando con puntos ciegos.
            </p>
          </div>
        </ScrollReveal>

        {/* The Pain Grid (3 Columns) */}
        <div className="mt-16 grid grid-cols-1 gap-8 md:grid-cols-3">
          
          {/* Card 1: Ceguera */}
          <ScrollReveal delay={0.05} duration={0.8} className="h-full">
            <div className="group relative rounded-sm border border-white/10 bg-white/5 p-8 hover:bg-white/10 hover:border-[#bef264]/30 transition-all duration-300 h-full flex flex-col justify-between">
              <div>
                <div className="flex h-12 w-12 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 group-hover:bg-[#bef264] group-hover:text-black transition-colors">
                  <EyeOff className="h-5 w-5" />
                </div>
                
                <h3 className="mt-6 text-lg font-bold text-white font-sans">
                  Ceguera de Mercado
                </h3>
                
                <p className="mt-3 text-xs sm:text-sm text-white/60 leading-relaxed">
                  "No sé exactamente qué hace mi competencia hoy, solo lo que hicieron hace un mes." Estás reaccionando a datos históricos en lugar de influir activamente en el mercado.
                </p>
              </div>
              
              {/* Old stat indicator */}
              <div className="mt-6 border-t border-white/10 pt-4 flex items-center justify-between font-mono text-[10px] tracking-widest text-white/40">
                <span>FRECUENCIA TRADICIONAL</span>
                <span className="font-bold text-[#bef264]">Cada 30-45 días</span>
              </div>
            </div>
          </ScrollReveal>

          {/* Card 2: Fricción */}
          <ScrollReveal delay={0.15} duration={0.8} className="h-full">
            <div className="group relative rounded-sm border border-white/10 bg-white/5 p-8 hover:bg-white/10 hover:border-[#bef264]/30 transition-all duration-300 h-full flex flex-col justify-between">
              <div>
                <div className="flex h-12 w-12 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 group-hover:bg-[#bef264] group-hover:text-black transition-colors">
                  <Shuffle className="h-5 w-5" />
                </div>
                
                <h3 className="mt-6 text-lg font-bold text-white font-sans">
                  Fricción de Datos
                </h3>
                
                <p className="mt-3 text-xs sm:text-sm text-white/60 leading-relaxed">
                  "Tardo horas limpiando nombres de productos y convirtiendo unidades para poder comparar." El 80% de tu tiempo se pierde en homologar SKUs en vez de planificar la estrategia comercial.
                </p>
              </div>
              
              {/* Old stat indicator */}
              <div className="mt-6 border-t border-white/10 pt-4 flex items-center justify-between font-mono text-[10px] tracking-widest text-white/40">
                <span>ESFUERZO DE LIMPIEZA</span>
                <span className="font-bold text-[#bef264]">80% Operativo</span>
              </div>
            </div>
          </ScrollReveal>

          {/* Card 3: Lentitud */}
          <ScrollReveal delay={0.25} duration={0.8} className="h-full">
            <div className="group relative rounded-sm border border-white/10 bg-white/5 p-8 hover:bg-white/10 hover:border-[#bef264]/30 transition-all duration-300 h-full flex flex-col justify-between">
              <div>
                <div className="flex h-12 w-12 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 group-hover:bg-[#bef264] group-hover:text-black transition-colors">
                  <Clock className="h-5 w-5" />
                </div>
                
                <h3 className="mt-6 text-lg font-bold text-white font-sans">
                  Lentitud de Respuesta
                </h3>
                
                <p className="mt-3 text-xs sm:text-sm text-white/60 leading-relaxed">
                  "Tomo decisiones basadas en intuiciones porque la data real es accesible o costosa." El margen comercial se erosiona silenciosamente frente a competidores ágiles que detectan promociones antes.
                </p>
              </div>
              
              {/* Old stat indicator */}
              <div className="mt-6 border-t border-white/10 pt-4 flex items-center justify-between font-mono text-[10px] tracking-widest text-white/40">
                <span>MÉTODO DE DECISIÓN</span>
                <span className="font-bold text-[#bef264]">Intuición / Reactiva</span>
              </div>
            </div>
          </ScrollReveal>

        </div>

        {/* Excel vs Programable Comparison Box */}
        <ScrollReveal delay={0.1} duration={0.9} distance={40}>
          <div className="mt-16 rounded-sm border border-white/10 bg-white/5 p-6 sm:p-10 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 h-40 w-40 bg-[#bef264]/5 blur-3xl rounded-full"></div>
            
            <div className="grid grid-cols-1 items-center gap-8 lg:grid-cols-2 relative">
              
              {/* Left Box side */}
              <div className="text-left space-y-4">
                <div className="flex items-center space-x-2 text-[#bef264] font-mono text-[10px] font-bold uppercase tracking-widest">
                  <FileSpreadsheet className="h-4 w-4" />
                  <span>La Gran Diferencia</span>
                </div>
                <h4 className="text-xl sm:text-2xl font-bold leading-tight">
                  Pasa de la descripción reactiva a la promesa ejecutiva.
                </h4>
                <p className="text-white/60 text-xs sm:text-sm leading-relaxed">
                  Mapear precios no sirve de nada si se hace en silos. Con CLI Market, toda la góndola de LATAM 
                  está normalizada y fluye directamente por WhatsApp o API en un modelo inteligente estructurado.
                </p>
              </div>

              {/* Right Comparison column */}
              <div className="space-y-4">
                <div className="flex items-center space-x-3 rounded-sm bg-black/40 p-4 border border-white/10">
                  <div className="flex h-8 w-8 items-center justify-center rounded-sm bg-white/5 text-white/50 border border-white/10 font-mono text-[10px] font-bold shrink-0">EX</div>
                  <div className="flex-1 text-left">
                    <div className="text-xs font-bold text-white/80">El Proceso Tradicional (Excel)</div>
                    <div className="text-[10px] text-white/40">Web scrapers frágiles • Hojas rotas • Homologación manual interminable</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-center text-white/30">
                  <ArrowRight className="h-5 w-5 rotate-90 lg:rotate-0" />
                </div>

                <div className="flex items-center space-x-3 rounded-sm bg-[#bef264]/5 p-4 border border-[#bef264]/20">
                  <div className="flex h-8 w-8 items-center justify-center rounded-sm bg-[#bef264]/10 text-[#bef264] border border-[#bef264]/20 font-mono text-[10px] font-bold shrink-0">CLI</div>
                  <div className="flex-1 text-left">
                    <div className="text-xs font-bold text-[#bef264]">La Plataforma Inteligente CLI Market</div>
                    <div className="text-[10px] text-white/70">Resolución de SKU algorítmica • Refresco de 4H • WhatsApp conversacional</div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </ScrollReveal>

      </div>
    </section>
  );
}
