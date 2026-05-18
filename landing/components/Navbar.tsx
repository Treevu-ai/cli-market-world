"use client";
import { useState, useEffect } from "react";

const links = [
  { label: "Cobertura", section: "coverage" },
  { label: "Comandos",  section: "features" },
  { label: "FAQ",       section: "faq"      },
];

function scrollTo(id: string) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [menuOpen]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => { for (const e of entries) { if (e.isIntersecting && e.target.id) setActive(e.target.id); } },
      { threshold: 0.3 }
    );
    links.forEach((l) => { const el = document.getElementById(l.section); if (el) obs.observe(el); });
    return () => obs.disconnect();
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? "bg-[#0A0A0A]/90 backdrop-blur-md border-b border-[#1A1A1A]" : "bg-transparent"}`}>
      <div className="flex items-center justify-between h-[52px] px-6 md:px-28">
        <a href="#hero" className="font-mono text-[13px] tracking-[0.2em] text-[#F5F5F0] hover:text-[#00FF88] transition-colors">CLI MARKET</a>
        <div className="hidden md:flex items-center gap-8">
          {links.map((l) => (
            <button key={l.section} onClick={() => scrollTo(l.section)}
              className={`font-mono text-[11px] uppercase tracking-[0.15em] transition-colors ${active === l.section ? "text-[#F5F5F0]" : "text-[#555] hover:text-[#888]"}`}>
              {l.label}
            </button>
          ))}
          <a href="https://github.com/Treevu-ai/cli-market-latam"
            className="font-mono text-[10px] uppercase tracking-[0.15em] text-[#AAA] border border-[#333] px-4 py-1.5 hover:border-[#00FF88] hover:text-[#00FF88] transition-all">
            Instalar
          </a>
        </div>
        <button className="md:hidden font-mono text-[11px] text-[#888]" onClick={() => setMenuOpen(!menuOpen)}>
          {menuOpen ? "Cerrar" : "Menú"}
        </button>
      </div>
      {menuOpen && (
        <div className="md:hidden bg-[#0A0A0A] border-t border-[#1A1A1A] px-6 py-6 flex flex-col gap-5">
          {links.map((l) => (
            <button key={l.section} onClick={() => { scrollTo(l.section); setMenuOpen(false); }}
              className="font-mono text-[12px] uppercase tracking-[0.15em] text-[#888] text-left">{l.label}</button>
          ))}
          <a href="https://github.com/Treevu-ai/cli-market-latam"
            className="font-mono text-[11px] text-[#00FF88] border border-[#00FF88]/30 px-4 py-2 text-center mt-2">Instalar CLI</a>
        </div>
      )}
    </nav>
  );
}
