import React, { useState, useEffect } from "react";
import { MessageSquare, Play, Sparkles, Check, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import ScrollReveal from "./ScrollReveal";

export default function Hero() {
  const [step, setStep] = useState(0);

  // Automatically cycle through the simulated WhatsApp chat steps for the dynamic mockup
  useEffect(() => {
    const timers = [
      setTimeout(() => setStep(1), 1000),  // User message appears
      setTimeout(() => setStep(2), 2200),  // Bot "typing..."
      setTimeout(() => setStep(3), 4000),  // Bot reply appears
    ];

    return () => timers.forEach(clearTimeout);
  }, []);

  const handleRestart = () => {
    setStep(0);
    setTimeout(() => setStep(1), 800);
    setTimeout(() => setStep(2), 2000);
    setTimeout(() => setStep(3), 3800);
  };

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <section id="hero-section" className="relative overflow-hidden bg-[#0a0a0a] text-[#f5f5f5] pt-20 pb-24 lg:pt-28 lg:pb-32 terminal-grid">
      {/* Editorial glowing ambient dots */}
      <div className="absolute top-0 right-1/4 -z-10 h-96 w-96 rounded-full bg-[#bef264]/5 blur-3xl"></div>
      <div className="absolute bottom-10 left-10 -z-10 h-80 w-80 rounded-full bg-zinc-800/20 blur-3xl"></div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 items-center gap-16 lg:grid-cols-12">
          
          {/* Copy Column */}
          <div className="lg:col-span-7 flex flex-col justify-center text-left space-y-6">
            
            {/* Tag/Badge */}
            <ScrollReveal delay={0.05} duration={0.6}>
              <div className="inline-flex w-fit items-center space-x-2 border border-[#bef264]/20 bg-[#bef264]/5 px-3 py-1.5 rounded-full">
                <span className="flex h-1.5 w-1.5 rounded-full bg-[#bef264] animate-pulse"></span>
                <span className="font-mono text-[10px] tracking-widest text-[#bef264] uppercase font-bold">INTELLIGENCE EN TIEMPO REAL</span>
              </div>
            </ScrollReveal>

            {/* Title - Large Editorial Header */}
            <ScrollReveal delay={0.15} duration={0.7} distance={20}>
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-5xl xl:text-[68px] leading-[0.9] font-bold tracking-tight">
                Deja de adivinar el mercado. <br/>
                <span className="text-[#bef264] italic font-serif">Domina la góndola en tiempo real.</span>
              </h1>
            </ScrollReveal>

            {/* Subtitle */}
            <ScrollReveal delay={0.25} duration={0.7} distance={20}>
              <p className="text-sm sm:text-base md:text-lg text-white/60 max-w-xl leading-relaxed">
                La primera infraestructura de inteligencia de comercio para LATAM.
                Convertimos el caos de los precios de retail en un activo programable
                para tus equipos de <strong className="text-[#bef264]">Revenue</strong>, <strong className="text-[#bef264]">Growth</strong> y <strong className="text-[#bef264]">Compras</strong>.<span className="terminal-cursor"></span>
              </p>
            </ScrollReveal>

            {/* CTAs */}
            <ScrollReveal delay={0.35} duration={0.7} distance={20}>
              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => scrollToSection("pricing-section")}
                  className="bg-[#bef264] text-black px-8 py-4 font-bold text-xs sm:text-sm uppercase tracking-widest hover:bg-[#c9f67a] active:scale-[0.98] transition-all flex items-center justify-center font-mono cursor-pointer"
                  id="hero-cta-primary"
                >
                  <span>Empezar ahora</span>
                  <ChevronRight className="ml-2 h-4 w-4 stroke-[3]" />
                </button>
                
                <button
                  onClick={() => scrollToSection("chat-section")}
                  className="bg-white/5 border border-white/10 text-white hover:bg-white/10 px-8 py-4 font-bold text-xs sm:text-sm uppercase tracking-widest active:scale-[0.98] transition-all flex items-center justify-center font-mono cursor-pointer"
                  id="hero-cta-secondary"
                >
                  <MessageSquare className="mr-2 h-4.5 w-4.5 text-[#bef264]" />
                  <span>Ver Demo de WhatsApp</span>
                </button>
              </div>
            </ScrollReveal>

            {/* Trust factors */}
            <ScrollReveal delay={0.45} duration={0.8} distance={15}>
              <div className="pt-8 border-t border-white/10">
                <div className="flex flex-wrap items-center gap-x-8 gap-y-4 font-mono text-[11px] tracking-wider text-white/50 uppercase">
                  <div className="flex items-center">
                    <Check className="mr-2 h-4 w-4 text-[#bef264] stroke-[3]" />
                    <span>Sin fricción de APIs</span>
                  </div>
                  <div className="flex items-center">
                    <Check className="mr-2 h-4 w-4 text-[#bef264] stroke-[3]" />
                    <span>Precisión del 99.1%</span>
                  </div>
                  <div className="flex items-center">
                    <Check className="mr-2 h-4 w-4 text-[#bef264] stroke-[3]" />
                    <span>Multipaís (9 Países)</span>
                  </div>
                </div>
              </div>
            </ScrollReveal>

          </div>

          {/* Dynamic Mockup Column (Editorial Dark WhatsApp Sandbox) */}
          <div className="lg:col-span-5 flex justify-center">
            
            <ScrollReveal delay={0.3} duration={0.9} direction="up" distance={40}>
            
            <div className="relative w-full max-w-[340px] rounded-[40px] border-[10px] border-zinc-800 bg-zinc-950 shadow-2xl overflow-hidden aspect-[9/18.5] flex flex-col">
              
              {/* Speaker & Sensor */}
              <div className="absolute top-0 left-1/2 z-30 h-5 w-28 -translate-x-1/2 rounded-b-xl bg-zinc-800 flex items-center justify-center">
                <span className="h-0.5 w-6 rounded bg-zinc-700"></span>
              </div>

              {/* WhatsApp Editorial Dark UI */}
              <div className="h-full w-full bg-zinc-950 flex flex-col relative select-none pt-5">
                
                {/* Header Chat */}
                <div className="bg-zinc-900 text-white pt-4 pb-3 px-3.5 flex items-center space-x-2 shrink-0 border-b border-white/10">
                  <div className="relative h-8 w-8 rounded-full bg-zinc-800 flex items-center justify-center text-[#bef264] font-mono font-bold text-xs border border-white/10">
                    CLI
                    <span className="absolute bottom-0 right-0 h-2 w-2 rounded-full bg-[#bef264]"></span>
                  </div>
                  <div className="flex-1 text-left min-w-0">
                    <div className="text-xs font-bold font-mono tracking-wider text-[#bef264] uppercase">CLI Market Bot</div>
                    <div className="text-[9px] text-white/50 flex items-center font-mono">
                      <span className="h-1.5 w-1.5 rounded-full bg-[#bef264] animate-pulse mr-1.5"></span>
                      En línea • Analista AI
                    </div>
                  </div>
                  
                  {/* Restart simulation button */}
                  <button 
                    onClick={handleRestart}
                    className="rounded-full hover:bg-white/10 p-1.5 text-[#bef264] transition-colors"
                    title="Reiniciar simulación"
                  >
                    <Play className="h-3.5 w-3.5" />
                  </button>
                </div>

                {/* Chat Area */}
                <div className="flex-1 p-3 overflow-y-auto space-y-4 flex flex-col justify-end text-xs pb-4">
                  
                  {/* Security Header */}
                  <div className="mx-auto bg-zinc-900 border border-white/5 text-[9px] text-white/40 px-2.5 py-1 rounded-sm text-center font-mono uppercase tracking-widest">
                    🔒 Conexión cifrada con CLI Server
                  </div>

                  {/* Step 1: User message */}
                  {step >= 1 && (
                    <motion.div 
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      className="self-end max-w-[85%] bg-[#056162]/90 text-white p-3 rounded-lg rounded-tr-none border border-[#056162] text-left relative shadow-lg"
                    >
                      <p className="text-[11px] leading-relaxed">
                        ¿Cuál es la tendencia del precio del café en Lima esta semana?
                      </p>
                      <span className="block text-[8px] text-white/40 text-right mt-1 font-mono">14:52 ✓✓</span>
                    </motion.div>
                  )}

                  {/* Step 2: Bot is typing */}
                  {step === 2 && (
                    <motion.div 
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="self-start bg-zinc-900 text-white/50 border border-white/5 px-3 py-2 rounded-lg rounded-tl-none flex items-center space-x-1.5"
                    >
                      <span className="text-[10px] font-mono italic">Analista procesando góndola</span>
                      <span className="flex space-x-1">
                        <span className="h-1 w-1 rounded-full bg-[#bef264] animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="h-1 w-1 rounded-full bg-[#bef264] animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="h-1 w-1 rounded-full bg-[#bef264] animate-bounce" style={{ animationDelay: '300ms' }}></span>
                      </span>
                    </motion.div>
                  )}

                  {/* Step 3: Bot Response */}
                  {step >= 3 && (
                    <motion.div 
                      initial={{ opacity: 0, y: 12 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ type: "spring", stiffness: 100 }}
                      className="self-start max-w-[95%] bg-[#262d31] text-white/90 p-3 rounded-lg rounded-tl-none border border-white/5 text-left shadow-xl"
                    >
                      <div className="flex items-center justify-between border-b border-white/10 pb-1.5 mb-2">
                        <span className="text-[9px] font-bold text-[#bef264] font-mono uppercase tracking-widest">📊 Reporte de Categoría</span>
                        <span className="bg-[#bef264]/20 text-[#bef264] text-[8px] font-mono px-1 rounded uppercase border border-[#bef264]/30 font-bold">Realtime</span>
                      </div>
                      
                      <p className="text-[10px] text-white/70 mb-2 leading-normal">
                        La categoría <strong className="text-white">Café Soluble</strong> subió un <strong className="text-[#bef264]">4.1%</strong> en promedio. Wong lidera el precio alto.
                      </p>

                      {/* Mock pricing Table inside WhatsApp */}
                      <div className="border border-white/15 rounded-sm overflow-hidden mb-2 bg-black/40 text-[9px] font-mono">
                        <div className="grid grid-cols-3 bg-zinc-800/80 p-1 font-bold text-[#bef264] uppercase tracking-wider">
                          <span>SKU (100g)</span>
                          <span className="text-center">PlazaVea</span>
                          <span className="text-right">Wong</span>
                        </div>
                        <div className="grid grid-cols-3 p-1.5 border-b border-white/5 text-white/80">
                          <span className="truncate">Nescafé Gold</span>
                          <span className="text-center text-[#bef264] font-bold">S/ 23.90</span>
                          <span className="text-right text-red-400">S/ 26.50</span>
                        </div>
                        <div className="grid grid-cols-3 p-1.5 text-white/80">
                          <span className="truncate">Altomayo Org</span>
                          <span className="text-center">S/ 18.50</span>
                          <span className="text-right">S/ 18.50</span>
                        </div>
                      </div>

                      <div className="bg-[#bef264]/10 border-l-2 border-[#bef264] p-1.5 rounded-sm text-[9px] text-[#bef264] leading-tight font-mono">
                        💡 **Gap del 10.8%** en Nescafé Gold. Plaza Vea lidera en competitividad de precio hoy.
                      </div>

                      <span className="block text-[8px] text-white/40 text-right mt-1.5 font-mono">14:52</span>
                    </motion.div>
                  )}

                </div>

                {/* Input Area (Mock) */}
                <div className="p-2 bg-zinc-900 flex items-center space-x-1.5 border-t border-white/10 shrink-0">
                  <div className="flex-1 bg-white/5 border border-white/10 rounded-full py-1.5 px-3 flex items-center text-left">
                    <span className="text-[10px] text-white/30">Tu analista en WhatsApp...</span>
                  </div>
                  <div className="h-7 w-7 rounded-full bg-[#bef264] text-black flex items-center justify-center">
                    <MessageSquare className="h-3.5 w-3.5" />
                  </div>
                </div>

              </div>
            </div>

            {/* Float Badge */}
            <div className="absolute -bottom-4 right-1/2 translate-x-1/2 lg:translate-x-0 lg:right-4 bg-zinc-900 border border-white/10 shadow-2xl rounded-sm p-4 flex items-center space-x-3 max-w-[240px]">
              <div className="h-9 w-9 rounded-sm bg-white/5 flex items-center justify-center text-[#bef264] border border-white/10 shrink-0">
                <Sparkles className="h-5 w-5" />
              </div>
              <div className="text-left">
                <div className="text-xs font-bold text-white font-mono uppercase tracking-wider">Demo Interactiva</div>
                <div className="text-[10px] text-white/50">Prueba interactiva abajo 👇</div>
              </div>
            </div>

            </ScrollReveal>

          </div>

        </div>
      </div>
    </section>
  );
}
