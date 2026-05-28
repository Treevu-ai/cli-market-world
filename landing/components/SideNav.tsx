"use client"
import { useState, useEffect } from "react"
import { useLang } from "@/lib/LanguageContext"

const items = [
  { id: "hero", es: "Inicio", en: "Home" },
  { id: "stats", es: "Escala", en: "Scale" },
  { id: "terminal", es: "Terminal", en: "Terminal" },
  { id: "retailers", es: "Retailers", en: "Retailers" },
  { id: "coverage", es: "Cobertura", en: "Coverage" },
  { id: "pricing", es: "Planes", en: "Pricing" },
  { id: "faq", es: "FAQ", en: "FAQ" },
]

export default function SideNav() {
  const [active, setActive] = useState("hero")
  const { lang, setLang } = useLang()
  const isES = lang === "es"

  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => { entries.forEach(e => { if (e.isIntersecting) setActive(e.target.id) }) },
      { threshold: 0.2 },
    )
    items.forEach(({ id }) => { const el = document.getElementById(id); if (el) obs.observe(el) })
    return () => obs.disconnect()
  }, [])

  return (
    <nav className="fixed left-0 top-0 z-50 h-screen w-12 hidden md:flex flex-col justify-center bg-background/80 backdrop-blur-sm">
      <div className="flex flex-col gap-4 px-3">
        {items.map(({ id, es, en }) => (
          <button key={id} onClick={() => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" })}
            className="group relative flex items-center" aria-label={isES ? es : en}>
            <span className={`h-1.5 w-1.5 rounded-full transition-all duration-300 ${
              active === id ? "bg-[var(--wise-green)] scale-125" : "bg-white/20 group-hover:bg-white/50"}`} />
            <span className={`absolute left-6 font-mono text-[9px] uppercase tracking-widest opacity-0 group-hover:opacity-100 group-hover:left-7 transition-all duration-200 whitespace-nowrap ${
              active === id ? "text-[var(--wise-green)]" : "text-white/40"}`}>
              {isES ? es : en}
            </span>
          </button>
        ))}
        <button onClick={() => setLang(isES ? "en" : "es")} className="mt-4 text-[8px] font-mono text-white/20 hover:text-white/40 transition-colors">
          {isES ? "EN" : "ES"}
        </button>
      </div>
    </nav>
  )
}
