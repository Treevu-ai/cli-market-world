"use client";

import { useLang } from "@/lib/LanguageContext";

const ITEMS_ES = [
  "⚡ Mastercard Agent Pay live en LATAM — Mar 2026",
  "📈 805% de crecimiento de tráfico AI · Black Friday 2025",
  "$67B en ventas influenciadas por AI · Cyber Week 2025 — Salesforce",
  "22 herramientas MCP · claude.ai · ChatGPT · Cursor",
  "38% mayor conversión de compradores vía AI vs. búsqueda tradicional — MetaRouter",
  "El 25% del gasto online pasará por agentes de IA en 2030 — Morgan Stanley",
  "Visa Trusted Agent Protocol · LATAM rollout 2026",
];

const ITEMS_EN = [
  "⚡ Mastercard Agent Pay live in LATAM — Mar 2026",
  "📈 805% AI traffic growth · Black Friday 2025",
  "$67B in AI-influenced sales · Cyber Week 2025 — Salesforce",
  "22 MCP tools · claude.ai · ChatGPT · Cursor",
  "38% higher conversion from AI shoppers vs. traditional search — MetaRouter",
  "25% of online spend through AI agents by 2030 — Morgan Stanley",
  "Visa Trusted Agent Protocol · LATAM rollout 2026",
];

export default function AgenticWaveBand() {
  const { lang } = useLang();
  const isES = lang === "es";
  const items = isES ? ITEMS_ES : ITEMS_EN;
  const track = [...items, ...items];

  return (
    <div
      className="price-ticker brand-mode-terminal"
      role="region"
      aria-label={
        isES
          ? "El momentum del comercio agentivo en LATAM"
          : "Agentic commerce momentum in LATAM"
      }
    >
      <div className="price-ticker-track" style={{ animationDuration: "55s" }}>
        {track.map((item, i) => (
          <span key={i} className="price-ticker-item">
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}
