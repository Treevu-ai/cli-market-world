export type Lang = "es" | "en";
export type Dict = Record<string, string>;

const es: Dict = {
  nav_coverage: "Cobertura", nav_how: "Flujo", nav_cli: "Terminal", nav_features: "Comandos",
  nav_pricing: "Precios", nav_faq: "FAQ", nav_agents: "Agentes", nav_cases: "Casos",
  hero_eye: "Infraestructura de comercio para agentes de IA",
  hero_h1a: "3,600+ retailers.", hero_h1b: "Una sola API.", hero_h1c_p: "Tus agentes pueden", hero_h1c_s: "solos.",
  hero_sub: "Conectamos agentes de IA con 3,600+ comercios VTEX en 67 países.",
  hero_install: "Instalar CLI", hero_cov: "Ver cobertura", hero_contact: "Contactar",
  hero_words: "comprar,comparar,buscar,analizar",
  stats_label: "Escala", stats_title: "El ecosistema\nVTEX completo.", stats_sub: "Infraestructura invisible.",
  terminal_label: "Terminal", terminal_title: "Una CLI. Miles de comercios.",
  how_label: "Flujo", how_title: "6 comandos.\nCompra completa.",
  features_label: "Comandos", features_title: "Una CLI.\n3,600+ comercios.",
  agent_label: "AI-to-AI Communication Protocol", agent_title: "Infraestructura para Agentes",
  usecases_label: "Casos de uso", usecases_title: "Para quien construye.",
  lines_label: "[COBERTURA] // 3,600+ COMERCIOS · 12 LÍNEAS · 67 PAÍSES",
  lines_title: "UN CONECTOR.\nCOBERTURA REAL.",
  pricing_label: "Precios", pricing_title: "Free tier\npara empezar.",
  faq_title: "Preguntas frecuentes.",
  cta_title: "¿Listo para empezar?",
};
const en: Dict = {
  nav_coverage: "Coverage", nav_how: "Flow", nav_cli: "Terminal", nav_features: "Commands",
  nav_pricing: "Pricing", nav_faq: "FAQ", nav_agents: "Agents", nav_cases: "Use Cases",
  hero_eye: "Commerce infrastructure for AI agents",
  hero_h1a: "3,600+ retailers.", hero_h1b: "One single API.", hero_h1c_p: "Your agents can", hero_h1c_s: "on their own.",
  hero_sub: "We connect AI agents to 3,600+ VTEX retailers across 67 countries.",
  hero_install: "Install CLI", hero_cov: "Coverage", hero_contact: "Contact",
  hero_words: "purchase,compare,search,analyze",
  stats_label: "Scale", stats_title: "The complete\nVTEX ecosystem.", stats_sub: "Invisible infrastructure.",
  terminal_label: "Terminal", terminal_title: "One CLI. Thousands of stores.",
  how_label: "Flow", how_title: "6 commands.\nComplete purchase.",
  features_label: "Commands", features_title: "One CLI.\n3,600+ stores.",
  agent_label: "AI-to-AI Communication Protocol", agent_title: "Infrastructure for Agents",
  usecases_label: "Use Cases", usecases_title: "For builders.",
  lines_label: "[COVERAGE] // 3,600+ STORES · 12 LINES · 67 COUNTRIES",
  lines_title: "ONE CONNECTOR.\nREAL COVERAGE.",
  pricing_label: "Pricing", pricing_title: "Free tier\nto start.",
  faq_title: "Frequently asked questions.",
  cta_title: "Ready to start?",
};

const dicts: Record<Lang, Dict> = { es, en };
export function getDict(lang: Lang): Dict { return dicts[lang] || es; }
export function t(lang: Lang, key: string): string { return dicts[lang]?.[key] || es[key] || key; }
