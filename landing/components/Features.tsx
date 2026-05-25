"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";

const tools = [
  { n: "market_login",   d_es: "Autentica al agente para operar",        d_en: "Authenticate the agent session",
    demo_es: "market login\n→ Token guardado en ~/.market/session.json\n→ Todas las tools requieren este paso.",
    demo_en: "market login\n→ Token stored in ~/.market/session.json\n→ All tools require this step first.",
    c: "#3cffd0" },
  { n: "market_lines",   d_es: "Lista las 6 lineas con sus retailers",   d_en: "List 6 business lines with retailers",
    demo_es: "market lines\n→ supermercados (14) · electro (9) · farmacias (4) · moda (2) · hogar (2) · departamentales (1)",
    demo_en: "market lines\n→ supermarkets (14) · electronics (9) · pharmacies (4) · fashion (2) · home (2) · department (1)",
    c: "#3cffd0" },
  { n: "market_search",  d_es: "Busca productos en 30 retailers",        d_en: "Search products across 30 retailers",
    demo_es: 'market search "leche" --country PE\n→ 1. Leche Gloria 400ml  Wong  S/3.50\n→ 2. Leche Ideal 395g  Metro  S/3.20',
    demo_en: 'market search "milk" --country AR\n→ 1. Milk 1L  Carrefour  ARS 1,200\n→ 2. Milk 1L  Jumbo  ARS 1,150',
    c: "#FFD600" },
  { n: "market_compare", d_es: "Compara precios entre paises",            d_en: "Cross-country price comparison",
    demo_es: 'market compare "aceite"\n→ Aceite Primor 1L: Wong S/8.90, Carrefour AR ARS 1250, Exito COP 8500\n→ Mejor: Wong',
    demo_en: 'market compare "oil"\n→ Oil 1L: Wong PEN 8.90, Carrefour AR ARS 1250, Exito COP 8500\n→ Best: Wong',
    c: "#4ADE80" },
  { n: "market_add",     d_es: "Agrega productos al carrito",            d_en: "Add products to cart",
    demo_es: "market add 3 --qty 2\n→ Agregado: 2x Leche Gloria 400ml\n→ Carrito: 2 items, total S/7.00",
    demo_en: "market add 3 --qty 2\n→ Added: 2x Milk 1L\n→ Cart: 2 items, total ARS 2,400",
    c: "#FF6B35" },
  { n: "market_cart",    d_es: "Muestra el carrito actual",               d_en: "View current cart",
    demo_es: "market cart\n→ 1. 2x Leche Gloria 400ml  Wong  S/3.50\n→ 2. 1x Arroz Costeno 1kg  Metro  S/4.20\n→ Total: S/11.20",
    demo_en: "market cart\n→ 1. 2x Milk 1L  Carrefour  ARS 1,200\n→ 2. 1x Rice 1kg  Jumbo  ARS 980\n→ Total: ARS 3,380",
    c: "#FF6B35" },
  { n: "market_cart_update", d_es: "Cambia cantidades en el carrito",    d_en: "Update cart quantities",
    demo_es: "market cart-update <product_id> 5\n→ Cantidad actualizada a 5",
    demo_en: "market cart-update <product_id> 5\n→ Quantity updated to 5",
    c: "#FF6B35" },
  { n: "market_cart_remove", d_es: "Elimina productos del carrito",      d_en: "Remove items from cart",
    demo_es: "market cart-remove <product_id>\n→ Producto eliminado del carrito",
    demo_en: "market cart-remove <product_id>\n→ Item removed from cart",
    c: "#FF6B35" },
  { n: "market_checkout", d_es: "Completa la compra (humano requerido)",   d_en: "Complete purchase (human-in-the-loop)",
    demo_es: "market checkout --payment yape\n→ Pedido #ORD-004 confirmado\n→ Total: S/11.20 · Pago: Yape\n→ Requiere aprobacion humana",
    demo_en: "market checkout --payment card\n→ Order #ORD-004 confirmed\n→ Total: ARS 3,380 · Payment: Card\n→ Requires human approval",
    c: "#60A5FA" },
  { n: "market_orders",  d_es: "Historial de ordenes",                    d_en: "Order history",
    demo_es: "market orders\n→ #ORD-001  2026-05-18  S/15.50  Yape\n→ #ORD-002  2026-05-19  S/8.90   Plin",
    demo_en: "market orders\n→ #ORD-001  2026-05-18  ARS 5,200  Card\n→ #ORD-002  2026-05-19  ARS 3,100  Card",
    c: "#A78BFA" },
  { n: "market_reorder", d_es: "Repite una orden anterior",               d_en: "Repeat a previous order",
    demo_es: "market reorder ORD-001\n→ Orden ORD-001 restaurada al carrito\n→ 3 items listos para checkout",
    demo_en: "market reorder ORD-001\n→ Order ORD-001 restored to cart\n→ 3 items ready for checkout",
    c: "#A78BFA" },
  { n: "market_ask",     d_es: "Compra por lenguaje natural",              d_en: "Natural language purchase",
    demo_es: 'market ask "compra 2 leche y 1 arroz al mejor precio"\n→ Buscando leche... Comparando arroz...\n→ Mejor: Wong — S/11.20 total',
    demo_en: 'market ask "buy 2 milk and 1 rice at the best price"\n→ Searching milk... Comparing rice...\n→ Best: Wong — S/11.20 total',
    c: "#FB923C" },
  { n: "market_basket",  d_es: "Compara canasta completa entre tiendas",   d_en: "Compare full basket across stores",
    demo_es: "market basket leche:2 arroz:1 --country AR\n→ Carrefour AR: ARS 3,380\n→ Jumbo AR: ARS 3,150  ······ MEJOR\n→ Vea AR: ARS 3,420",
    demo_en: "market basket milk:2 rice:1 --country AR\n→ Carrefour AR: ARS 3,380\n→ Jumbo AR: ARS 3,150  ······ BEST\n→ Vea AR: ARS 3,420",
    c: "#F472B6" },
  { n: "market_inflation", d_es: "Inflacion desde el data moat",           d_en: "Inflation tracking from data moat",
    demo_es: "market inflation --country AR\n→ Inflacion promedio: +2.3%\n→ 127 productos rastreados · ultima actualizacion: hace 4h",
    demo_en: "market inflation --country AR\n→ Avg inflation: +2.3%\n→ 127 products tracked · last updated: 4h ago",
    c: "#38BDF8" },
  { n: "market_categories", d_es: "Arbol de categorias por tienda",        d_en: "Category tree per retailer",
    demo_es: "market categories wong\n→ Alimentos\n  Lacteos\n  Panaderia\n  Carnes\n→ Bebidas\n→ Limpieza",
    demo_en: "market categories carrefour\n→ Food\n  Dairy\n  Bakery\n  Meat\n→ Drinks\n→ Cleaning",
    c: "#34D399" },
];

