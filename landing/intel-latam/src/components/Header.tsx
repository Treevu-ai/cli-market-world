import React, { useState, useEffect } from "react";
import { Terminal, ChevronDown, Activity, ShieldCheck, Zap, Menu, X } from "lucide-react";
import { RoleTabId } from "../types";

interface HeaderProps {
  onSelectRole: (role: RoleTabId) => void;
}

export default function Header({ onSelectRole }: HeaderProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const hero = document.getElementById("hero-section");
      if (hero) {
        const rect = hero.getBoundingClientRect();
        // Activated when the bottom of the hero section is at or above the header height (64px)
        setIsScrolled(rect.bottom <= 64);
      } else {
        // Fallback fallback if the element isn't found
        setIsScrolled(window.scrollY > 300);
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleRoleClick = (role: RoleTabId) => {
    onSelectRole(role);
    setIsDropdownOpen(false);
    setIsMobileMenuOpen(false);
    const element = document.getElementById("soluciones-section");
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  const scrollToSection = (id: string) => {
    setIsMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <header className={`sticky top-0 z-50 w-full transition-all duration-300 text-[#f5f5f5] ${
      isScrolled 
        ? "border-b border-white/10 bg-[#0a0a0a]/90 backdrop-blur-md" 
        : "border-b border-transparent bg-transparent"
    }`}>
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        
        {/* Logo - Editorial Terminal Style */}
        <div 
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} 
          className="flex cursor-pointer items-center gap-2"
          id="nav-logo"
        >
          <div className="bg-[#bef264] text-black font-mono font-bold px-2 py-1 text-xs sm:text-sm tracking-tighter">
            CLI_MARKET
          </div>
          <span className="hidden sm:inline-block text-[10px] font-mono uppercase tracking-[0.2em] opacity-60 ml-1">
            Intelligence Infrastructure
          </span>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-8 text-[11px] uppercase tracking-widest font-mono">
          
          {/* Solutions Dropdown Menu */}
          <div 
            className="relative"
            onMouseEnter={() => setIsDropdownOpen(true)}
            onMouseLeave={() => setIsDropdownOpen(false)}
          >
            <button 
              className="flex items-center space-x-1 font-medium text-white/70 hover:text-[#bef264] transition-colors py-2"
              id="solutions-dropdown-btn"
            >
              <span>Soluciones</span>
              <ChevronDown className={`h-3 w-3 transition-transform duration-200 ${isDropdownOpen ? "rotate-180" : ""}`} />
            </button>

            {isDropdownOpen && (
              <div className="absolute left-0 mt-0 w-64 rounded-sm border border-white/10 bg-[#121212] p-2 shadow-2xl animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="px-3 py-2 text-[9px] font-semibold text-white/40 uppercase tracking-wider font-mono border-b border-white/5 mb-1">
                  Segmentado por Rol
                </div>
                
                <button
                  onClick={() => handleRoleClick("revenue")}
                  className="flex w-full items-start space-x-3 rounded-sm p-2.5 text-left hover:bg-white/5 transition-colors group"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] group-hover:bg-[#bef264] group-hover:text-black transition-colors">
                    <Activity className="h-4.5 w-4.5" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white group-hover:text-[#bef264]">Revenue & Growth</div>
                    <div className="text-[10px] text-white/50">Ajustes dinámicos de precio y gaps</div>
                  </div>
                </button>

                <button
                  onClick={() => handleRoleClick("procurement")}
                  className="flex w-full items-start space-x-3 rounded-sm p-2.5 text-left hover:bg-white/5 transition-colors group"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-sm bg-white/5 text-sky-400 group-hover:bg-sky-400 group-hover:text-black transition-colors">
                    <ShieldCheck className="h-4.5 w-4.5" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white group-hover:text-sky-400">Procurement & Ops</div>
                    <div className="text-[10px] text-white/50">Procure Copilot y canastas optimizadas</div>
                  </div>
                </button>

                <button
                  onClick={() => handleRoleClick("innovation")}
                  className="flex w-full items-start space-x-3 rounded-sm p-2.5 text-left hover:bg-white/5 transition-colors group"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-sm bg-white/5 text-purple-400 group-hover:bg-purple-400 group-hover:text-black transition-colors">
                    <Zap className="h-4.5 w-4.5" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white group-hover:text-purple-400">Innovación & Producto</div>
                    <div className="text-[10px] text-white/50">Sizing de SKUs y elasticidad de góndola</div>
                  </div>
                </button>
              </div>
            )}
          </div>

          <button 
            onClick={() => scrollToSection("tecnologia-section")}
            className="font-medium text-white/70 hover:text-[#bef264] transition-colors"
          >
            Tecnología
          </button>
          
          <button 
            onClick={() => scrollToSection("pricing-section")}
            className="font-medium text-white/70 hover:text-[#bef264] transition-colors"
          >
            Precios
          </button>
        </nav>

        {/* CTA and Mobile Menu Button */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => scrollToSection("chat-section")}
            className="hidden sm:inline-flex items-center justify-center border border-[#bef264] text-[#bef264] px-4 py-2 text-[10px] uppercase tracking-widest font-mono font-bold hover:bg-[#bef264] hover:text-black transition-colors"
            id="header-cta-btn"
          >
            Probar Demo Gratis
          </button>

          {/* Mobile Menu Icon */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="inline-flex md:hidden h-10 w-10 items-center justify-center rounded-sm text-white/70 hover:bg-white/5 focus:outline-none"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-white/10 bg-[#0a0a0a] px-4 py-4 space-y-4 animate-in slide-in-from-top-5 duration-200">
          <div className="space-y-1">
            <div className="px-3 py-1 text-[9px] font-semibold text-white/40 uppercase tracking-wider font-mono">
              Soluciones por Rol
            </div>
            <button
              onClick={() => handleRoleClick("revenue")}
              className="flex w-full items-center space-x-3 rounded-sm px-3 py-2.5 text-left text-xs font-mono uppercase tracking-widest text-white/80 hover:bg-white/5"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-[#bef264]"></span>
              <span>Revenue & Growth</span>
            </button>
            <button
              onClick={() => handleRoleClick("procurement")}
              className="flex w-full items-center space-x-3 rounded-sm px-3 py-2.5 text-left text-xs font-mono uppercase tracking-widest text-white/80 hover:bg-white/5"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-sky-400"></span>
              <span>Procurement & Ops</span>
            </button>
            <button
              onClick={() => handleRoleClick("innovation")}
              className="flex w-full items-center space-x-3 rounded-sm px-3 py-2.5 text-left text-xs font-mono uppercase tracking-widest text-white/80 hover:bg-white/5"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-purple-400"></span>
              <span>Innovación & Producto</span>
            </button>
          </div>

          <hr className="border-white/10" />

          <div className="space-y-1">
            <button
              onClick={() => scrollToSection("tecnologia-section")}
              className="flex w-full items-center rounded-sm px-3 py-2 text-left text-xs font-mono uppercase tracking-widest text-white/80 hover:bg-white/5"
            >
              Tecnología (Secret Sauce)
            </button>
            <button
              onClick={() => scrollToSection("pricing-section")}
              className="flex w-full items-center rounded-sm px-3 py-2 text-left text-xs font-mono uppercase tracking-widest text-white/80 hover:bg-white/5"
            >
              Precios
            </button>
          </div>

          <button
            onClick={() => scrollToSection("chat-section")}
            className="flex w-full items-center justify-center border border-[#bef264] text-[#bef264] py-3 text-xs uppercase tracking-widest font-mono font-bold hover:bg-[#bef264] hover:text-black transition-colors"
          >
            Probar Demo Gratis
          </button>
        </div>
      )}
    </header>
  );
}
