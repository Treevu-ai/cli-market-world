export type Lang = "es" | "en";
export type Dict = Record<string, string>;

const es: Dict = {
  nav_coverage: "Cobertura", nav_how: "Flujo", nav_terminal: "Terminal", nav_features: "Capacidades",
  nav_pricing: "Precios", nav_faq: "FAQ", nav_agents: "Agentes", nav_cases: "Casos",
  hero_eye: "Infraestructura de comercio para agentes de IA",
  hero_h1a: "3,760+ retailers.", hero_h1b: "Una sola API.", hero_h1c_p: "Tus agentes pueden", hero_h1c_s: "solos.",
  hero_sub: "Conectamos agentes de IA con 3,760+ comercios VTEX en 67 países.",
  hero_install: "Instalar CLI", hero_cov: "Ver cobertura", hero_contact: "Contactar",
  hero_words: "comprar,comparar,buscar,analizar",
  stats_label: "Escala", stats_title: "3,760 retailers.\nUn solo conector.", stats_sub: "Cada retailer es una linea de JSON. Todos comparten la misma API. Infraestructura invisible.",
  terminal_label: "Terminal", terminal_title: "Una terminal.\n3,760 comercios.",
  how_label: "Flujo", how_title: "6 comandos.\nDel install a la compra.",
  how_subtitle: "Del install al checkout en menos de un minuto. Sin interfaz. Sin navegador.",
  how_footer: "INSTALL → SEARCH → COMPARE → CHECKOUT · TODO EN LA TERMINAL",
  features_label: "Capacidades", features_title: "12 herramientas.\nUn ecosistema.",
  agent_label: "AI-to-AI Communication Protocol", agent_title: "Infraestructura para Agentes",
  usecases_label: "Casos de uso", usecases_title: "Para quien construye.",
  lines_label: "[COBERTURA] // 3,760 COMERCIOS · 12 LÍNEAS · 67 PAÍSES",
  lines_title: "3,760 retailers.\n67 países. 12 líneas.",
  pricing_label: "Precios", pricing_title: "Empieza gratis.\nEscala cuando quieras.",
  faq_title: "Preguntas frecuentes.",
  cta_title: "Tu agente puede comprar solo.\nHoy.",
};
const en: Dict = {
  nav_coverage: "Coverage", nav_how: "Flow", nav_terminal: "Terminal", nav_features: "Capabilities",
  nav_pricing: "Pricing", nav_faq: "FAQ", nav_agents: "Agents", nav_cases: "Use Cases",
  hero_eye: "Commerce infrastructure for AI agents",
  hero_h1a: "3,760+ retailers.", hero_h1b: "One single API.", hero_h1c_p: "Your agents can", hero_h1c_s: "on their own.",
  hero_sub: "We connect AI agents to 3,760+ VTEX retailers across 67 countries.",
  hero_install: "Install CLI", hero_cov: "Coverage", hero_contact: "Contact",
  hero_words: "purchase,compare,search,analyze",
  stats_label: "Scale", stats_title: "3,760 retailers.\nOne connector.", stats_sub: "Each retailer is one line of JSON. All share the same public API. Invisible infrastructure.",
  terminal_label: "Terminal", terminal_title: "One terminal.\n3,760 stores.",
  how_label: "Flow", how_title: "6 commands.\nFrom install to purchase.",
  how_subtitle: "From install to checkout in under a minute. No UI. No browser.",
  how_footer: "INSTALL → SEARCH → COMPARE → CHECKOUT · ALL IN THE TERMINAL",
  features_label: "Capabilities", features_title: "12 tools.\nOne ecosystem.",
  agent_label: "AI-to-AI Communication Protocol", agent_title: "Infrastructure for Agents",
  usecases_label: "Use Cases", usecases_title: "For builders.",
  lines_label: "[COVERAGE] // 3,760 STORES · 12 LINES · 67 COUNTRIES",
  lines_title: "3,760 retailers.\n67 countries. 12 lines.",
  pricing_label: "Pricing", pricing_title: "Start free.\nScale when ready.",
  faq_title: "Frequently asked questions.",
  cta_title: "Your agent can buy on its own.\nToday.",
};

const dicts: Record<Lang, Dict> = { es, en };
export function getDict(lang: Lang): Dict { return dicts[lang] || es; }
export function t(lang: Lang, key: string): string { return dicts[lang]?.[key] || es[key] || key; }