export default function Features() {
  const { t: _t, lang } = useLang();
  const [active, setActive] = useState<number | null>(null);

  return (
    <section id="features" className="relative flex flex-col w-full bg-[#131313] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#3cffd0]/40"/>{_t("features_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05] whitespace-pre-line">
          {lang === "es" ? "19 herramientas.\nUn ecosistema." : "19 tools.\nOne ecosystem."}
        </h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">
          {lang === "es" ? "Clickea cualquier tool para ver como funciona." : "Click any tool to see how it works."}
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 max-w-[1100px]">
        {tools.map((t, i) => {
          const isOpen = active === i;
          return (
            <div key={t.n}>
              <button
                onClick={() => setActive(isOpen ? null : i)}
                className="w-full text-left bg-[#131313] border p-3 flex flex-col gap-1.5 transition-all cursor-pointer"
                style={{ borderColor: isOpen ? t.c : "#2d2d2d", background: isOpen ? `${t.c}08` : "#131313" }}
              >
                <div className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: t.c }} />
                  <span className="text-[10px] font-mono font-bold text-white/80 truncate">{t.n}</span>
                  <span className="ml-auto text-[9px] font-mono" style={{ color: isOpen ? t.c : "#333" }}>{isOpen ? "−" : "+"}</span>
                </div>
                <p className="text-[9px] font-mono text-[#555] leading-relaxed">{lang === "es" ? t.d_es : t.d_en}</p>
              </button>
              {isOpen && (
                <div className="bg-[#0c0c0c] border border-t-0 px-3 py-3 font-mono text-[9px] leading-relaxed whitespace-pre-wrap" style={{ borderColor: `${t.c}30` }}>
                  <span className="text-[#888]">{lang === "es" ? t.demo_es : t.demo_en}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Checkout receipt */}
      <div className="max-w-[500px] bg-[#131313] border border-[#2d2d2d] overflow-hidden mt-6">
        <div className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] border-b border-[#2d2d2d]">
          <div className="w-[8px] h-[8px] rounded-full bg-[#FF5F57]"/><div className="w-[8px] h-[8px] rounded-full bg-[#FEBC2E]"/><div className="w-[8px] h-[8px] rounded-full bg-[#28C840]"/>
          <span className="ml-2 text-[9px] font-mono text-[#555] tracking-wider">CHECKOUT — ORD-004</span>
          <span className="ml-auto text-[8px] font-mono text-[#28C840]">● {lang === "es" ? "CONFIRMADO" : "CONFIRMED"}</span>
        </div>
        <div className="p-5 font-mono text-[10px] leading-relaxed">
          <div className="flex justify-between text-[#888] border-b border-[#2d2d2d] pb-3 mb-3">
            <span>{lang === "es" ? "Tienda" : "Store"}</span>
            <span className="text-white/60">Wong · 🇵🇪</span>
          </div>
          <div className="space-y-2 border-b border-[#2d2d2d] pb-3 mb-3">
            <div className="flex justify-between"><span className="text-[#888]">2× Leche Gloria 400ml</span><span className="text-white/60">S/7.00</span></div>
            <div className="flex justify-between"><span className="text-[#888]">1× Arroz Costeno 1kg</span><span className="text-white/60">S/4.20</span></div>
            <div className="flex justify-between"><span className="text-[#888]">1× Aceite Primor 1L</span><span className="text-white/60">S/8.90</span></div>
          </div>
          <div className="flex justify-between text-[#3cffd0] font-bold">
            <span>TOTAL</span>
            <span>S/20.10</span>
          </div>
          <div className="flex justify-between text-[#555] mt-2 text-[9px]">
            <span>{lang === "es" ? "Pago" : "Payment"}</span>
            <span>Yape · {lang === "es" ? "Aprobado" : "Approved"}</span>
          </div>
          <div className="text-[9px] text-[#444] mt-3 text-center border-t border-[#2d2d2d] pt-3">
            market checkout --payment yape
          </div>
        </div>
      </div>

      <p className="text-white/20 font-mono text-[10px] uppercase tracking-widest max-w-[800px] mt-2">MCP NATIVO · API REST · JSON PARSEABLE · CROSS-BORDER · DATA FEED · CHECKOUT LOCAL</p>
      <p className="text-white/10 font-mono text-[9px] mt-1">{_t("features_live")}</p>
    </section>
  );
}
