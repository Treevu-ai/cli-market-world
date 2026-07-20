import React from "react";
import { Terminal, Github, Linkedin, Twitter, ArrowUp, Send } from "lucide-react";
import ScrollReveal from "./ScrollReveal";
import ActivateProPanel from "./ActivateProPanel";

export default function Footer() {
  const handleScrollTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <footer className="bg-[#0a0a0a] text-white pt-20 pb-10 relative overflow-hidden border-t border-white/10" id="contacto-footer">
      <div className="absolute top-0 left-1/4 -z-10 h-64 w-64 rounded-full bg-[#bef264]/5 blur-3xl"></div>
      
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Call To Action Banner */}
        <ScrollReveal duration={0.8}>
          <div className="bg-white/5 border border-white/10 rounded-sm p-8 sm:p-12 text-center relative overflow-hidden mb-16">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom,rgba(190,242,100,0.06),transparent_60%)]"></div>
            
            <div className="relative max-w-2xl mx-auto space-y-6">
              <span className="font-mono text-[10px] font-bold text-[#bef264] uppercase tracking-widest bg-[#bef264]/5 border border-[#bef264]/20 px-3 py-1.5 rounded-sm">
                Lidera la góndola
              </span>
              
              <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
                El mercado no espera. ¿Y tú?
              </h2>
              
              <p className="text-xs sm:text-sm text-white/60 leading-relaxed">
                Únete a las empresas líderes que ya están transformando sus datos desordenados de góndola en ventaja competitiva programable en tiempo real.
              </p>

              <div className="pt-4 flex flex-col sm:flex-row justify-center gap-4 items-center">
                <button
                  onClick={() => scrollToSection("chat-section")}
                  className="w-full sm:w-auto inline-flex items-center justify-center rounded-sm bg-[#bef264] px-6 py-3.5 text-xs font-mono font-bold uppercase tracking-widest text-black hover:bg-[#d9f99d] active:scale-95 transition-all cursor-pointer"
                  id="footer-cta-access"
                >
                  <span>Solicitar Acceso Ahora</span>
                  <Send className="ml-2 h-3.5 w-3.5" />
                </button>
                
                {/* Terminal command trigger */}
                <div className="bg-black border border-white/10 px-4 py-2.5 rounded-sm text-left font-mono text-xs text-white/80 max-w-xs overflow-hidden flex items-center space-x-2">
                  <span className="text-[#bef264] select-none">$</span>
                  <span className="text-white/90 select-all font-mono text-[11px]">curl api.climarket.io/v1/pulse</span>
                </div>
              </div>
            </div>
          </div>
        </ScrollReveal>

        {/* Links & Brand grid */}
        <ScrollReveal delay={0.15} duration={0.8}>
          <div className="grid grid-cols-1 md:grid-cols-12 gap-10 border-b border-white/10 pb-12 text-left">
            
            {/* Brand Info */}
            <div className="md:col-span-5 space-y-4">
              <div className="flex items-center space-x-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-sm bg-[#bef264] text-black font-bold font-mono text-xs">
                  CLI
                </div>
                <span className="font-mono text-lg font-bold tracking-tight text-white uppercase">CLI MARKET</span>
              </div>
              
              <p className="text-[11px] sm:text-xs text-white/40 leading-relaxed">
                La primera infraestructura de inteligencia de comercio integrada en tiempo real para Latinoamérica. 
                Normalización algorítmica y resolución de SKU.
              </p>

              {/* Social icons */}
              <div className="flex items-center space-x-3.5 pt-2">
                <a
                  href="https://x.com/cli_market_dev"
                  target="_blank"
                  rel="referrer noopener"
                  className="h-8 w-8 rounded-sm bg-white/5 border border-white/10 flex items-center justify-center text-white/60 hover:text-white hover:bg-white/10 transition-all"
                  title="X (Twitter)"
                >
                  <Twitter className="h-4 w-4" />
                </a>
                <a
                  href="https://www.linkedin.com/company/cli-market/posts/?feedView=all"
                  target="_blank"
                  rel="referrer noopener"
                  className="h-8 w-8 rounded-sm bg-white/5 border border-white/10 flex items-center justify-center text-white/60 hover:text-white hover:bg-white/10 transition-all"
                  title="LinkedIn"
                >
                  <Linkedin className="h-4 w-4" />
                </a>
              </div>
            </div>

            {/* Quick links block 1: Tech */}
            <div className="md:col-span-3 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-widest text-white/40 font-mono">
                Tecnología
              </h4>
              <ul className="space-y-2 text-xs font-mono uppercase text-[10px] tracking-wide">
                <li>
                  <a 
                    href="#tecnologia-section" 
                    onClick={(e) => { e.preventDefault(); scrollToSection("tecnologia-section"); }}
                    className="text-white/50 hover:text-[#bef264] transition-colors"
                  >
                    Resolución de Entidades
                  </a>
                </li>
                <li>
                  <span className="text-white/50 font-mono flex items-center space-x-1.5 cursor-pointer hover:text-[#bef264]">
                    <span>Documentación API</span>
                    <span className="bg-[#bef264]/10 text-[#bef264] text-[8px] font-bold px-1 rounded-sm uppercase tracking-wider border border-[#bef264]/20">v1.2</span>
                  </span>
                </li>
                <li>
                  <span className="text-white/50 cursor-pointer hover:text-[#bef264]">Canasta Procure Copilot</span>
                </li>
              </ul>
            </div>

            {/* Quick links block 2: Company */}
            <div className="md:col-span-4 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-widest text-white/40 font-mono">
                Compañía & Soporte
              </h4>
              <ul className="space-y-2 text-xs font-mono uppercase text-[10px] tracking-wide">
                <li>
                  <a 
                    href="#pricing-section"
                    onClick={(e) => { e.preventDefault(); scrollToSection("pricing-section"); }}
                    className="text-white/50 hover:text-[#bef264] transition-colors"
                  >
                    Modelos de Precios
                  </a>
                </li>
                <li>
                  <span className="text-white/50 cursor-pointer hover:text-[#bef264]">Términos del Servicio</span>
                </li>
                <li>
                  <span className="text-white/50 cursor-pointer hover:text-[#bef264]">Privacidad de Datos</span>
                </li>
                <li>
                  <span className="text-white/50 font-sans tracking-normal normal-case text-xs">Soporte: hello@cli-market.dev</span>
                </li>
              </ul>
            </div>

          </div>
        </ScrollReveal>

        {/* Copy footnote */}
        <ScrollReveal delay={0.3} duration={0.8}>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-between text-[10px] text-white/30 font-mono uppercase tracking-widest gap-4">
            <p>© 2026 CLI Market Intelligence. Todos los derechos reservados.</p>
            
            <button
              onClick={handleScrollTop}
              className="flex items-center space-x-1 text-white/40 hover:text-white transition-colors"
              title="Volver arriba"
            >
              <span>Volver arriba</span>
              <ArrowUp className="h-4 w-4 text-[#bef264]" />
            </button>
          </div>
        </ScrollReveal>

        <ActivateProPanel />

      </div>
    </footer>
  );
}
