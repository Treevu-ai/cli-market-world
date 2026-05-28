"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";

const categories: {
  id: string; label_es: string; label_en: string;
  tools: { n: string; d_es: string; d_en: string }[];
}[] = [
  { id: "shop", label_es: "Búsqueda & Compra", label_en: "Search & Purchase", tools: [
    { n: "market_search", d_es: "Buscar productos en 30 retailers", d_en: "Search products across 30 retailers" },
    { n: "market_compare", d_es: "Comparar precios cross-border", d_en: "Cross-border price comparison" },
    { n: "market_basket", d_es: "Comparar canasta completa entre retailers", d_en: "Compare full basket across retailers" },
    { n: "market_add", d_es: "Agregar productos al carrito", d_en: "Add products to cart" },
    { n: "market_cart", d_es: "Ver y editar el carrito", d_en: "View and edit cart" },
    { n: "market_checkout", d_es: "Completar la compra (Yape, Plin, Wise)", d_en: "Complete purchase (Yape, Plin, Wise)" },
    { n: "market_stock", d_es: "Ver disponibilidad por tienda", d_en: "Check stock per store" },
  ]},
  { id: "intel", label_es: "Inteligencia de Precios", label_en: "Price Intelligence", tools: [
    { n: "market_inflation", d_es: "Tracking de inflación real por producto", d_en: "Real inflation tracking per product" },
    { n: "market_price_history", d_es: "Historial de precios de un SKU", d_en: "SKU price history" },
    { n: "market_trending", d_es: "Productos con mayor movimiento de precio", d_en: "Products with highest price movement" },
    { n: "market_intel", d_es: "Análisis de mercado por línea/país", d_en: "Market analysis by line/country" },
    { n: "market_stats", d_es: "Estadísticas agregadas del data moat", d_en: "Aggregated data moat stats" },
    { n: "market_export", d_es: "Exportar datos históricos (JSON/CSV)", d_en: "Export historical data (JSON/CSV)" },
    { n: "market_scan", d_es: "Escanear nuevas tiendas VTEX", d_en: "Scan new VTEX stores" },
  ]},
  { id: "orders", label_es: "Órdenes & Pagos", label_en: "Orders & Payments", tools: [
    { n: "market_orders", d_es: "Ver historial de órdenes", d_en: "View order history" },
    { n: "market_reorder", d_es: "Reordenar una compra anterior", d_en: "Reorder a previous purchase" },
    { n: "market_ticket", d_es: "Scanear ticket de compra (OCR)", d_en: "Scan receipt (OCR)" },
    { n: "market_exchange", d_es: "Cotizar tipo de cambio en tiempo real", d_en: "Real-time exchange rate quotes" },
  ]},
  { id: "platform", label_es: "Plataforma", label_en: "Platform", tools: [
    { n: "market_login", d_es: "Autenticación", d_en: "Authentication" },
    { n: "market_lines", d_es: "Listar líneas de negocio disponibles", d_en: "List available business lines" },
    { n: "market_countries", d_es: "Listar países con cobertura", d_en: "List countries with coverage" },
    { n: "market_stores", d_es: "Listar 30 retailers verificados", d_en: "List 30 verified retailers" },
    { n: "market_ask", d_es: "Modo agente: lenguaje natural", d_en: "Agent mode: natural language" },
    { n: "market_voice", d_es: "Transcribir búsqueda por voz", d_en: "Voice search transcription" },
    { n: "market_enrich", d_es: "Enriquecer SKU con metadata", d_en: "Enrich SKU with metadata" },
    { n: "market_categories", d_es: "Listar categorías por tienda", d_en: "List categories per store" },
    { n: "market_barcode", d_es: "Buscar por código de barras", d_en: "Search by barcode" },
    { n: "market_whoami", d_es: "Ver perfil y suscripción", d_en: "View profile and subscription" },
    { n: "market_subscription", d_es: "Gestionar plan (Free/Pro/Enterprise)", d_en: "Manage plan (Free/Pro/Enterprise)" },
  ]},
];

export default function Features() {
  const { lang } = useLang();
  const [open, setOpen] = useState<string | null>(null);
  const isES = lang === "es";

  return (
    <section id="features" className="relative bg-[var(--wise-canvas-soft)] py-20 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[var(--wise-body)] font-mono uppercase tracking-[0.15em] mb-8">
          {isES ? "Herramientas" : "Tools"}
        </p>
        <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-3 tracking-tight">
          {isES ? "36 herramientas MCP.\nPara tu agente de IA." : "36 MCP tools.\nFor your AI agent."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-md mx-auto mb-12">
          {isES ? "4 categorías. Haz clic para expandir y ver cada herramienta." : "4 categories. Click to expand and explore each tool."}
        </p>

        <div className="space-y-2">
          {categories.map((cat) => (
            <div key={cat.id} className="text-left">
              <button
                onClick={() => setOpen(open === cat.id ? null : cat.id)}
                className="w-full flex items-center justify-between px-4 py-3 bg-[var(--wise-canvas-soft)] border border-[#c5edab] rounded-lg hover:bg-[var(--wise-green-pale)] transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-[10px] text-[var(--wise-body)] font-mono w-4 text-right">{cat.tools.length}</span>
                  <span className="text-sm font-medium text-[var(--wise-ink)]">{isES ? cat.label_es : cat.label_en}</span>
                </div>
                <svg className={`w-4 h-4 text-[var(--wise-body)] transition-transform ${open === cat.id ? "rotate-180" : ""}`}
                  fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </button>
              {open === cat.id && (
                <div className="mt-1 grid grid-cols-1 sm:grid-cols-2 gap-1 px-1">
                  {cat.tools.map((t) => (
                    <div key={t.n} className="flex flex-col gap-0.5 px-3 py-2">
                      <code className="text-[12px] text-[var(--wise-ink)] font-mono">{t.n}</code>
                      <span className="text-[11px] text-[var(--wise-body)] leading-tight">{isES ? t.d_es : t.d_en}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
