"use client"
import { useState, useEffect } from "react"
import { useLang } from "@/lib/LanguageContext"

const items = [
  { id: "hero", es: "Inicio", en: "Home" },
  { id: "how", es: "Flujo", en: "Flow" },
  { id: "api", es: "API", en: "API" },
  { id: "coverage", es: "Cobertura", en: "Coverage" },
  { id: "casos", es: "Casos", en: "Use cases" },
  { id: "procure", es: "Procure", en: "Procure" },
  { id: "intelligence", es: "Intelligence", en: "Intelligence" },
  { id: "pricing", es: "Planes", en: "Pricing" },
  { id: "retailers", es: "Retailers", en: "Retailers" },
  { id: "faq", es: "FAQ", en: "FAQ" },
  { id: "contact", es: "Contacto", en: "Contact" },
]

export default function SideNav() {
  const [active, setActive] = useState("hero")
  const [progress, setProgress] = useState(0)
  const { lang, setLang } = useLang()
  const isES = lang === "es"

  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => { entries.forEach(e => { if (e.isIntersecting) setActive(e.target.id) }) },
      { threshold: 0.2 },
    )
    items.forEach(({ id }) => { const el = document.getElementById(id); if (el) obs.observe(el) })

    const onScroll = () => {
      const scrollTop = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      if (docHeight > 0) setProgress(Math.min(scrollTop / docHeight, 1))
    }
    window.addEventListener("scroll", onScroll, { passive: true })
    onScroll()

    return () => {
      obs.disconnect()
      window.removeEventListener("scroll", onScroll)
    }
  }, [])

  const activeIndex = items.findIndex(i => i.id === active)

  return (
    <nav className="fixed left-0 top-0 z-40 h-screen w-12 hidden xl:flex flex-col justify-center bg-[var(--cm-background)]/80 backdrop-blur-sm" aria-label={isES ? "Navegación de secciones" : "Section navigation"}>
      <div className="relative flex flex-col gap-4 px-3">
        {/* Connector line */}
        <div className="absolute left-[calc(0.75rem+2.5px)] top-4 bottom-4 w-px bg-white/10" aria-hidden="true">
          <div
            className="w-full bg-[var(--cm-mint)]/40 transition-all duration-300 ease-out"
            style={{ height: `${Math.max(progress * 100, (activeIndex / (items.length - 1)) * 100)}%` }}
          />
        </div>

        {items.map(({ id, es, en }) => (
          <a key={id} href={`/#${id}`}
            className="touch-compact group relative flex items-center z-10" aria-label={isES ? es : en} title={isES ? es : en}>
            <span className={`h-1.5 w-1.5 rounded-full transition-all duration-300 ${
              active === id ? "bg-[var(--cm-mint)] scale-125 shadow-[0_0_6px_var(--cm-mint)]" : "bg-white/15 group-hover:bg-white/30"}`} />
          </a>
        ))}
        <button onClick={() => setLang(isES ? "en" : "es")} className="mt-4 text-xs font-mono text-[var(--cm-on-surface-variant)] hover:text-white transition-colors z-10">
          {isES ? "EN" : "ES"}
        </button>
      </div>
    </nav>
  )
}
