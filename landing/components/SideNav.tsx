"use client";

import { useLang } from "@/lib/LanguageContext";
import { SIDE_NAV } from "@/lib/siteNav";
import { useActiveSection } from "@/hooks/useActiveSection";

export default function SideNav() {
  const { active, activeIndex, progress, storyAct } = useActiveSection();
  const { lang, setLang } = useLang();
  const isES = lang === "es";

  return (
    <nav
      className="fixed left-0 top-0 z-40 h-screen w-12 hidden xl:flex flex-col justify-center bg-white/80 backdrop-blur-sm"
      aria-label={isES ? "Navegación de secciones" : "Section navigation"}
    >
      <div className="relative flex flex-col gap-4 px-3">
        <div className="absolute left-[calc(0.75rem+2.5px)] top-4 bottom-4 w-px bg-gray-200" aria-hidden="true">
          <div
            className="w-full bg-[var(--cm-mint)]/40 transition-all duration-300 ease-out"
            style={{
              height: `${Math.max(progress * 100, (activeIndex / Math.max(SIDE_NAV.length - 1, 1)) * 100)}%`,
            }}
          />
        </div>

        {SIDE_NAV.map(({ id, es, en }) => (
          <a
            key={id}
            href={`/#${id}`}
            className="touch-compact group relative flex flex-col items-center z-10"
            aria-label={isES ? es : en}
            title={isES ? es : en}
            aria-current={active === id ? "true" : undefined}
          >
            {id === "story" && active === "story" ? (
              <span className="flex flex-col gap-0.5 mb-0.5" aria-hidden="true">
                {[0, 1, 2, 3].map((i) => (
                  <span
                    key={i}
                    className={`block h-0.5 w-0.5 rounded-full transition-colors ${
                      i === storyAct ? "bg-[var(--cm-mint)] scale-150" : "bg-gray-300"
                    }`}
                  />
                ))}
              </span>
            ) : null}
            <span
              className={`h-1.5 w-1.5 rounded-full transition-all duration-300 ${
                active === id
                  ? "bg-[var(--cm-mint)] scale-125 shadow-[0_0_6px_var(--cm-mint)]"
                  : "bg-gray-300 group-hover:bg-gray-400"
              }`}
            />
          </a>
        ))}
        <button
          onClick={() => setLang(isES ? "en" : "es")}
          className="mt-4 text-xs font-mono text-[var(--cm-on-surface-variant)] hover:text-gray-900 transition-colors z-10"
        >
          {isES ? "EN" : "ES"}
        </button>
      </div>
    </nav>
  );
}
