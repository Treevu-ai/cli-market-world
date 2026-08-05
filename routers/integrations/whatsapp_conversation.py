"""Standard WhatsApp conversation funnel for product price queries.

Handles the common case where users start with a generic description
("aceite", "limpieza", "pollo") instead of a precise SKU. Flow:

  idle → (vague) clarify family → (medium/specific) catalog candidates
       → pick 1..N for offer detail
  multi-line list (2–20 líneas) → POST /v1/basket/compare → store review
  analytic / open questions still go to /v1/intel/ask with guardrails

Session state is stored as JSON in messenger_sessions.last_context.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Awaitable, Callable

import httpx

from server_deps import get_messenger_session, update_messenger_session

logger = logging.getLogger("market.whatsapp.conversation")

FLOW_TYPE = "wa_flow"
DEFAULT_COUNTRY = "PE"
MAX_CANDIDATES = 3
MAX_BASKET_ITEMS = 20
MIN_BASKET_ITEMS = 2
# Small PE supermarket set — complete-basket compare is only useful when every
# item can be checked in the same channel (mirrors Telegram HORECA segment).
DEFAULT_BASKET_STORES = ("wong", "metro", "plazavea", "makro_pe", "vega_pe")

_BASKET_HELP = frozenset(
    {
        "canasta",
        "cotizar",
        "cotizacion",
        "cotización",
        "lista",
        "pedido",
        "mi lista",
        "armar canasta",
    }
)
_BASKET_LINE_RE = re.compile(
    r"^(?:(\d{1,4})\s*(?:x|unidades?|unds?|u)?\s+)?(.+?)$",
    re.IGNORECASE,
)

# Product families that almost never mean a single SKU on first turn.
_FAMILY_CLARIFY: dict[str, list[str]] = {
    "aceite": ["Vegetal / soya", "Oliva", "Girasol", "Otro (escribí marca o tipo)"],
    "aceites": ["Vegetal / soya", "Oliva", "Girasol", "Otro (escribí marca o tipo)"],
    "leche": ["Evaporada", "Entera / fresca", "Deslactosada", "Otro (marca o presentación)"],
    "arroz": ["Extra / superior 5 kg", "Integral", "Arborio / especial", "Otro"],
    "pollo": ["Pechuga", "Entero", "Trozado / muslo", "Otro"],
    "cafe": ["Molido", "Instantáneo", "En grano", "Otro (marca)"],
    "café": ["Molido", "Instantáneo", "En grano", "Otro (marca)"],
    "limpieza": ["Detergente", "Cloro / lejía", "Desinfectante", "Otro"],
    "detergente": ["Ropa (polvo/líquido)", "Loza", "Industrial", "Otro"],
    "jabon": ["Tocador", "Lavavajilla", "Industrial", "Otro"],
    "jabón": ["Tocador", "Lavavajilla", "Industrial", "Otro"],
    "papel": ["Higiénico", "Toalla", "Servilletas", "Otro"],
    "azucar": ["Blanca", "Rubia", "Endulzante", "Otro"],
    "azúcar": ["Blanca", "Rubia", "Endulzante", "Otro"],
    "agua": ["Sin gas 2.5–3 L", "Con gas", "Personal 600 ml", "Otro"],
    "huevo": ["Parda / roja", "Blanca", "Organica", "Otro"],
    "huevos": ["Parda / roja", "Blanca", "Organica", "Otro"],
    "pan": ["De molde", "Francés / baguette", "Integral", "Otro"],
    "queso": ["Edam / mantecoso", "Parmesano", "Crema / fresco", "Otro"],
    "yogurt": ["Natural", "Griego", "Batido / sabor", "Otro"],
    "yogur": ["Natural", "Griego", "Batido / sabor", "Otro"],
    "harina": ["Sin preparar", "Preparada", "Integral", "Otro"],
    "fideos": ["Spaghetti", "Cabello de ángel", "Mostachol", "Otro"],
    "pasta": ["Spaghetti", "Cabello de ángel", "Mostachol", "Otro"],
    "carne": ["Res", "Cerdo", "Molida", "Otro"],
    "pescado": ["Filete", "Entero", "Conserva", "Otro"],
    "gaseosa": ["Personal", "1.5–2 L", "Zero / light", "Otro"],
    "cerveza": ["Lata", "Botella", "Six-pack", "Otro"],
    "insumos": ["Aceites y grasas", "Lácteos", "Limpieza", "Otro (describí)"],
}

_GREETINGS = frozenset(
    {
        "hola",
        "hi",
        "hello",
        "buenas",
        "buen dia",
        "buen día",
        "buenos dias",
        "buenos días",
        "hey",
        "ola",
    }
)
_HELP = frozenset({"ayuda", "help", "menu", "menú", "start", "inicio"})
_RESET = frozenset({"reset", "reiniciar", "cancelar", "salir"})
_BACK = frozenset({"atras", "atrás", "back", "volver"})

_SIZE_RE = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:ml|m\.?l\.?|l|lt|lts|litro|litros|g|gr|grs|kg|kilos?|oz|lb|unid(?:ades?)?|unds?|u\.?)\b",
    re.IGNORECASE,
)
_INTEL_RE = re.compile(
    r"\b("
    r"cu[aá]nto|cu[aá]nta|compara(?:r)?|comparaci[oó]n|subir|bajar|"
    r"inflaci[oó]n|tendencia|historial|variaci[oó]n|va a|pron[oó]stico|"
    r"m[aá]s barato|mas barato|mejor precio|ahorro|nowcast"
    r")\b",
    re.IGNORECASE,
)
_COUNTRY_RE = re.compile(
    r"\b(per[uú]|pe|lima|colombia|co|bogot[aá]|m[eé]xico|mx|brasil|br|chile|cl|argentina|ar)\b",
    re.IGNORECASE,
)

SearchFn = Callable[[str, str, str | None], Awaitable[list[dict] | None]]
IntelFn = Callable[[str, str | None], Awaitable[str]]
# (items, country, token) → (payload dict | None, http status | None)
BasketFn = Callable[
    [list[dict], str, str | None],
    Awaitable[tuple[dict | None, int | None]],
]


def _normalize_msg(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _guess_country(text: str) -> str:
    m = _COUNTRY_RE.search(text or "")
    if not m:
        return DEFAULT_COUNTRY
    token = m.group(1).lower()
    mapping = {
        "peru": "PE",
        "perú": "PE",
        "pe": "PE",
        "lima": "PE",
        "colombia": "CO",
        "co": "CO",
        "bogota": "CO",
        "bogotá": "CO",
        "mexico": "MX",
        "méxico": "MX",
        "mx": "MX",
        "brasil": "BR",
        "br": "BR",
        "chile": "CL",
        "cl": "CL",
        "argentina": "AR",
        "ar": "AR",
    }
    return mapping.get(token, DEFAULT_COUNTRY)


def _load_state(platform_id: str) -> dict[str, Any]:
    session = get_messenger_session(platform_id)
    raw = session.get("last_context")
    if not raw:
        return {"type": FLOW_TYPE, "state": "idle", "country": session.get("last_country") or DEFAULT_COUNTRY}
    if isinstance(raw, dict):
        data = raw
    else:
        try:
            data = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            return {
                "type": FLOW_TYPE,
                "state": "idle",
                "country": session.get("last_country") or DEFAULT_COUNTRY,
                "legacy_context": str(raw)[:300],
            }
    if not isinstance(data, dict) or data.get("type") != FLOW_TYPE:
        # Preserve foreign contexts (e.g. HORECA) as idle for standard flow.
        return {"type": FLOW_TYPE, "state": "idle", "country": session.get("last_country") or DEFAULT_COUNTRY}
    data.setdefault("state", "idle")
    data.setdefault("country", session.get("last_country") or DEFAULT_COUNTRY)
    return data


def _save_state(
    platform_id: str,
    state: dict[str, Any],
    *,
    last_query: str | None = None,
    last_country: str | None = None,
) -> None:
    payload = dict(state)
    payload["type"] = FLOW_TYPE
    update_messenger_session(
        platform_id,
        context=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        last_query=last_query,
        last_country=last_country or payload.get("country"),
    )


def _clear_state(platform_id: str, country: str = DEFAULT_COUNTRY) -> None:
    _save_state(
        platform_id,
        {"type": FLOW_TYPE, "state": "idle", "country": country},
        last_country=country,
    )


def classify_specificity(message: str) -> str:
    """Return one of: greeting, help, back, reset, pick, clarify_choice, vague, medium, specific, intel."""
    msg = _normalize_msg(message)
    if not msg:
        return "help"
    if msg in _GREETINGS:
        return "greeting"
    if msg in _HELP:
        return "help"
    if msg in _RESET:
        return "reset"
    if msg in _BACK:
        return "back"
    if re.fullmatch(r"[1-5]", msg):
        return "pick"
    if _INTEL_RE.search(msg):
        return "intel"

    tokens = msg.split()
    size = bool(_SIZE_RE.search(msg))
    family = tokens[0] if tokens else ""
    in_family = family in _FAMILY_CLARIFY

    # Single-token family → always clarify first.
    if len(tokens) == 1 and in_family:
        return "vague"
    # Family alone plus filler words without size/brand detail.
    if in_family and len(tokens) <= 2 and not size:
        # "aceite oliva" is medium (type known); "aceite barato" still vague-ish → medium search
        second = tokens[1] if len(tokens) > 1 else ""
        if second in {"barato", "barata", "precio", "precios", "para", "de", "el", "la", "un", "una"}:
            return "vague"
        return "medium"
    if size and len(tokens) >= 2:
        return "specific"
    if len(tokens) >= 3:
        return "specific"
    if len(tokens) == 2:
        return "medium"
    return "medium"


def build_welcome_message() -> str:
    return (
        "¡Hola! Soy el bot de *CLI Market* 🚀\n\n"
        "Te ayudo a ver *precios de góndola* en supermercados (por defecto *Perú*).\n\n"
        "*Cómo preguntar:*\n"
        "• Mal: `aceite`\n"
        "• Bien: `aceite Primor 1L` o `aceite vegetal 1 litro`\n\n"
        "*Canasta (varios productos):*\n"
        "Mandá *2 a 20 líneas* en un solo mensaje, por ejemplo:\n"
        "12 x leche Gloria 390 g\n"
        "4 x aceite vegetal 1 L\n"
        "2 x arroz extra 5 kg\n"
        "También: escribí `canasta` para el ejemplo.\n\n"
        "*Otros:*\n"
        "1️⃣ Un producto → hasta 3 opciones\n"
        "2️⃣ `compara leche evaporada en Lima`\n"
        "3️⃣ `¿va a subir el arroz?`\n\n"
        "Atajos: `menu` · `atras` · *1/2/3* elige opción o tienda.\n\n"
        "*Límites:* no compro ni pago; solo precios observados."
    )


def build_basket_help_message() -> str:
    return (
        "Para cotizar una *canasta*, enviá entre *2 y 20 productos*, "
        "una línea por producto (podés usar `;` si WhatsApp junta todo):\n\n"
        "12 x leche Gloria 390 g\n"
        "4 x aceite vegetal 1 L\n"
        "2 x arroz extra 5 kg\n\n"
        "Incluí marca y presentación cuando las sepas. "
        "Sin cobertura completa no muestro total ni 'mejor tienda'."
    )


def parse_basket_items(text: str) -> list[dict] | None:
    """Parse 2–20 product lines (newline or ';' separated). Same contract as Telegram."""
    if not text or not str(text).strip():
        return None
    # Strip a leading command word so "canasta\n2 x leche..." still parses.
    raw = str(text).strip()
    first_line, _, rest = raw.partition("\n")
    if _normalize_msg(first_line) in _BASKET_HELP and rest.strip():
        raw = rest
    raw_lines = [
        line.strip(" -•\t")
        for line in re.split(r"[\n;]+", raw)
        if line.strip(" -•\t")
    ]
    # Drop pure command-only first token lines already handled.
    raw_lines = [ln for ln in raw_lines if _normalize_msg(ln) not in _BASKET_HELP]
    if len(raw_lines) < MIN_BASKET_ITEMS or len(raw_lines) > MAX_BASKET_ITEMS:
        return None
    items: list[dict] = []
    for line in raw_lines:
        match = _BASKET_LINE_RE.match(line)
        if not match:
            return None
        name = match.group(2).strip()
        if not name or len(name) > 200:
            return None
        # Reject pure greetings/help as basket lines
        if _normalize_msg(name) in _GREETINGS | _HELP | _RESET | _BACK | _BASKET_HELP:
            return None
        items.append({"name": name, "qty": int(match.group(1) or 1)})
    return items


def _basket_store_from_result(store: dict) -> dict:
    breakdown = []
    for row in (store.get("breakdown") or [])[:20]:
        if not isinstance(row, dict):
            continue
        breakdown.append(
            {
                "item": str(row.get("item") or "")[:200],
                "resolved_name": str(row.get("resolved_name") or "")[:240],
                "brand": str(row.get("brand") or "")[:120],
                "qty": row.get("qty"),
                "unit_price": row.get("unit_price"),
                "item_total": row.get("item_total"),
                "canonical_product_id": str(row.get("canonical_product_id") or "")[:160],
                "match_confidence": str(row.get("match_confidence") or "")[:20],
            }
        )
    return {
        "store": str(store.get("store") or "")[:80],
        "store_name": str(store.get("store_name") or "Tienda")[:120],
        "currency": str(store.get("currency") or "PEN")[:12],
        "total": store.get("total"),
        "items_found": store.get("items_found"),
        "breakdown": breakdown,
    }


def format_basket_store_list(items_searched: int, stores: list[dict], country: str) -> str:
    lines = [
        f"*Canasta con cobertura completa* ({country})",
        f"{items_searched} productos con match en {len(stores)} tienda(s).",
        "Revisá marca/presentación por tienda antes de usar un total.",
        "No es cotización contractual ni recomendación de compra.",
        "",
    ]
    for i, store in enumerate(stores[:5], start=1):
        currency = str(store.get("currency") or "PEN").upper()
        prefix = {"PEN": "S/", "USD": "US$"}.get(currency, currency)
        total = store.get("total")
        total_s = f"{prefix} {total}" if total is not None else "sin total"
        lines.append(f"{i}. *{store.get('store_name', 'Tienda')}* — {total_s}")
    lines.extend(
        [
            "",
            f"Respondé *1*{'-' + str(min(len(stores), 5)) if len(stores) > 1 else ''} "
            "para ver el desglose de esa tienda.",
        ]
    )
    return "\n".join(lines)


def format_basket_store_detail(store: dict) -> str:
    currency = str(store.get("currency") or "PEN").upper()
    prefix = {"PEN": "S/", "USD": "US$"}.get(currency, currency)
    lines = [
        f"*Revisión — {store.get('store_name', 'Tienda')}*",
        "",
    ]
    for row in store.get("breakdown") or []:
        qty = row.get("qty") or 1
        requested = row.get("item") or "?"
        resolved = row.get("resolved_name") or "sin match"
        brand = row.get("brand") or "s/marca"
        unit = row.get("unit_price")
        unit_s = f"{prefix} {unit}" if unit is not None else "s/precio"
        conf = row.get("match_confidence") or "?"
        lines.append(
            f"• {qty} × {requested}\n"
            f"  → {resolved} · {brand} · {unit_s}\n"
            f"  match: {conf}"
        )
    total = store.get("total")
    total_s = f"{prefix} {total}" if total is not None else "sin dato"
    lines.extend(
        [
            "",
            f"Total observado: *{total_s}*",
            "",
            "Confirmá equivalencia de cada línea. Escribí otra lista o `menu`.",
        ]
    )
    return "\n".join(lines)


async def default_compare_basket(
    items: list[dict],
    token: str | None,
    country: str,
    market_api_url: str,
    stores: tuple[str, ...] | list[str] | None = None,
) -> tuple[dict | None, int | None]:
    if not token:
        return None, None
    payload: dict[str, Any] = {
        "items": items,
        "country": country,
        "enveloped": False,
        "stores": list(stores or DEFAULT_BASKET_STORES),
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{market_api_url.rstrip('/')}/v1/basket/compare",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=35,
            )
        if response.status_code == 200:
            data = response.json()
            return (data if isinstance(data, dict) else None), 200
        logger.warning("WA basket/compare %s: %s", response.status_code, response.text[:200])
        return None, response.status_code
    except Exception as exc:
        logger.warning("WA basket/compare failed: %s", exc)
        return None, None


async def process_basket_list(
    platform_id: str,
    raw_message: str,
    *,
    token: str | None,
    market_api_url: str,
    basket_fn: BasketFn | None = None,
) -> str:
    items = parse_basket_items(raw_message)
    if items is None:
        return build_basket_help_message()

    country = _guess_country(raw_message)
    if basket_fn is None:

        async def _basket(
            its: list[dict], ctry: str, tok: str | None
        ) -> tuple[dict | None, int | None]:
            return await default_compare_basket(its, tok, ctry, market_api_url)

        basket_fn = _basket

    result, status = await basket_fn(items, country, token)
    if status == 403:
        return (
            "La comparación de canastas requiere acceso Pro. "
            "Podés buscar un producto a la vez escribiendo el nombre."
        )
    if result is None:
        return "No pude verificar la canasta ahora. Probá de nuevo en un momento."

    items_searched = int(result.get("items_searched") or len(items))
    items_found = int(result.get("items_found") or 0)
    if items_found < items_searched:
        _save_state(
            platform_id,
            {"type": FLOW_TYPE, "state": "idle", "country": country, "candidates": []},
            last_query=raw_message[:200],
            last_country=country,
        )
        return (
            f"Cobertura incompleta: encontré *{items_found}* de *{items_searched}* productos.\n"
            "No muestro total ni mejor tienda con gaps.\n\n"
            "Reenviá la lista con *marca y presentación* más claras "
            "(ej. `leche Gloria evaporada 400g` en lugar de `leche`)."
        )

    raw_stores = result.get("stores") or []
    if not isinstance(raw_stores, list):
        raw_stores = []
    full_stores = [
        _basket_store_from_result(store)
        for store in raw_stores
        if isinstance(store, dict) and int(store.get("items_found") or 0) >= items_searched
    ]
    if not full_stores:
        return (
            "Encontré productos sueltos, pero *ninguna tienda cubre la canasta completa*.\n"
            "No muestro total. Ajustá marca/presentación o separá la compra."
        )

    # Prefer high-confidence canonical matches when available; else show full stores
    # with an honesty note (WhatsApp users need a usable path without Telegram keyboards).
    verified = [
        s
        for s in full_stores
        if s.get("breakdown")
        and all(
            row.get("canonical_product_id") and row.get("match_confidence") == "high"
            for row in s["breakdown"]
        )
    ][:5]
    stores_out = verified or full_stores[:5]
    low_conf = not verified

    state = {
        "type": FLOW_TYPE,
        "state": "basket_stores",
        "country": country,
        "items_searched": items_searched,
        "stores": stores_out,
        "candidates": [],
    }
    _save_state(platform_id, state, last_query=raw_message[:200], last_country=country)
    body = format_basket_store_list(items_searched, stores_out, country)
    if low_conf:
        body += (
            "\n\n_Nota: la identidad de algunos ítems no es alta confianza. "
            "Revisá el desglose antes de decidir._"
        )
    return body


def build_clarify_message(family: str, options: list[str]) -> str:
    lines = [
        f"*{family.capitalize()}* puede ser varias cosas. ¿Qué buscás?",
        "",
    ]
    for i, opt in enumerate(options, start=1):
        lines.append(f"{i}. {opt}")
    lines.extend(
        [
            "",
            "Respondé con el *número*, o escribí marca y tamaño (ej. `Primor 1L`).",
        ]
    )
    return "\n".join(lines)


def _price_label(candidate: dict) -> str:
    price = candidate.get("price")
    if price is None or price == "":
        return "sin precio"
    currency = str(candidate.get("currency") or "PEN").upper()
    prefix = {"PEN": "S/", "USD": "US$", "MXN": "MX$", "COP": "COL$", "BRL": "R$", "CLP": "CLP$"}.get(
        currency, currency
    )
    try:
        value = float(price)
        price_s = f"{value:.2f}" if value < 1000 else f"{value:.0f}"
    except (TypeError, ValueError):
        price_s = str(price)
    return f"{prefix} {price_s}"


def candidate_from_result(result: dict) -> dict:
    return {
        "id": str(result.get("id") or "")[:120],
        "name": str(result.get("name") or "Producto sin nombre")[:240],
        "brand": str(result.get("brand") or "")[:120],
        "price": result.get("price"),
        "currency": str(result.get("currency") or "")[:12],
        "store_name": str(result.get("store_name") or result.get("store") or "Tienda")[:120],
        "stock": result.get("stock"),
        "canonical_product_id": str(result.get("canonical_product_id") or "")[:160],
    }


def format_candidates_message(query: str, candidates: list[dict], country: str) -> str:
    if not candidates:
        return (
            f"No encontré coincidencias claras para *{query}* ({country}).\n\n"
            "Probá con marca y presentación, por ejemplo:\n"
            "• `aceite Primor 1L`\n"
            "• `leche Gloria evaporada 400g`\n\n"
            "O escribí otra descripción. `menu` para empezar de nuevo."
        )
    lines = [
        f"Resultados para *{query}* ({country}):",
        "",
    ]
    for i, c in enumerate(candidates, start=1):
        brand = c.get("brand") or ""
        brand_bit = f" · {brand}" if brand else ""
        lines.append(
            f"{i}. {c.get('name', 'Producto')}{brand_bit}\n"
            f"   {_price_label(c)} · {c.get('store_name', 'Tienda')}"
        )
    lines.extend(
        [
            "",
            f"Respondé *1*{'-' + str(len(candidates)) if len(candidates) > 1 else ''} para ver el detalle, "
            "o escribí otra marca/presentación.",
        ]
    )
    return "\n".join(lines)


def format_detail_message(candidate: dict) -> str:
    brand = candidate.get("brand") or "sin marca"
    stock = candidate.get("stock")
    stock_s = str(stock) if stock not in (None, "") else "sin dato"
    return (
        f"*{candidate.get('name', 'Producto')}*\n"
        f"Marca: {brand}\n"
        f"Tienda: {candidate.get('store_name', 'Tienda')}\n"
        f"Precio observado: *{_price_label(candidate)}*\n"
        f"Stock reportado: {stock_s}\n\n"
        "Precio de góndola observado (no es oferta contractual).\n"
        "Escribí otro producto, o `menu` para el inicio."
    )


def resolve_clarify_choice(choice: str, family: str, options: list[str]) -> str | None:
    """Map 1..N or free text to a refined search query."""
    msg = _normalize_msg(choice)
    if re.fullmatch(r"[1-9]", msg):
        idx = int(msg) - 1
        if 0 <= idx < len(options):
            opt = options[idx]
            # "Otro..." → ask free text, not search yet
            if opt.lower().startswith("otro"):
                return None
            # Strip parentheticals for cleaner search
            clean = re.sub(r"\s*/\s*", " ", opt)
            clean = re.sub(r"\s*\(.*?\)\s*", " ", clean).strip()
            return f"{family} {clean}".strip()
    # Free text refinement
    if msg and msg not in _GREETINGS | _HELP | _BACK | _RESET:
        return f"{family} {msg}".strip() if family else msg
    return None


def is_clarify_other_choice(choice: str, options: list[str]) -> bool:
    msg = _normalize_msg(choice)
    if re.fullmatch(r"[1-9]", msg):
        idx = int(msg) - 1
        if 0 <= idx < len(options):
            return options[idx].lower().startswith("otro")
    return False


def build_intel_question(user_msg: str, prior: str | None = None) -> str:
    guard = (
        "Responde solo con datos verificables de CLI Market. "
        "Si falta marca, presentación o equivalencia, pide una aclaración breve "
        "(una pregunta). No inventes ahorro ni 'mejor tienda' con datos incompletos. "
        "Sé conciso (WhatsApp)."
    )
    if prior:
        return f"{guard}\nContexto previo: {prior}\nConsulta: {user_msg}"
    return f"{guard}\nConsulta: {user_msg}"


async def default_search_catalog(
    query: str, token: str | None, country: str, market_api_url: str
) -> list[dict] | None:
    if not token:
        return None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{market_api_url.rstrip('/')}/products/search",
                json={
                    "query": query,
                    "country": country,
                    "limit": MAX_CANDIDATES,
                    "require_all": True,
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
        if response.status_code == 200:
            payload = response.json()
            results = payload.get("results", [])
            return results if isinstance(results, list) else []
        logger.warning("WA catalog search %s: %s", response.status_code, response.text[:200])
    except Exception as exc:
        logger.warning("WA catalog search failed: %s", exc)
    return None


async def default_ask_intel(question: str, token: str | None, market_api_url: str) -> str:
    if not token:
        return "El bot no está configurado para consultar precios ahora."
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{market_api_url.rstrip('/')}/v1/intel/ask",
                json={"question": question},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
        if response.status_code == 200:
            return str(response.json().get("answer") or "").strip() or (
                "No pude armar una respuesta con datos verificables. "
                "Probá con marca y presentación."
            )
        logger.warning("WA intel %s: %s", response.status_code, response.text[:200])
    except Exception as exc:
        logger.warning("WA intel failed: %s", exc)
    return "No pude consultar los precios ahora. Probá de nuevo en un ratito."


async def _run_search_and_format(
    platform_id: str,
    query: str,
    country: str,
    token: str | None,
    market_api_url: str,
    search_fn: SearchFn | None,
) -> str:
    using_default_search = search_fn is None
    if search_fn is None:

        async def _search(q: str, c: str, t: str | None) -> list[dict] | None:
            return await default_search_catalog(q, t, c, market_api_url)

        search_fn = _search

    results = await search_fn(query, country, token)
    if results is None:
        return "No pude consultar el catálogo ahora. Probá de nuevo en un momento."

    candidates = [candidate_from_result(row) for row in results[:MAX_CANDIDATES]]
    # Soft retry without require_all when the strict catalog pass is empty.
    if not candidates and using_default_search and token:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{market_api_url.rstrip('/')}/products/search",
                    json={
                        "query": query,
                        "country": country,
                        "limit": MAX_CANDIDATES,
                        "require_all": False,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30,
                )
            if response.status_code == 200:
                raw = response.json().get("results") or []
                if isinstance(raw, list):
                    candidates = [candidate_from_result(row) for row in raw[:MAX_CANDIDATES]]
        except Exception as exc:
            logger.debug("WA soft search retry skipped: %s", exc)

    state = {
        "type": FLOW_TYPE,
        "state": "candidates" if candidates else "idle",
        "country": country,
        "query": query,
        "candidates": candidates,
    }
    _save_state(platform_id, state, last_query=query, last_country=country)
    return format_candidates_message(query, candidates, country)


async def handle_standard_turn(
    platform_id: str,
    message: str,
    *,
    token: str | None,
    market_api_url: str,
    search_fn: SearchFn | None = None,
    intel_fn: IntelFn | None = None,
    basket_fn: BasketFn | None = None,
) -> str:
    """Process one user turn and return the WhatsApp reply body (markdown-ish *bold*)."""
    raw = (message or "").strip()
    msg = _normalize_msg(raw)
    state = _load_state(platform_id)
    country = _guess_country(raw) if raw else (state.get("country") or DEFAULT_COUNTRY)
    kind = classify_specificity(msg)

    if kind in {"greeting", "help", "reset"}:
        _clear_state(platform_id, country)
        return build_welcome_message()

    if kind == "back":
        _clear_state(platform_id, country)
        return "Listo, volvemos al inicio.\n\n" + build_welcome_message()

    # Multi-line (or ';'-separated) basket — must run before normalize loses structure.
    # Also: lone "canasta"/"cotizar" shows the list template.
    if msg in _BASKET_HELP and parse_basket_items(raw) is None:
        return build_basket_help_message()
    if parse_basket_items(raw) is not None:
        return await process_basket_list(
            platform_id,
            raw,
            token=token,
            market_api_url=market_api_url,
            basket_fn=basket_fn,
        )

    # Active clarify step
    if state.get("state") == "clarify" and state.get("clarify_options"):
        family = str(state.get("family") or "")
        options = list(state.get("clarify_options") or [])
        if is_clarify_other_choice(msg, options):
            state["state"] = "await_free_text"
            _save_state(platform_id, state, last_country=country)
            return (
                f"Dale. Escribí *{family}* con marca o presentación "
                f"(ej. `{family} Primor 1L`)."
            )
        refined = resolve_clarify_choice(msg, family, options)
        if refined:
            return await _run_search_and_format(
                platform_id, refined, country, token, market_api_url, search_fn
            )
        if kind == "pick":
            return "Opción fuera de rango. Elegí un número de la lista o escribí marca y tamaño."

    if state.get("state") == "await_free_text":
        family = str(state.get("family") or "")
        query = msg if not family or family in msg else f"{family} {msg}"
        return await _run_search_and_format(
            platform_id, query.strip(), country, token, market_api_url, search_fn
        )

    # Pick store after basket compare
    if kind == "pick" and state.get("state") == "basket_stores":
        stores = list(state.get("stores") or [])
        idx = int(msg) - 1
        if 0 <= idx < len(stores):
            state["state"] = "basket_detail"
            state["selected_store"] = idx
            _save_state(platform_id, state, last_country=country)
            return format_basket_store_detail(stores[idx])
        return f"Elegí un número entre 1 y {len(stores)}." if stores else build_basket_help_message()

    # Pick from last single-product candidates
    if kind == "pick" and state.get("state") == "candidates":
        candidates = list(state.get("candidates") or [])
        idx = int(msg) - 1
        if 0 <= idx < len(candidates):
            chosen = candidates[idx]
            state["state"] = "detail"
            state["selected"] = idx
            _save_state(platform_id, state, last_query=state.get("query"), last_country=country)
            return format_detail_message(chosen)
        return f"Elegí un número entre 1 y {len(candidates)}." if candidates else build_welcome_message()

    if kind == "vague":
        tokens = msg.split()
        family = tokens[0] if tokens else msg
        options = _FAMILY_CLARIFY.get(family) or [
            "Con marca",
            "Sin marca / genérico",
            "Otra presentación",
            "Otro (escribí)",
        ]
        new_state = {
            "type": FLOW_TYPE,
            "state": "clarify",
            "country": country,
            "family": family,
            "clarify_options": options,
            "candidates": [],
        }
        _save_state(platform_id, new_state, last_query=msg, last_country=country)
        return build_clarify_message(family, options)

    if kind == "intel":
        prior = state.get("query")
        question = build_intel_question(raw, prior=prior)
        if intel_fn is None:

            async def _intel(q: str, t: str | None) -> str:
                return await default_ask_intel(q, t, market_api_url)

            intel_fn = _intel
        answer = await intel_fn(question, token)
        _save_state(
            platform_id,
            {
                "type": FLOW_TYPE,
                "state": "idle",
                "country": country,
                "query": raw[:200],
                "candidates": [],
            },
            last_query=raw[:200],
            last_country=country,
        )
        return answer

    # medium / specific / fallback → catalog search
    return await _run_search_and_format(
        platform_id, raw, country, token, market_api_url, search_fn
    )
