"""Standard WhatsApp conversation funnel for product price queries.

Handles the common case where users start with a generic description
("aceite", "limpieza", "pollo") instead of a precise SKU. Flow:

  idle → (vague) clarify family → (medium/specific) catalog candidates
       → pick 1..N for offer detail
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
        "*También podés:*\n"
        "1️⃣ Escribir un producto (te muestro hasta 3 opciones)\n"
        "2️⃣ Preguntar comparación: `compara leche evaporada en Lima`\n"
        "3️⃣ Pedir tendencia: `¿va a subir el arroz?`\n\n"
        "Atajos: `menu` · `atras` · respondé *1/2/3* para elegir una opción.\n\n"
        "*Límites:* no compro ni pago; solo precios observados de tiendas que monitoreamos."
    )


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
) -> str:
    """Process one user turn and return the WhatsApp reply body (markdown-ish *bold*)."""
    msg = _normalize_msg(message)
    state = _load_state(platform_id)
    country = _guess_country(msg) if msg else (state.get("country") or DEFAULT_COUNTRY)
    kind = classify_specificity(msg)

    if kind in {"greeting", "help", "reset"}:
        _clear_state(platform_id, country)
        return build_welcome_message()

    if kind == "back":
        _clear_state(platform_id, country)
        return "Listo, volvemos al inicio.\n\n" + build_welcome_message()

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

    # Pick from last candidates
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
        question = build_intel_question(message.strip(), prior=prior)
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
                "query": message.strip()[:200],
                "candidates": [],
            },
            last_query=message.strip()[:200],
            last_country=country,
        )
        return answer

    # medium / specific / fallback → catalog search
    query = message.strip()
    return await _run_search_and_format(
        platform_id, query, country, token, market_api_url, search_fn
    )
