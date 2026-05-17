"use client";

import { useState, useEffect } from "react";

const links = [
  { label: "COMANDOS",    section: "features"   },
  { label: "ARQUITECTURA", section: "comparison" },
  { label: "CASOS",       section: "showcase"   },
  { label: "FAQ",         section: "faq"        },
  { label: "PRECIOS",     section: "pricing"    },
];

function scrollTo(id: string) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);

  // Body scroll lock when mobile menu is open
  useEffect(() => {
    if (menuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [menuOpen]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const ids = links.map((l) => l.section).filter(Boolean);
    const obs: IntersectionObserver[] = [];

    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      const o = new IntersectionObserver(
        ([entry]) => { if (entry.isIntersecting) setActive(id); },
        { rootMargin: "-35% 0px -60% 0px" }
      );
      o.observe(el);
      obs.push(o);
    });

    return () => obs.forEach((o) => o.disconnect());
  }, []);

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      style={{
        background: scrolled ? "rgba(10,10,10,0.88)" : "transparent",
        backdropFilter: scrolled ? "blur(14px)" : "none",
        WebkitBackdropFilter: scrolled ? "blur(14px)" : "none",
        borderBottom: scrolled ? "1px solid #1E1E1E" : "1px solid transparent",
      }}
    >
      <div className="flex items-center justify-between h-[60px] px-6 md:px-[48px] max-w-[1400px] mx-auto">
        {/* Logo */}
        <a href="#" className="flex items-center gap-[10px] shrink-0 group">
          <span className="font-grotesk text-[13px] font-bold text-[#F5F5F0] tracking-[2.5px]">
            <span className="text-[#00FF88]">$ </span>MARKET
          </span>
        </a>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-[36px]">
          {links.map(({ label, section }) => {
            const isActive = active === section;
            return (
              <button
                key={label}
                onClick={() => scrollTo(section)}
                className="relative font-ibm-mono text-[10px] tracking-[1.5px] transition-colors duration-150 bg-transparent border-none cursor-pointer"
                style={{ color: isActive ? "#00FF88" : "#555" }}
                onMouseEnter={(e) => {
                  if (!isActive) (e.currentTarget as HTMLButtonElement).style.color = "#F5F5F0";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.color = isActive ? "#00FF88" : "#555";
                }}
              >
                {label}
                <span
                  className="absolute left-0 -bottom-[3px] h-[1.5px] bg-[#00FF88] transition-all duration-300"
                  style={{ width: isActive ? "100%" : "0%" }}
                />
              </button>
            );
          })}
        </nav>

        {/* Desktop CTA */}
        <div className="hidden md:flex items-center gap-[14px]">
          <a
            href="https://github.com/Treevu-ai/cli-market-latam"
            className="font-grotesk text-[11px] font-bold text-[#0A0A0A] bg-[#00FF88] tracking-[1.5px] px-[18px] py-[9px] hover:bg-[#00cc6a] transition-colors"
          >
            INSTALAR CLI
          </a>
        </div>

        {/* Mobile burger */}
        <button
          className="md:hidden flex flex-col items-center justify-center gap-[5px] w-[44px] h-[44px] -mr-2"
          onClick={() => setMenuOpen((v) => !v)}
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
        >
          <span
            className="block w-[20px] h-[1.5px] bg-[#F5F5F0] transition-transform duration-200 origin-center"
            style={{ transform: menuOpen ? "translateY(6.5px) rotate(45deg)" : "none" }}
          />
          <span
            className="block w-[20px] h-[1.5px] bg-[#F5F5F0] transition-opacity duration-200"
            style={{ opacity: menuOpen ? 0 : 1 }}
          />
          <span
            className="block w-[20px] h-[1.5px] bg-[#F5F5F0] transition-transform duration-200 origin-center"
            style={{ transform: menuOpen ? "translateY(-6.5px) rotate(-45deg)" : "none" }}
          />
        </button>
      </div>

      {/* Mobile drawer */}
      <div
        className="md:hidden overflow-hidden transition-all duration-300"
        style={{
          maxHeight: menuOpen ? "400px" : "0px",
          background: "rgba(10,10,10,0.97)",
          backdropFilter: "blur(14px)",
          borderBottom: menuOpen ? "1px solid #1E1E1E" : "none",
        }}
      >
        <nav className="flex flex-col px-6 py-5 gap-0">
          {links.map(({ label, section }) => {
            const isActive = active === section;
            return (
              <button
                key={label}
                onClick={() => { scrollTo(section); setMenuOpen(false); }}
                className="flex items-center gap-3 w-full font-ibm-mono text-[13px] tracking-[2px] py-4 border-b border-[#141414] transition-colors bg-transparent border-x-0 border-t-0 cursor-pointer min-h-[48px]"
                style={{ color: isActive ? "#00FF88" : "#666" }}
              >
                <span
                  className="w-[4px] h-[4px] rounded-full shrink-0 transition-colors"
                  style={{ background: isActive ? "#00FF88" : "#2D2D2D" }}
                />
                {label}
              </button>
            );
          })}
          <div className="flex flex-col gap-[10px] pt-5">
            <a
              href="https://github.com/Treevu-ai/cli-market-latam"
              className="font-grotesk text-[11px] font-bold text-[#0A0A0A] bg-[#00FF88] tracking-[1.5px] px-[18px] py-[11px] text-center hover:bg-[#00cc6a] transition-colors"
            >
              INSTALAR CLI
            </a>
          </div>
        </nav>
      </div>
    </header>
  );
}
