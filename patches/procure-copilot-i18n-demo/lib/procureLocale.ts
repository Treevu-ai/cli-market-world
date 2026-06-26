/**
 * Bilingual marketing copy for Procure Copilot landing.
 * Use: const copy = getProcureCopy(lang);
 */
import type { Lang } from "@/lib/i18n";

export type ProcureCopy = {
  hero: {
    badge: string;
    title: { lead: string; mid: string; accent: string };
    subcopy: string;
    primaryCta: { label: string; href: string };
    secondaryCta: { label: string; href: string };
  };
  finalCta: {
    title: string;
    subcopy: string;
    primary: { label: string; href: string };
    secondary: { label: string; href: string };
  };
  bookDemoLabel: string;
  tryDemoLabel: string;
};

import { procureBookDemoHref, procureTryDemoHref } from "@/lib/procureCta";

const TRY = procureTryDemoHref();
const BOOK = procureBookDemoHref();

const ES: ProcureCopy = {
  hero: {
    badge: "40 retailers verificados · 8 países · precios verificados cada 4h",
    title: {
      lead: "Tus compras.",
      mid: "Comparadas, verificadas,",
      accent: "aprobadas.",
    },
    subcopy:
      "Procurement empresarial en LatAm conectado a CLI Market. 4–6 horas/semana en WhatsApp y Excel → comparación automática, data-gate y aprobaciones. desde $29/mes.",
    primaryCta: { label: "Probar demo", href: TRY },
    secondaryCta: { label: "Cómo funciona", href: "#how" },
  },
  finalCta: {
    title: "Empieza a ahorrar en tus compras hoy.",
    subcopy:
      "Demo gratuita del flujo completo · desde $29/mes · 40 retailers verificados · data-gate · aprobaciones",
    primary: { label: "Probar demo", href: TRY },
    secondary: { label: "Agendar demo 15 min", href: BOOK },
  },
  bookDemoLabel: "Agendar demo 15 min",
  tryDemoLabel: "Probar demo",
};

const EN: ProcureCopy = {
  hero: {
    badge: "40 verified retailers · 8 countries · prices refreshed every 4h",
    title: {
      lead: "Your purchases.",
      mid: "Compared, verified,",
      accent: "approved.",
    },
    subcopy:
      "Enterprise procurement in LatAm powered by CLI Market. 4–6 hours/week on WhatsApp and Excel → automated compare, data-gate, and approvals. From $29/mo.",
    primaryCta: { label: "Try demo", href: TRY },
    secondaryCta: { label: "How it works", href: "#how" },
  },
  finalCta: {
    title: "Start saving on procurement today.",
    subcopy:
      "Free full-flow demo · from $29/mo · 40 verified retailers · data-gate · approvals",
    primary: { label: "Try demo", href: TRY },
    secondary: { label: "Book 15-min demo", href: BOOK },
  },
  bookDemoLabel: "Book 15-min demo",
  tryDemoLabel: "Try demo",
};

export function getProcureCopy(lang: Lang): ProcureCopy {
  return lang === "en" ? EN : ES;
}
