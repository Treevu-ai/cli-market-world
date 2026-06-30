"""i18n strings and language helpers for the `market` CLI.

Extracted from market_cli.py to keep the CLI entry point focused on
command dispatch rather than copy.
"""

from __future__ import annotations

from market_core import LANG_FILE

T = {
    "es": {
        "desc": "Agentic Market CLI — compras desde la terminal.",
        "usage": "market <comando> [opciones]",
        "login": "Autenticarse", "search": "Buscar productos", "compare": "Comparar precios entre tiendas",
        "investigate": "Reporte profundo de mercado (search + compare + intel)",
        "add": "Agregar al carrito (usa # de tabla o product_id)", "cart": "Ver carrito",
        "cart_remove": "Eliminar un producto del carrito", "cart_update": "Cambiar cantidad de un producto en el carrito",
        "cart_clear": "Vaciar el carrito por completo", "checkout": "Finalizar compra",
        "orders": "Historial de órdenes", "reorder": "Repetir una orden (última si no se especifica ID)",
        "ask": "Compra por lenguaje natural", "preferences": "Ver perfil y preferencias de compra",
        "countries": "Ver países y tiendas disponibles", "lines": "Ver líneas de negocio y sus retailers",
        "stores": "Listar retailers verificados (filtro por país o línea)",
        "about": "Modelo de negocio", "whoami": "Ver sesión activa", "account": "Dashboard tier, uso y upgrade", "lang": "Cambiar idioma (es/en)",
        "categories": "Explorar categorías de una tienda", "barcode": "Buscar producto por código de barras",
        "enrich": "Buscar con datos de Open Food Facts",
        "query": "Buscar productos", "store": "Tienda específica", "country": "Filtrar por país",
        "line": "Filtrar por línea de negocio", "limit": "Cantidad de resultados", "page": "Página de resultados",
        "product_id": "Número de la tabla de búsqueda (#) o ID de producto",
        "product_name_help": "Nombre del producto (auto-fill si se usa #)",
        "price_help": "Precio (auto-fill si se usa #)", "qty": "Cantidad",
        "payment": "Método de pago", "order_id_help": "ID de la orden a repetir",
        "prompt": "Ej: 'compra leche', 'repite la última', 'compara arroz'",
        "barcode_help": "Código de barras EAN/UPC",
        "lang_code_help": "Código de idioma: es o en",
        "json_help": "Salida machine-readable para agentes IA",
        "username": "Usuario", "password": "Contraseña",
        "product_remove_help": "ID del producto a eliminar del carrito",
        "product_update_help": "ID del producto",
        "quantity_help": "Nueva cantidad (0 = eliminar)",
        "hello": "Onboarding post-install y próximos pasos",
        "register": "Crear cuenta free y API key (sk-)",
        "share": "Link de referido para compartir CLI Market",
        "upgrade": "Upgrade a Pro — suscripción PayPal (foco principal para builders de agentes)",
        "doctor": "Diagnóstico: API, auth, tier y MCP",
        "init": "Onboarding completo: API, cuenta, MCP",
        "shell": "Sesión interactiva tipo agente (REPL)",
        "intel": "Intelligence / data moat (analistas, Price Pulse)",
        "intel_inflation": "Inflación por línea y país",
        "intel_brief": "Brief ejecutivo: headline + señales + scores (una llamada)",
        "intel_indicators": "Catálogo de indicadores del moat",
        "intel_enrichment": "Enriquecimiento (OFF, Wiki, clima, CPI)",
        "intel_scores": "Scores compuestos (fairness, stress, aggression)",
        "tutorial": "Tutorial interactivo de 3 ejercicios (buscar, comparar, exportar) en 60 segundos",
        "demo": "Demo sin cuenta: token temporal + search/compare en <5 min",
        "mcp_setup": "Configuración one-liner de MCP para Cursor/Claude/etc.",
        "mcp": "Centro MCP (solo lectura): tools + salud doctor",
        "discover": "Cobertura de retailers en una llamada: líneas, tiendas y países",
        "basket": "Comparar canasta entre retailers (opción --tco)",
        "optimize": "Optimizar compra en una llamada: canasta + TCO + sustitutos + intel",
    },
    "en": {
        "desc": "Agentic Market CLI — purchases from the terminal.",
        "usage": "market <command> [options]",
        "login": "Authenticate", "search": "Search products", "compare": "Compare prices across stores",
        "investigate": "Deep market report (search + compare + intel)",
        "add": "Add to cart (use table # or product_id)", "cart": "View cart",
        "cart_remove": "Remove product from cart", "cart_update": "Change product quantity in cart",
        "cart_clear": "Clear entire cart", "checkout": "Complete purchase",
        "orders": "Order history", "reorder": "Repeat last order",
        "ask": "Natural language purchase", "preferences": "View profile and preferences",
        "countries": "View countries and stores", "lines": "View business lines and retailers",
        "stores": "List verified retailers (filter by country or line)",
        "about": "Business model", "whoami": "View active session", "account": "Account dashboard: tier, usage, upgrade", "lang": "Change language (es/en)",
        "categories": "Explore store categories", "barcode": "Search product by barcode",
        "enrich": "Search with Open Food Facts data",
        "query": "Search products", "store": "Specific store", "country": "Filter by country",
        "line": "Filter by business line", "limit": "Number of results", "page": "Results page",
        "product_id": "Table # from search or product ID",
        "product_name_help": "Product name (auto-fill if using #)",
        "price_help": "Price (auto-fill if using #)", "qty": "Quantity",
        "payment": "Payment method", "order_id_help": "Order ID to repeat",
        "prompt": "E.g. 'buy milk', 'repeat last', 'compare rice'",
        "barcode_help": "EAN/UPC barcode",
        "lang_code_help": "Language code: es or en",
        "json_help": "Machine-readable output for AI agents",
        "username": "Username", "password": "Password",
        "product_remove_help": "Product ID to remove from cart",
        "product_update_help": "Product ID",
        "quantity_help": "New quantity (0 = remove)",
        "hello": "Post-install onboarding and next steps",
        "register": "Create free account and API key (sk-)",
        "share": "Referral link to share CLI Market",
        "upgrade": "Upgrade Starter/Pro — PayPal subscription",
        "doctor": "Diagnostics: API, auth, tier, and MCP",
        "init": "Full onboarding: API, account, MCP",
        "shell": "Interactive agent-style session (REPL)",
        "intel": "Intelligence / data moat (analysts, Price Pulse)",
        "intel_inflation": "Inflation by line and country",
        "intel_brief": "Executive brief: headline + shelf signals + scores (one call)",
        "intel_indicators": "Moat indicator catalog",
        "intel_enrichment": "Enrichment signals (OFF, Wiki, weather, CPI)",
        "intel_scores": "Composite scores (fairness, stress, aggression)",
        "tutorial": "Interactive 3-step tutorial (search, compare, export) in 60 seconds",
        "demo": "No-account demo: temp token + search/compare in under 5 minutes",
        "mcp_setup": "One-liner MCP setup for Cursor/Claude/etc.",
        "mcp": "MCP center (read-only): tools + doctor health",
        "discover": "Retail coverage in one call: lines, stores, and countries",
        "basket": "Compare basket across retailers (--tco for full cost)",
        "optimize": "One-call purchase optimization: basket + TCO + substitutes + intel",
    },
}

_LEGACY_INTEL_CMDS = frozenset({"inflation", "indicators", "enrichment", "scores"})
_META_CMDS = frozenset({"about", "share"})


def get_lang() -> str:
    if LANG_FILE.exists():
        return LANG_FILE.read_text().strip()
    return "es"


def set_lang(code: str) -> None:
    LANG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LANG_FILE.write_text(code)


def t(key: str) -> str:
    lang = get_lang()
    return T.get(lang, {}).get(key, key)
