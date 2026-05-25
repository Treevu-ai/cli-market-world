"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";

interface Tool {
  n: string; d_es: string; d_en: string;
  demo_es: string; demo_en: string;
  c: string;
}
interface Category {
  id: string; label_es: string; label_en: string; color: string; tools: Tool[];
}

const categories: Category[] = [
  {
    id: "shop", label_es: "Shop", label_en: "Shop", color: "#3cffd0",
    tools: [
      { n: "market_login",   d_es: "Autentica al agente para operar", d_en: "Authenticate the agent session", demo_es: "market login\n→ Token guardado en ~/.market/session.json", demo_en: "market login\n→ Token stored in ~/.market/session.json", c: "#3cffd0" },
      { n: "market_search",  d_es: "Busca en 30 retailers VTEX", d_en: "Search across 30 VTEX retailers", demo_es: 'market search "leche" --country PE\n→ 1. Leche Gloria 400ml Wong S/3.50\n→ 2. Leche Ideal 395g Metro S/3.20', demo_en: 'market search "milk" --country AR\n→ 1. Milk 1L Carrefour ARS 1,200\n→ 2. Milk 1L Jumbo ARS 1,150', c: "#FFD600" },
      { n: "market_compare", d_es: "Compara precios entre países", d_en: "Cross-country price comparison", demo_es: 'market compare "aceite"\n→ Primor 1L: S/8.90 Wong\n→ Natura 900ml: ARS 1,250 Carrefour AR', demo_en: 'market compare "oil"\n→ Oil 1L: PEN 8.90 Wong\n→ Oil 1L: ARS 1,250 Carrefour AR', c: "#4ADE80" },
      { n: "market_add",     d_es: "Agrega al carrito", d_en: "Add to cart", demo_es: "market add 3 --qty 2\n→ Agregado: 2x Leche Gloria 400ml", demo_en: "market add 3 --qty 2\n→ Added: 2x Milk 1L", c: "#FF6B35" },
      { n: "market_cart",    d_es: "Ver carrito actual", d_en: "View current cart", demo_es: "market cart\n→ 1. 2x Leche S/3.50\n→ Total: S/11.20", demo_en: "market cart\n→ 1. 2x Milk ARS 1,200\n→ Total: ARS 3,380", c: "#FF6B35" },
      { n: "market_checkout", d_es: "Completa la compra", d_en: "Complete purchase", demo_es: "market checkout --payment yape\n→ Pedido ORD-004 confirmado", demo_en: "market checkout --payment card\n→ Order ORD-004 confirmed", c: "#60A5FA" },
      { n: "market_ask",     d_es: "Compra en lenguaje natural", d_en: "Natural language purchase", demo_es: 'market ask "compra 2 leche y 1 arroz al mejor precio"\n→ Mejor: Wong S/11.20', demo_en: 'market ask "buy 2 milk and 1 rice best price"\n→ Best: Wong S/11.20', c: "#FB923C" },
    ],
  },
  {
    id: "orders", label_es: "Orders", label_en: "Orders", color: "#A78BFA",
    tools: [
      { n: "market_cart_update", d_es: "Cambia cantidades", d_en: "Update quantities", demo_es: "market cart-update <id> 5\n→ Cantidad actualizada a 5", demo_en: "market cart-update <id> 5\n→ Quantity updated to 5", c: "#A78BFA" },
      { n: "market_cart_remove", d_es: "Elimina del carrito", d_en: "Remove from cart", demo_es: "market cart-remove <id>\n→ Producto eliminado", demo_en: "market cart-remove <id>\n→ Item removed", c: "#A78BFA" },
      { n: "market_orders",  d_es: "Historial de órdenes", d_en: "Order history", demo_es: "market orders\n→ ORD-001 S/15.50 Yape\n→ ORD-002 S/8.90 Plin", demo_en: "market orders\n→ ORD-001 ARS 5,200 Card\n→ ORD-002 ARS 3,100 Card", c: "#A78BFA" },
      { n: "market_reorder", d_es: "Repite orden anterior", d_en: "Repeat previous order", demo_es: "market reorder ORD-001\n→ Restaurada al carrito", demo_en: "market reorder ORD-001\n→ Restored to cart", c: "#A78BFA" },
      { n: "market_basket",  d_es: "Compara canasta entre tiendas", d_en: "Compare basket across stores", demo_es: "market basket leche:2 arroz:1 --country AR\n→ Carrefour: ARS 3,380\n→ Jumbo: ARS 3,150 ← MEJOR", demo_en: "market basket milk:2 rice:1 --country AR\n→ Carrefour: ARS 3,380\n→ Jumbo: ARS 3,150 ← BEST", c: "#F472B6" },
    ],
  },
  {
    id: "intel", label_es: "Intel", label_en: "Intel", color: "#FFD600",
    tools: [
      { n: "market_inflation", d_es: "Inflación desde el data moat", d_en: "Inflation from data moat", demo_es: "market inflation --country AR\n→ Promedio: +2.3%\n→ 127 productos rastreados", demo_en: "market inflation --country AR\n→ Avg: +2.3%\n→ 127 products tracked", c: "#38BDF8" },
      { n: "market_price_history", d_es: "Historial de precios", d_en: "Price history", demo_es: "market_price_history product_id=123\n→ 50 snapshots · min S/3.20 · max S/4.10", demo_en: "market_price_history product_id=123\n→ 50 snapshots · min 3.20 · max 4.10", c: "#38BDF8" },
      { n: "market_stats",  d_es: "Estadísticas del data moat", d_en: "Data moat statistics", demo_es: "market_stats\n→ 4,439 precios · 30 tiendas activas", demo_en: "market_stats\n→ 4,439 prices · 30 active stores", c: "#38BDF8" },
      { n: "market_alerts",  d_es: "Alertas de bajada de precio", d_en: "Price drop alerts", demo_es: 'market_alerts product="leche" threshold=5\n→ 3 productos bajaron >5%', demo_en: 'market_alerts product="milk" threshold=5\n→ 3 products dropped >5%', c: "#F472B6" },
      { n: "market_trending", d_es: "Productos con más movimiento", d_en: "Trending products", demo_es: "market_trending --country PE\n→ Top 10 productos con mayor delta", demo_en: "market_trending --country AR\n→ Top 10 products by movement", c: "#F472B6" },
      { n: "market_barcode", d_es: "Busca por código de barras", d_en: "Barcode lookup", demo_es: "market_barcode 7750182000017\n→ Leche Gloria 400ml", demo_en: "market_barcode 7750182000017\n→ Milk 1L", c: "#34D399" },
      { n: "market_enrich",  d_es: "Enriquece con Open Food Facts", d_en: "Enrich with Open Food Facts", demo_es: 'market_enrich "leche"\n→ Nutriscore: A · Calorías: 62kcal', demo_en: 'market_enrich "milk"\n→ Nutriscore: A · Calories: 62kcal', c: "#34D399" },
    ],
  },
  {
    id: "platform", label_es: "Platform", label_en: "Platform", color: "#FF6B35",
    tools: [
      { n: "market_lines",   d_es: "6 líneas con sus retailers", d_en: "6 business lines", demo_es: "market lines\n→ supermercados (14) · electro (9) · farmacias (4) · moda (2)", demo_en: "market lines\n→ supermarkets (14) · electronics (9) · pharmacies (4) · fashion (2)", c: "#3cffd0" },
      { n: "market_stores",  d_es: "30 retailers verificados", d_en: "30 verified retailers", demo_es: "market_stores\n→ Wong 🇵🇪 · Carrefour 🇦🇷 · Motorola 🇧🇷 ...", demo_en: "market_stores\n→ Wong 🇵🇪 · Carrefour 🇦🇷 · Motorola 🇧🇷 ...", c: "#3cffd0" },
      { n: "market_countries", d_es: "8 países con cobertura", d_en: "8 countries covered", demo_es: "market_countries\n→ AR (8) · BR (7) · PE (4) · CO (3) ...", demo_en: "market_countries\n→ AR (8) · BR (7) · PE (4) · CO (3) ...", c: "#3cffd0" },
      { n: "market_categories", d_es: "Árbol de categorías VTEX", d_en: "VTEX category tree", demo_es: "market_categories wong\n→ Alimentos\n  Lácteos\n  Panadería", demo_en: "market_categories carrefour\n→ Food\n  Dairy\n  Bakery", c: "#34D399" },
      { n: "market_ticket",  d_es: "Escanea ticket de compra", d_en: "Scan purchase receipt", demo_es: "market_ticket url=<imagen>\n→ OCR: Leche Gloria 400ml S/3.50", demo_en: "market_ticket url=<image>\n→ OCR: Milk 1L 3.50", c: "#60A5FA" },
      { n: "market_voice",   d_es: "Transcribe audio a texto", d_en: "Transcribe voice to text", demo_es: "market_voice url=<audio>\n→ \"compra leche y arroz\"", demo_en: "market_voice url=<audio>\n→ \"buy milk and rice\"", c: "#60A5FA" },
      { n: "market_export",  d_es: "Exporta data moat (JSON/CSV)", d_en: "Export data moat (JSON/CSV)", demo_es: "market_export --country PE --format csv\n→ 100 registros exportados", demo_en: "market_export --country AR --format csv\n→ 100 records exported", c: "#FF6B35" },
      { n: "market_scan",    d_es: "Escanea nuevas tiendas VTEX", d_en: "Scan new VTEX stores", demo_es: "market_scan --line farmacias\n→ 4 tiendas verificadas", demo_en: "market_scan --line pharmacies\n→ 4 stores verified", c: "#FF6B35" },
      { n: "market_whoami",  d_es: "Verifica identidad y tier", d_en: "Verify identity and tier", demo_es: "market_whoami\n→ admin · tier: free · 1 API key", demo_en: "market_whoami\n→ admin · tier: free · 1 API key", c: "#FB923C" },
      { n: "market_subscription", d_es: "Consulta plan de suscripción", d_en: "View subscription plan", demo_es: "market_subscription\n→ Free · 60 req/min · 1,000 req/día", demo_en: "market_subscription\n→ Free · 60 req/min · 1,000 req/day", c: "#FB923C" },
      { n: "market_preferences", d_es: "Preferencias de compra", d_en: "Shopping preferences", demo_es: "market_preferences\n→ Tienda fav: Wong · Total gastado: S/45.30", demo_en: "market_preferences\n→ Fav store: Wong · Total spent: 45.30", c: "#FB923C" },
    ],
  },
];

