"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";

const categories = [
  { id: "shop", label: "Búsqueda & Compra", tools: [
    { n: "market_search", d: "Buscar productos en 60 retailers" },
    { n: "market_compare", d: "Comparar precios cross-border" },
    { n: "market_basket", d: "Comparar canasta completa entre retailers" },
    { n: "market_add", d: "Agregar productos al carrito" },
    { n: "market_cart", d: "Ver y editar el carrito" },
    { n: "market_checkout", d: "Completar la compra (Yape, Plin, Wise)" },
    { n: "market_stock", d: "Ver disponibilidad por tienda" },
  ]},
  { id: "intel", label: "Inteligencia de Precios", tools: [
    { n: "market_inflation", d: "Tracking de inflación real por producto" },
    { n: "market_price_history", d: "Historial de precios de un SKU" },
    { n: "market_trending", d: "Productos con mayor movimiento de precio" },
    { n: "market_intel", d: "Análisis de mercado por línea/país" },
    { n: "market_stats", d: "Estadísticas agregadas del data moat" },
    { n: "market_export", d: "Exportar datos históricos (JSON/CSV)" },
    { n: "market_scan", d: "Escanear nuevas tiendas VTEX" },
  ]},
  { id: "orders", label: "Órdenes & Pagos", tools: [
    { n: "market_orders", d: "Ver historial de órdenes" },
    { n: "market_reorder", d: "Reordenar una compra anterior" },
    { n: "market_ticket", d: "Scanear ticket de compra (OCR)" },
    { n: "market_exchange", d: "Cotizar tipo de cambio en tiempo real" },
  ]},
  { id: "platform", label: "Plataforma", tools: [
    { n: "market_login", d: "Autenticación" },
    { n: "market_lines", d: "Listar líneas de negocio disponibles" },
    { n: "market_countries", d: "Listar países con cobertura" },
    { n: "market_stores", d: "Listar 60 retailers verificados" },
    { n: "market_ask", d: "Modo agente: lenguaje natural" },
    { n: "market_voice", d: "Transcribir búsqueda por voz" },
    { n: "market_enrich", d: "Enriquecer SKU con metadata" },
    { n: "market_categories", d: "Listar categorías por tienda" },
    { n: "market_barcode", d: "Buscar por código de barras" },
    { n: "market_whoami", d: "Ver perfil y suscripción" },
    { n: "market_subscription", d: "Gestionar plan (Free/Pro/Enterprise)" },
  ]},
];

export default function Features() {
  const { lang } = useLang();
  const [open, setOpen] = useState<string | null>(null);
  const isES = lang === "es";

  return (
    <section id="features" className="relative bg-white py-20 border-t border-[#e5e5e5]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#a3a3a3] font-mono uppercase tracking-[0.15em] mb-8">
          {isES ? "Herramientas" : "Tools"}
        </p>
        <h2 className="text-[24px] font-medium text-black mb-3 tracking-tight">
          {isES ? "36 herramientas MCP.\nPara tu agente de IA." : "36 MCP tools.\nFor your AI agent."}
        </h2>
        <p className="text-sm text-[#a3a3a3] max-w-md mx-auto mb-12">
          {isES ? "4 categorías. Haz clic para expandir y ver cada herramienta." : "4 categories. Click to expand and explore each tool."}
        </p>

        <div className="space-y-2">
          {categories.map((cat) => (
            <div key={cat.id} className="text-left">
              <button
                onClick={() => setOpen(open === cat.id ? null : cat.id)}
                className="w-full flex items-center justify-between px-4 py-3 bg-white border border-[#e5e5e5] rounded-lg hover:bg-[#fafafa] transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-[10px] text-[#a3a3a3] font-mono w-4 text-right">{cat.tools.length}</span>
                  <span className="text-sm font-medium text-black">{cat.label}</span>
                </div>
                <svg
                  className={`w-4 h-4 text-[#a3a3a3] transition-transform ${open === cat.id ? "rotate-180" : ""}`}
                  fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"
                >
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </button>
              {open === cat.id && (
                <div className="mt-1 grid grid-cols-1 sm:grid-cols-2 gap-1 px-1">
                  {cat.tools.map((t) => (
                    <div key={t.n} className="flex flex-col gap-0.5 px-3 py-2">
                      <code className="text-[12px] text-black font-mono">{t.n}</code>
                      <span className="text-[11px] text-[#a3a3a3] leading-tight">{t.d}</span>
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
