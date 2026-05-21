"use client";
import { useLang } from "@/lib/LanguageContext";

const tools = [
  { n: "market_login",       d_es: "Autentica al agente para operar",       d_en: "Authenticate the agent session",       c: "#00FF88" },
  { n: "market_lines",       d_es: "Lista las 4 líneas con sus retailers",  d_en: "List 4 business lines with retailers",  c: "#00FF88" },
  { n: "market_search",      d_es: "Busca productos en 27 retailers",       d_en: "Search products across 27 retailers",   c: "#FFD600" },
  { n: "market_compare",     d_es: "Compara precios entre países",           d_en: "Cross-country price comparison",         c: "#4ADE80" },
  { n: "market_add",         d_es: "Agrega productos al carrito",           d_en: "Add products to cart",                  c: "#FF6B35" },
  { n: "market_cart",        d_es: "Muestra el carrito actual",              d_en: "View current cart",                     c: "#FF6B35" },
  { n: "market_cart_update", d_es: "Cambia cantidades en el carrito",       d_en: "Update cart quantities",                c: "#FF6B35" },
  { n: "market_cart_remove", d_es: "Elimina productos del carrito",         d_en: "Remove items from cart",                c: "#FF6B35" },
  { n: "market_checkout",    d_es: "Completa la compra (humano requerido)",  d_en: "Complete purchase (human-in-the-loop)",  c: "#60A5FA" },
  { n: "market_orders",      d_es: "Historial de órdenes",                   d_en: "Order history",                         c: "#A78BFA" },
  { n: "market_reorder",     d_es: "Repite una orden anterior",              d_en: "Repeat a previous order",               c: "#A78BFA" },
  { n: "market_ask",         d_es: "Compra por lenguaje natural",             d_en: "Natural language purchase",             c: "#FB923C" },
  { n: "market_basket",      d_es: "Compara canasta completa entre tiendas",  d_en: "Compare full basket across stores",     c: "#F472B6" },
  { n: "market_inflation",   d_es: "Inflación desde el data moat",            d_en: "Inflation tracking from data moat",     c: "#38BDF8" },
  { n: "market_categories",  d_es: "Árbol de categorías por tienda",          d_en: "Category tree per retailer",            c: "#34D399" },
];

export default function Features() {
  const { t: _t, lang } = useLang();

  return (
    <section id="features" className="relative flex flex-col w-full bg-[#0C0C0C] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#00FF88]/40"/>{_t("features_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">
          {lang === "es" ? "15 herramientas.\nUn ecosistema." : "15 tools.\nOne ecosystem."}
        </h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">
          {lang === "es" ? "12 originales más basket, inflation y categories. Componibles. Un solo comando." : "12 original plus basket, inflation and categories. Composable. One command."}
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 max-w-[1100px]">
        {tools.map((t) => (
          <div key={t.n} className="bg-[#0A0A0A] border border-[#1A1A1A] p-3 flex flex-col gap-1.5 hover:border-[#333] transition-all">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: t.c }} />
              <span className="text-[10px] font-mono font-bold text-white/80 truncate">{t.n}</span>
            </div>
            <p className="text-[9px] font-mono text-[#555] leading-relaxed">{lang === "es" ? t.d_es : t.d_en}</p>
          </div>
        ))}
      </div>

      <p className="text-white/20 font-mono text-[10px] uppercase tracking-widest max-w-[800px] mt-2">MCP NATIVO · API REST · JSON PARSEABLE · CROSS-BORDER · DATA FEED · CHECKOUT LOCAL</p>
      <p className="text-white/10 font-mono text-[9px] mt-1">{_t("features_live")}</p>
    </section>
  );
}