export default function Features() {
  const { t: _t, lang } = useLang();
  const [openCat, setOpenCat] = useState<string | null>(null);
  const [activeTool, setActiveTool] = useState<string | null>(null);

  return (
    <section id="features" className="relative flex flex-col w-full bg-[#131313] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#3cffd0]/40"/>{_t("features_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">
          {lang === "es" ? "30 herramientas.\nUn ecosistema." : "30 tools.\nOne ecosystem."}
        </h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">
          {lang === "es" ? "4 categorías. Clickeá para expandir y ver cada tool." : "4 categories. Click to expand and explore each tool."}
        </p>
      </div>

      <div className="flex flex-col gap-3 max-w-[1100px]">
        {categories.map((cat) => {
          const isOpen = openCat === cat.id;
          return (
            <div key={cat.id}>
              <button
                onClick={() => { setOpenCat(isOpen ? null : cat.id); setActiveTool(null); }}
                className="w-full flex items-center gap-3 px-4 py-3 bg-[#131313] border text-left transition-all cursor-pointer"
                style={{ borderColor: isOpen ? cat.color : "#2d2d2d", background: isOpen ? `${cat.color}06` : "#131313" }}
              >
                <span className="w-2 h-2 rounded-full shrink-0" style={{ background: cat.color }} />
                <span className="text-sm font-mono font-bold text-white/80">{lang === "es" ? cat.label_es : cat.label_en}</span>
                <span className="text-[10px] font-mono text-[#555] ml-2">({cat.tools.length} tools)</span>
                <span className="ml-auto text-xs font-mono" style={{ color: isOpen ? cat.color : "#444" }}>{isOpen ? "−" : "+"}</span>
              </button>
              {isOpen && (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-1.5 mt-1.5">
                  {cat.tools.map((t) => {
                    const isActive = activeTool === t.n;
                    return (
                      <div key={t.n}>
                        <button
                          onClick={() => setActiveTool(isActive ? null : t.n)}
                          className="w-full text-left bg-[#0c0c0c] border p-2.5 flex flex-col gap-1 transition-all cursor-pointer"
                          style={{ borderColor: isActive ? t.c : "#1f1f1f", background: isActive ? `${t.c}08` : "#0c0c0c" }}
                        >
                          <div className="flex items-center gap-1.5">
                            <span className="w-1 h-1 rounded-full shrink-0" style={{ background: t.c }} />
                            <span className="text-[9px] font-mono font-bold text-white/70 truncate">{t.n}</span>
                          </div>
                          <p className="text-[8px] font-mono text-[#555] leading-relaxed">{lang === "es" ? t.d_es : t.d_en}</p>
                        </button>
                        {isActive && (
                          <div className="bg-[#080808] border border-t-0 px-2.5 py-2.5 font-mono text-[8px] leading-relaxed whitespace-pre-wrap" style={{ borderColor: `${t.c}30` }}>
                            <span className="text-[#777]">{lang === "es" ? t.demo_es : t.demo_en}</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <p className="text-white/20 font-mono text-[10px] uppercase tracking-widest max-w-[800px]">MCP NATIVO · API REST · JSON PARSEABLE · CROSS-BORDER · DATA FEED · CHECKOUT LOCAL</p>
      <p className="text-white/10 font-mono text-[9px]">{_t("features_live")}</p>
    </section>
  );
}
