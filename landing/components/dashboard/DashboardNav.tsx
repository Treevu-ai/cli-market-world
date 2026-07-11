"use client";

import { usePathname } from "next/navigation";
import { useLang } from "@/lib/LanguageContext";
import { useApiKey } from "@/lib/useApiKey";

/** Small nav for the authenticated /dashboard/* console — deliberately
 *  separate from lib/siteNav.ts's TOP_NAV (dashboard pages were removed
 *  from the marketing nav on 2026-07-10, kept decoupled). */
const DASHBOARD_NAV = [
  { id: "explorer", es: "Explorer", en: "Explorer", href: "/dashboard/explorer" },
  { id: "pricing", es: "Pricing", en: "Pricing", href: "/dashboard/pricing" },
  { id: "household", es: "Hogar", en: "Household", href: "/dashboard/household" },
  { id: "developer", es: "Developer", en: "Developer", href: "/dashboard/developer" },
];

export default function DashboardNav() {
  const { lang } = useLang();
  const isES = lang === "es";
  const pathname = usePathname();
  const { clearApiKey } = useApiKey();

  return (
    <nav className="border-b border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]">
      <div className="landing-container flex items-center justify-between py-2 overflow-x-auto">
        <div className="flex items-center gap-1">
          {DASHBOARD_NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <a
                key={item.id}
                href={item.href}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono whitespace-nowrap transition-colors ${
                  active
                    ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)]"
                    : "text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-on-surface)]"
                }`}
              >
                {isES ? item.es : item.en}
              </a>
            );
          })}
        </div>
        <button
          type="button"
          onClick={clearApiKey}
          className="px-3 py-1.5 rounded-lg text-xs font-mono text-[var(--cm-on-surface-variant)] hover:text-red-400 transition-colors shrink-0"
        >
          {isES ? "Salir" : "Log out"}
        </button>
      </div>
    </nav>
  );
}
