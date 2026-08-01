import os
import re
import json
import secrets
import logging
import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response
from market_core import check_rate_limit_sqlite
from server_deps import claim_messenger_update, get_messenger_session, update_messenger_session

router = APIRouter(prefix="/v1/integrations/telegram", tags=["integrations"])
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# Must match the secret_token passed to Telegram's setWebhook call. Telegram
# echoes it back on every webhook POST as X-Telegram-Bot-Api-Secret-Token;
# without checking it, anyone can POST a forged update body.
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

# Per-chat cap so a single (secret-token-authenticated) chat can't run up
# paid LLM costs by hammering the webhook.
TELEGRAM_RATE_LIMIT_MIN = int(os.getenv("TELEGRAM_RATE_LIMIT_MIN", "20"))
TELEGRAM_RATE_LIMIT_WINDOW = int(os.getenv("TELEGRAM_RATE_LIMIT_WINDOW", "60"))
TELEGRAM_RATE_LIMIT_DAY = int(os.getenv("TELEGRAM_RATE_LIMIT_DAY", "300"))
TELEGRAM_GLOBAL_RATE_LIMIT_DAY = int(os.getenv("TELEGRAM_GLOBAL_RATE_LIMIT_DAY", "1000"))
_TELEGRAM_MESSAGE_LIMIT = 3900
_SEARCH_MODE_CONTEXT = "telegram_mode:search"
_BASKET_INPUT_CONTEXT_TYPE = "basket_input"
_BASKET_CANDIDATES_CONTEXT_TYPE = "basket_candidates"


def _parse_chat_id_set(raw: str) -> set[str]:
    return {part.strip() for part in (raw or "").split(",") if part.strip()}


# Closed pilot by default. Set TELEGRAM_PUBLIC_MODE=true only after the
# activation gate in the PRD is approved. Admin chats may use MARKET_API_TOKEN;
# everyone else must use the dedicated bot-scoped key (never fall back to the
# platform admin token).
TELEGRAM_ALLOWED_CHAT_IDS = _parse_chat_id_set(os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", ""))
TELEGRAM_ADMIN_CHAT_IDS = _parse_chat_id_set(os.getenv("TELEGRAM_ADMIN_CHAT_IDS", ""))
TELEGRAM_PUBLIC_MODE = os.getenv("TELEGRAM_PUBLIC_MODE", "").strip().lower() in {"1", "true", "yes"}

_DENIED_BODY = (
    "Este chat no está autorizado para usar el bot de CLI Market. "
    "Si necesitas acceso, solicítalo al administrador."
)

_GROUPS_DISABLED_BODY = (
    "Por ahora las cotizaciones funcionan en chat privado para proteger tu lista y tus datos. "
    "Abrí el bot y escríbeme /cotizar."
)
_RATE_LIMIT_BODY = "Has llegado al límite temporal de consultas. Inténtalo nuevamente en un momento."

_COMMANDS = [
    {"command": "cotizar", "description": "Cotiza una canasta de productos"},
    {"command": "buscar", "description": "Consulta el precio de un producto"},
    {"command": "ayuda", "description": "Ver ejemplos y límites"},
]


def _session_key(chat_id: str, user_id: str | None) -> str:
    """Keep Telegram state separate from other messenger integrations."""
    return f"telegram:{user_id or chat_id}"


def _initial_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "🧾 Nueva cotización", "callback_data": "flow:quote"}],
            [{"text": "🔎 Buscar un producto", "callback_data": "flow:search"},
             {"text": "❓ Ayuda", "callback_data": "flow:help"}],
        ]
    }


def _segment_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "🍽️ Alimentos / HORECA", "callback_data": "seg:horeca"}],
            [{"text": "🧹 Limpieza y MRO", "callback_data": "seg:mro"}],
            [{"text": "🛠️ Obra menor", "callback_data": "seg:obra"},
             {"text": "📦 Otra canasta", "callback_data": "seg:general"}],
        ]
    }


def _force_reply(placeholder: str) -> dict:
    return {"force_reply": True, "input_field_placeholder": placeholder}


def _basket_input_context(segment: str) -> str:
    return json.dumps(
        {"type": _BASKET_INPUT_CONTEXT_TYPE, "segment": segment},
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _check_telegram_rate_limit(identity: str) -> None:
    """Apply both per-user and deployment-wide cost caps before LLM work."""
    check_rate_limit_sqlite(
        f"telegram:{identity}",
        window_secs=TELEGRAM_RATE_LIMIT_WINDOW,
        max_req=TELEGRAM_RATE_LIMIT_MIN,
        daily_max=TELEGRAM_RATE_LIMIT_DAY,
    )
    check_rate_limit_sqlite(
        "telegram:global",
        window_secs=86400,
        max_req=TELEGRAM_GLOBAL_RATE_LIMIT_DAY,
        daily_max=TELEGRAM_GLOBAL_RATE_LIMIT_DAY,
    )


def _help_text() -> str:
    return (
        "<b>Cómo cotizar con CLI Market</b>\n\n"
        "1. Escribe marca, presentación y cantidad.\n"
        "2. Si aceptas sustitutos, indícalo.\n"
        "3. Te mostraré precios observados y sus límites de cobertura.\n\n"
        "Ejemplo: <i>12 latas de leche Gloria 390 g y 4 paquetes de papel toalla</i>.\n\n"
        "No realizo compras, pagos ni cotizaciones contractuales con flete o crédito."
    )

_COUNTRY_HINTS = {
    "peru": "PE", "perú": "PE",
    "colombia": "CO",
    "mexico": "MX", "méxico": "MX",
    "argentina": "AR",
    "chile": "CL",
    "brasil": "BR", "brazil": "BR",
}


def _esc(text: str) -> str:
    """Escape text interpolated into an HTML parse_mode Telegram message.
    Telegram's HTML parser only reserves & < > (unlike MarkdownV2's ~20
    punctuation chars) — but first_name (user-controlled) and answer
    (LLM-generated) are never under our control, and an unescaped & < > in
    either breaks the parser (Telegram returns 400, silently swallowed by
    _send_telegram's bare except) or lets the sender/LLM inject fake <b>/<i>
    formatting. Same fix procure-telegram-bot's src/lib/format.ts already
    applied for the same reason — ported here since it never was."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_TELEGRAM_FORMAT_TAG_RE = re.compile(r"</?(?:b|i)>")


def _markdown_bold_to_html(text: str) -> str:
    """ask_intel's answers are written in Markdown (**bold**), but Telegram
    messages are sent with parse_mode: "HTML" — the two don't mix, so users
    were seeing literal asterisks instead of bold text (reported live
    2026-07-20). Must run AFTER _esc() escapes & < > — ** itself isn't
    affected by that escaping, and text captured between markers can't
    contain raw < > to reintroduce after the fact."""
    return _MD_BOLD_RE.sub(r"<b>\1</b>", text)


def _split_telegram_text(text: str, limit: int = _TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    """Split long replies below Telegram's 4096-character ceiling.

    If a reply needs splitting, formatting tags are deliberately removed first.
    This keeps every chunk valid HTML instead of risking an unclosed tag or a
    malformed entity midway through a message.
    """
    if len(text) <= limit:
        return [text]

    plain = _TELEGRAM_FORMAT_TAG_RE.sub("", text)
    chunks: list[str] = []
    remaining = plain
    while len(remaining) > limit:
        split_at = max(remaining.rfind("\n", 0, limit + 1), remaining.rfind(" ", 0, limit + 1))
        if split_at <= 0:
            split_at = limit
            dangling_entity = remaining.rfind("&", 0, split_at)
            if dangling_entity > 0 and ";" not in remaining[dangling_entity:split_at]:
                split_at = dangling_entity
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


def _guess_country(text: str) -> str:
    """Best-effort country code from free text, defaulting to PE (primary
    market) — used only to re-run a button-triggered follow-up query, not
    for anything user-facing."""
    lowered = text.lower()
    for name, code in _COUNTRY_HINTS.items():
        if name in lowered:
            return code
    return "PE"


def _is_valid_telegram_secret(request: Request) -> bool:
    if not TELEGRAM_WEBHOOK_SECRET:
        return False
    return secrets.compare_digest(
        request.headers.get("x-telegram-bot-api-secret-token", ""),
        TELEGRAM_WEBHOOK_SECRET,
    )


def _is_chat_allowed(chat_id: str) -> bool:
    """Allow only pilot chats unless the approved public mode is enabled."""
    return TELEGRAM_PUBLIC_MODE or chat_id in TELEGRAM_ALLOWED_CHAT_IDS


def _bot_token_for_chat(chat_id: str) -> str | None:
    """Resolve API token for a Telegram chat.

    Public bot traffic must use MARKET_BOT_API_TOKEN only — never the platform
    admin MARKET_API_TOKEN, which bypasses tier/rate limits on /v1/intel/ask.
    """
    if chat_id in TELEGRAM_ADMIN_CHAT_IDS:
        return os.getenv("MARKET_API_TOKEN") or os.getenv("MARKET_BOT_API_TOKEN")
    return os.getenv("MARKET_BOT_API_TOKEN") or None


def _follow_up_keyboard() -> dict:
    """Inline keyboard attached to a real product-search answer. Each button
    carries only the action code — the product/country context is read back
    from messenger_sessions by chat_id, not from callback_data (Telegram
    caps callback_data at 64 bytes, too tight for arbitrary product names).

    Only "cmp" (compare stores) ships: it's backed by real search_products
    data. "trend"/"alert" were dropped (reported live 2026-07-20) — with no
    real forecasting or persistent-alert backend wired to Telegram, both
    just re-asked the LLM a one-off question dressed up as a monitoring
    feature that doesn't exist. See routers/alerts.py for the real
    account-scoped alert system this would need to hook into properly."""
    return {
        "inline_keyboard": [
            [{"text": "🔄 Comparar tiendas", "callback_data": "cmp"}],
        ]
    }


async def _telegram_api(method: str, payload: dict) -> httpx.Response | None:
    if not TELEGRAM_TOKEN:
        return None
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}",
                json=payload,
            )
            if response.status_code != 200:
                logger.warning("Telegram %s returned %s", method, response.status_code)
            return response
    except Exception as e:
        logger.warning("Telegram API error (%s): %s", method, e)
        return None


async def register_telegram_commands() -> None:
    """Register the short private-chat command menu at application startup."""
    if not TELEGRAM_TOKEN:
        return
    response = await _telegram_api(
        "setMyCommands",
        {"commands": _COMMANDS, "scope": {"type": "all_private_chats"}, "language_code": "es"},
    )
    if response is None or response.status_code != 200:
        logger.warning("Telegram command menu was not registered")


async def _send_telegram(chat_id: str, text: str, reply_markup: dict | None = None) -> str | None:
    """Send a message; returns its message_id (for later editing) or None."""
    first_message_id: str | None = None
    chunks = _split_telegram_text(text)
    for index, chunk in enumerate(chunks):
        payload = {"chat_id": chat_id, "text": chunk, "parse_mode": "HTML"}
        if reply_markup and index == len(chunks) - 1:
            payload["reply_markup"] = reply_markup
        r = await _telegram_api("sendMessage", payload)
        if r is None or r.status_code != 200:
            continue
        if first_message_id is None:
            try:
                first_message_id = str(r.json()["result"]["message_id"])
            except Exception:
                pass
    return first_message_id


async def _edit_telegram(chat_id: str, message_id: str, text: str, reply_markup: dict | None = None) -> bool:
    chunks = _split_telegram_text(text)
    payload = {"chat_id": chat_id, "message_id": message_id, "text": chunks[0], "parse_mode": "HTML"}
    if reply_markup and len(chunks) == 1:
        payload["reply_markup"] = reply_markup
    r = await _telegram_api("editMessageText", payload)
    if not r or r.status_code != 200:
        return False
    for index, chunk in enumerate(chunks[1:], start=1):
        await _send_telegram(chat_id, chunk, reply_markup if index == len(chunks) - 1 else None)
    return True


async def _send_typing(chat_id: str) -> None:
    await _telegram_api("sendChatAction", {"chat_id": chat_id, "action": "typing"})


async def _answer_callback_query(callback_query_id: str, text: str | None = None) -> None:
    """Mandatory: Telegram leaves the button showing a loading spinner on the
    sender's client until this is called, regardless of what else we do."""
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    await _telegram_api("answerCallbackQuery", payload)


async def _ask_intel(question: str, token: str | None) -> str:
    """Call /v1/intel/ask and return the answer text, or a fallback message."""
    if not token:
        return "El bot no está configurado para consultar precios ahora."
    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                f"{market_api_url}/v1/intel/ask",
                json={"question": question},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            if response.status_code == 200:
                return _markdown_bold_to_html(_esc(response.json().get("answer", "")))
            logger.warning("/v1/intel/ask returned %s: %s", response.status_code, response.text[:200])
    except Exception as e:
        logger.warning("Telegram intelligence request failed: %s", e)
    return "No pude consultar los precios ahora. Inténtalo nuevamente en un momento."


def _candidate_from_result(result: dict) -> dict:
    """Keep only the fields that are actually returned by /products/search."""
    return {
        "id": str(result.get("id") or "")[:120],
        "name": str(result.get("name") or "Producto sin nombre")[:240],
        "brand": str(result.get("brand") or "")[:120],
        "price": result.get("price"),
        "currency": str(result.get("currency") or "")[:12],
        "store_name": str(result.get("store_name") or result.get("store") or "Tienda sin identificar")[:120],
        "stock": result.get("stock"),
        "confidence": result.get("confidence"),
        "canonical_product_id": str(result.get("canonical_product_id") or "")[:160],
        "observed_at": str(result.get("queried_at") or "")[:80],
    }


def _candidate_button_label(candidate: dict, index: int) -> str:
    name = candidate["name"]
    if len(name) > 42:
        name = f"{name[:39]}..."
    return f"{index + 1}. {name}"


def _candidate_keyboard(candidates: list[dict]) -> dict:
    return {
        "inline_keyboard": [
            [{"text": _candidate_button_label(candidate, index), "callback_data": f"pick:{index}"}]
            for index, candidate in enumerate(candidates)
        ] + [[{"text": "🔎 Buscar otro producto", "callback_data": "flow:search"}]],
    }


def _price_label(candidate: dict) -> str:
    price = candidate.get("price")
    if price is None or price == "":
        return "Sin precio registrado"
    currency = candidate.get("currency", "")
    prefix = {"PEN": "S/", "USD": "US$"}.get(currency.upper(), currency)
    return f"{_esc(prefix)} {_esc(str(price))}".strip()


def _format_search_candidates(query: str, results: list[dict]) -> tuple[str, dict]:
    candidates = [_candidate_from_result(row) for row in results[:3]]
    if not candidates:
        return (
            "No encontré una coincidencia suficientemente específica. "
            "Prueba incluyendo marca y presentación, por ejemplo: <i>café Altomayo clásico 180 g</i>.",
            _initial_keyboard(),
        )
    return (
        f"<b>Resultados para {_esc(query)}</b>\n\n"
        "Elige una oferta para ver su ficha. No compararé opciones ni declararé una más barata hasta confirmar que son equivalentes.\n\n"
        f"Encontré {len(candidates)} coincidencia{'s' if len(candidates) != 1 else ''} del catálogo.",
        _candidate_keyboard(candidates),
    )


def _format_candidate_detail(candidate: dict) -> str:
    def field(value: object, fallback: str = "Sin dato") -> str:
        return _esc(str(value)) if value not in (None, "") else fallback

    return (
        "<b>Oferta observada</b>\n\n"
        f"Producto: <b>{field(candidate.get('name'))}</b>\n"
        f"Marca: {field(candidate.get('brand'))}\n"
        f"Tienda: {field(candidate.get('store_name'))}\n"
        f"Precio observado: <b>{_price_label(candidate)}</b>\n"
        f"Stock reportado: {field(candidate.get('stock'))}\n"
        f"Confianza del registro: {field(candidate.get('confidence'))}\n\n"
        f"Identidad canónica: {'registrada' if candidate.get('canonical_product_id') else 'pendiente'}\n"
        f"Última observación: {field(candidate.get('observed_at'))}\n\n"
        "Verifica disponibilidad, equivalencia y condiciones comerciales antes de comprar."
    )


async def _search_catalog(query: str, token: str | None, country: str) -> list[dict] | None:
    """Query the authenticated product-search endpoint without LLM synthesis."""
    if not token:
        return None
    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                f"{market_api_url}/products/search",
                json={"query": query, "country": country, "limit": 3, "require_all": True},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
        if response.status_code == 200:
            payload = response.json()
            results = payload.get("results", [])
            return results if isinstance(results, list) else []
        logger.warning("/products/search returned %s: %s", response.status_code, response.text[:200])
    except Exception as exc:
        logger.warning("Telegram catalog search failed: %s", exc)
    return None


async def _process_catalog_search(chat_id: str, session_id: str, query: str, token: str | None) -> tuple[str, dict]:
    country = _guess_country(query)
    results = await _search_catalog(query, token, country)
    if results is None:
        return "No pude consultar el catálogo ahora. Inténtalo nuevamente en un momento.", _initial_keyboard()
    answer, keyboard = _format_search_candidates(query, results)
    candidates = [_candidate_from_result(row) for row in results[:3]]
    context = json.dumps(
        {"type": "catalog_candidates", "query": query, "country": country, "candidates": candidates},
        ensure_ascii=False,
        separators=(",", ":"),
    ) if candidates else _SEARCH_MODE_CONTEXT
    update_messenger_session(session_id, context=context, last_query=query, last_country=country)
    return answer, keyboard


def _parse_basket_items(text: str) -> list[dict] | None:
    """Parse a deliberately simple, auditable one-item-per-line basket input."""
    raw_lines = [line.strip(" -•\t") for line in re.split(r"[\n;]+", text) if line.strip(" -•\t")]
    if len(raw_lines) < 2 or len(raw_lines) > 20:
        return None
    items: list[dict] = []
    for line in raw_lines:
        match = re.match(r"^(?:(\d{1,4})\s*(?:x|unidades?|unds?|u)?\s+)?(.+?)$", line, flags=re.IGNORECASE)
        if not match:
            return None
        name = match.group(2).strip()
        if not name or len(name) > 200:
            return None
        items.append({"name": name, "qty": int(match.group(1) or 1)})
    return items


async def _compare_basket(items: list[dict], token: str | None, country: str) -> tuple[dict | None, int | None]:
    """Call the basket endpoint as raw data; no LLM ranks or rewrites it."""
    if not token:
        return None, None
    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                f"{market_api_url}/v1/basket/compare",
                json={"items": items, "country": country, "enveloped": False},
                headers={"Authorization": f"Bearer {token}"},
                timeout=35,
            )
        if response.status_code == 200:
            payload = response.json()
            return (payload if isinstance(payload, dict) else None), response.status_code
        logger.warning("/v1/basket/compare returned %s: %s", response.status_code, response.text[:200])
        return None, response.status_code
    except Exception as exc:
        logger.warning("Telegram basket comparison failed: %s", exc)
        return None, None


def _basket_store_from_result(store: dict) -> dict:
    breakdown = []
    for row in store.get("breakdown", [])[:20]:
        if not isinstance(row, dict):
            continue
        breakdown.append({
            "item": str(row.get("item") or "")[:200],
            "resolved_name": str(row.get("resolved_name") or "")[:240],
            "brand": str(row.get("brand") or "")[:120],
            "qty": row.get("qty"),
            "unit_price": row.get("unit_price"),
            "item_total": row.get("item_total"),
            "product_id": str(row.get("product_id") or "")[:120],
            "canonical_product_id": str(row.get("canonical_product_id") or "")[:160],
            "observed_at": str(row.get("observed_at") or "")[:80],
            "stock": row.get("stock"),
            "match_confidence": str(row.get("match_confidence") or "")[:20],
        })
    return {
        "store": str(store.get("store") or "")[:80],
        "store_name": str(store.get("store_name") or "Tienda sin identificar")[:120],
        "currency": str(store.get("currency") or "")[:12],
        "total": store.get("total"),
        "items_found": store.get("items_found"),
        "data_freshness": str(store.get("data_freshness") or "")[:20],
        "data_age_hours": store.get("data_age_hours"),
        "breakdown": breakdown,
    }


def _basket_review_keyboard(stores: list[dict]) -> dict:
    return {
        "inline_keyboard": [
            [{"text": f"Revisar {store['store_name']}", "callback_data": f"basket:{index}"}]
            for index, store in enumerate(stores)
        ] + [[{"text": "🧾 Nueva cotización", "callback_data": "flow:quote"}]],
    }


def _format_basket_options(items_searched: int, stores: list[dict]) -> tuple[str, dict]:
    return (
        f"<b>Canasta con cobertura completa</b>\n\n"
        f"Los {items_searched} productos tuvieron coincidencia en {len(stores)} tienda{'s' if len(stores) != 1 else ''}. "
        "Revisa producto, marca y presentación por tienda antes de usar un total. "
        "No recomendaré una tienda ni calcularé ahorro en esta etapa.",
        _basket_review_keyboard(stores),
    )


def _format_basket_store_detail(store: dict) -> str:
    currency = store.get("currency") or ""
    currency_label = {"PEN": "S/", "USD": "US$"}.get(str(currency).upper(), str(currency))
    lines = [
        f"<b>Revisión de { _esc(str(store.get('store_name') or 'tienda')) }</b>",
        "",
        "Coincidencias encontradas:",
    ]
    for row in store.get("breakdown", []):
        requested = _esc(str(row.get("item") or "Sin dato"))
        resolved = _esc(str(row.get("resolved_name") or "Sin dato"))
        brand = _esc(str(row.get("brand") or "Sin marca"))
        qty = _esc(str(row.get("qty") or 1))
        unit_price = _esc(str(row.get("unit_price") or "Sin dato"))
        canonical = "registrada" if row.get("canonical_product_id") else "pendiente"
        match_confidence = _esc(str(row.get("match_confidence") or "Sin dato"))
        observed_at = row.get("observed_at")
        observation = f" · observado: {_esc(str(observed_at))}" if observed_at else ""
        lines.append(
            f"• {qty} × {requested}\n"
            f"  → {resolved} · {brand} · {currency_label} {unit_price}\n"
            f"  Identidad canónica: {canonical} · Coincidencia: {match_confidence}{observation}"
        )
    freshness = store.get("data_freshness")
    if freshness:
        age = store.get("data_age_hours")
        age_label = f" · { _esc(str(age)) } h" if age is not None else ""
        lines.append(f"\nFrescura del dato: {_esc(str(freshness))}{age_label}")
    lines.extend([
        "",
        f"Total observado: <b>{_esc(currency_label)} {_esc(str(store.get('total') or 'Sin dato'))}</b>",
        "",
        "Este total es exploratorio: confirma que cada coincidencia tiene la marca y presentación que necesitas. No es una cotización contractual ni una recomendación de compra.",
    ])
    return "\n".join(lines)


async def _process_basket_input(chat_id: str, session_id: str, incoming_msg: str, token: str | None) -> tuple[str, dict]:
    items = _parse_basket_items(incoming_msg)
    if items is None:
        return (
            "Para cotizar una canasta, envía entre 2 y 20 productos, una línea por producto. "
            "Puedes indicar cantidad al inicio.\n\n"
            "Ejemplo:\n12 x leche Gloria 390 g\n4 arroz extra 5 kg",
            _force_reply("Una línea por producto"),
        )
    country = _guess_country(incoming_msg)
    result, status_code = await _compare_basket(items, token, country)
    if status_code == 403:
        return "La comparación de canastas no está habilitada para este acceso. Puedes usar /buscar para consultar un producto.", _initial_keyboard()
    if result is None:
        return "No pude verificar la canasta ahora. Inténtalo nuevamente en un momento.", _initial_keyboard()

    items_searched = int(result.get("items_searched") or len(items))
    items_found = int(result.get("items_found") or 0)
    if items_found != items_searched:
        update_messenger_session(session_id, context=_basket_input_context("Canasta"))
        return (
            f"No puedo cerrar esta cotización: encontré {items_found} de {items_searched} productos. "
            "No mostraré total, ahorro ni tienda recomendada mientras falte cobertura. "
            "Reenvía la canasta con marca y presentación más específicas.",
            _force_reply("Ej.: 12 x leche Gloria 390 g"),
        )

    full_stores = [
        _basket_store_from_result(store)
        for store in result.get("stores", [])
        if isinstance(store, dict) and int(store.get("items_found") or 0) == items_searched
    ]
    if not full_stores:
        update_messenger_session(session_id, context=_basket_input_context("Canasta"))
        return (
            "Encontré los productos, pero ninguna tienda cubre la canasta completa. "
            "No mostraré total ni una tienda recomendada. Ajusta marca, presentación o separa la compra.",
            _force_reply("Una línea por producto"),
        )

    verified_stores = [
        store for store in full_stores
        if all(
            row.get("canonical_product_id") and row.get("match_confidence") == "high"
            for row in store.get("breakdown", [])
        )
    ][:3]
    if not verified_stores:
        update_messenger_session(session_id, context=_basket_input_context("Canasta"))
        return (
            "Encontré una canasta completa, pero no puedo verificar con suficiente certeza la identidad de cada producto. "
            "No mostraré total ni una tienda recomendada. Reenvía marca y presentación exactas por cada línea.",
            _force_reply("Ej.: 12 x leche Gloria 390 g"),
        )

    context = json.dumps(
        {
            "type": _BASKET_CANDIDATES_CONTEXT_TYPE,
            "country": country,
            "items_searched": items_searched,
            "stores": verified_stores,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    update_messenger_session(session_id, context=context, last_query=incoming_msg, last_country=country)
    return _format_basket_options(items_searched, verified_stores)


async def _process_message(
    chat_id: str, user_id: str | None, message_id: str | None, incoming_msg: str, first_name: str
) -> None:
    """Process a private-chat message after the webhook has been acknowledged."""
    token = _bot_token_for_chat(chat_id)
    session_id = _session_key(chat_id, user_id)
    command, _, command_arg = incoming_msg.partition(" ")
    command = command.lower()

    if command == "/start" or incoming_msg.lower() in ("hola", "hi", "hello"):
        deep_link = command_arg.strip().lower()
        segments = {"horeca": "Alimentos / HORECA", "mro": "Limpieza y MRO", "obra_menor": "Obra menor"}
        if deep_link in segments:
            segment = segments[deep_link]
            update_messenger_session(session_id, context=_basket_input_context(segment))
            answer = f"Hola <b>{_esc(first_name)}</b>. Elegiste <b>{segment}</b>.\n\nEscribe tu lista con marca, presentación y cantidad."
            keyboard = _force_reply("Ej.: 12 latas de leche Gloria 390 g")
        else:
            answer = (
                f"Hola <b>{_esc(first_name)}</b>.\n\n"
                "Soy el bot de <b>CLI Market</b>. Te ayudo a consultar precios observados y a preparar una canasta de compra.\n\n"
                "Para una comparación útil, incluye marca, presentación y cantidad."
            )
            keyboard = _initial_keyboard()
    elif command == "/ayuda":
        answer, keyboard = _help_text(), _initial_keyboard()
    elif command == "/cotizar":
        answer, keyboard = "¿Qué tipo de compra quieres cotizar? Esto solo ajusta las preguntas que te haré.", _segment_keyboard()
    elif command == "/buscar":
        search_query = command_arg.strip()
        if search_query:
            answer, keyboard = await _process_catalog_search(chat_id, session_id, search_query, token)
        else:
            update_messenger_session(session_id, context=_SEARCH_MODE_CONTEXT)
            answer, keyboard = "Escribe el producto con marca y presentación, si la conoces.", _force_reply("Ej.: café Altomayo clásico 180 g")
    else:
        session = get_messenger_session(session_id)
        context = session.get("last_context")
        if context == _SEARCH_MODE_CONTEXT:
            answer, keyboard = await _process_catalog_search(chat_id, session_id, incoming_msg, token)
        else:
            try:
                context_payload = json.loads(context or "{}")
            except (TypeError, json.JSONDecodeError):
                context_payload = {}
            if context_payload.get("type") == _BASKET_INPUT_CONTEXT_TYPE:
                answer, keyboard = await _process_basket_input(chat_id, session_id, incoming_msg, token)
            else:
                effective_query = (
                    "Responde únicamente con datos verificables de CLI Market. Si falta marca, presentación, retailer, cobertura o equivalencia, pide aclaración. "
                    "No declares ahorro, mejor tienda, alertas ni cotización contractual con datos incompletos.\n"
                    f"Contexto: {context}\nConsulta: {incoming_msg}"
                    if context else incoming_msg
                )
                answer = await _ask_intel(effective_query, token)
                keyboard = _initial_keyboard()
                update_messenger_session(
                    session_id,
                    context=f"Consulta: {incoming_msg} | Respuesta: {answer[:100]}...",
                    last_query=incoming_msg,
                    last_country=_guess_country(incoming_msg),
                )

    if message_id:
        if not await _edit_telegram(chat_id, message_id, answer, keyboard):
            await _send_telegram(chat_id, answer, keyboard)
    else:
        await _send_telegram(chat_id, answer, keyboard)


async def _process_incoming_message(chat_id: str, user_id: str | None, text: str, first_name: str) -> None:
    """Send progress only after Telegram has received the webhook acknowledgement."""
    await _send_typing(chat_id)
    placeholder_id = await _send_telegram(chat_id, "🔍 Buscando...")
    await _process_message(chat_id, user_id, placeholder_id, text, first_name)


_BUTTON_QUESTIONS = {
    "cmp": lambda q, c: f"Compara precios de {q} en {c} entre tiendas",
}


async def _process_callback(chat_id: str, user_id: str | None, message_id: str, action: str) -> None:
    """Handle only short opaque callback actions owned by the current user."""
    session_id = _session_key(chat_id, user_id)
    if action == "flow:quote":
        await _send_telegram(chat_id, "¿Qué tipo de compra quieres cotizar?", _segment_keyboard())
        return
    if action == "flow:search":
        update_messenger_session(session_id, context=_SEARCH_MODE_CONTEXT)
        await _send_telegram(chat_id, "Escribe el producto con marca y presentación, si la conoces.", _force_reply("Ej.: café Altomayo clásico 180 g"))
        return
    if action == "flow:help":
        await _send_telegram(chat_id, _help_text(), _initial_keyboard())
        return
    if action.startswith("seg:"):
        segment = {
            "seg:horeca": "Alimentos / HORECA",
            "seg:mro": "Limpieza y MRO",
            "seg:obra": "Obra menor",
            "seg:general": "Canasta general",
        }.get(action)
        if segment:
            update_messenger_session(session_id, context=_basket_input_context(segment))
            await _send_telegram(
                chat_id,
                f"Perfecto: <b>{segment}</b>. Escribe tu lista con marca, presentación y cantidad.",
                _force_reply("Ej.: 12 latas de leche Gloria 390 g"),
            )
        return

    if action.startswith("pick:"):
        session = get_messenger_session(session_id)
        try:
            payload = json.loads(session.get("last_context") or "{}")
            index = int(action.split(":", 1)[1])
            candidates = payload.get("candidates", [])
            if payload.get("type") != "catalog_candidates" or not isinstance(candidates, list):
                raise ValueError("missing catalog candidates")
            candidate = candidates[index]
            if not isinstance(candidate, dict):
                raise ValueError("invalid candidate")
        except (AttributeError, ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError):
            await _send_telegram(
                chat_id,
                "Esa búsqueda ya expiró. Busca nuevamente el producto para confirmar la oferta.",
                _initial_keyboard(),
            )
            return
        await _send_telegram(chat_id, _format_candidate_detail(candidate), _initial_keyboard())
        return

    if action.startswith("basket:"):
        session = get_messenger_session(session_id)
        try:
            payload = json.loads(session.get("last_context") or "{}")
            index = int(action.split(":", 1)[1])
            stores = payload.get("stores", [])
            if payload.get("type") != _BASKET_CANDIDATES_CONTEXT_TYPE or not isinstance(stores, list):
                raise ValueError("missing basket candidates")
            store = stores[index]
            if not isinstance(store, dict):
                raise ValueError("invalid basket candidate")
        except (AttributeError, ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError):
            await _send_telegram(
                chat_id,
                "Esa cotización ya expiró. Envía nuevamente la canasta para revisar las coincidencias.",
                _initial_keyboard(),
            )
            return
        await _send_telegram(chat_id, _format_basket_store_detail(store), _initial_keyboard())
        return

    # Backward-compatible action for messages sent before this release.
    session = get_messenger_session(session_id)
    last_query = session.get("last_query")
    if not last_query:
        await _send_telegram(
            chat_id,
            "Esa búsqueda ya expiró. Escribe nuevamente el producto que quieres consultar.",
        )
        return

    country = session.get("last_country") or "PE"
    builder = _BUTTON_QUESTIONS.get(action)
    if not builder:
        return
    token = _bot_token_for_chat(chat_id)
    answer = await _ask_intel(builder(last_query, country), token)
    await _send_telegram(chat_id, answer, _initial_keyboard())


@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook endpoint for Telegram bot updates."""
    if not TELEGRAM_TOKEN:
        return {"status": "disabled", "hint": "Set TELEGRAM_BOT_TOKEN env var"}

    if not _is_valid_telegram_secret(request):
        logger.warning("Telegram webhook: invalid or missing secret token")
        return Response(content="invalid secret token", status_code=403)

    try:
        body = await request.json()
    except Exception:
        return {"status": "invalid_json"}

    update_id = body.get("update_id")
    if update_id is not None and not claim_messenger_update("telegram", update_id):
        return {"status": "duplicate"}

    callback_query = body.get("callback_query")
    if callback_query:
        chat = callback_query.get("message", {}).get("chat", {})
        chat_id = str(chat.get("id", ""))
        message_id = str(callback_query.get("message", {}).get("message_id", ""))
        user_id = str(callback_query.get("from", {}).get("id", "")) or None
        action = callback_query.get("data", "")
        callback_query_id = callback_query.get("id", "")

        if not chat_id or not message_id:
            return {"status": "no_message"}

        if not _is_chat_allowed(chat_id):
            logger.info("Telegram denied: chat is not on allowlist")
            background_tasks.add_task(_send_telegram, chat_id, _DENIED_BODY)
            return {"status": "denied"}

        if chat.get("type", "private") != "private":
            background_tasks.add_task(_send_telegram, chat_id, _GROUPS_DISABLED_BODY)
            return {"status": "private_chat_required"}

        # Ack button spinner first, then process in background.
        await _answer_callback_query(callback_query_id, "Procesando...")

        try:
            _check_telegram_rate_limit(user_id or chat_id)
        except HTTPException as exc:
            if exc.status_code != 429:
                raise
            background_tasks.add_task(_send_telegram, chat_id, _RATE_LIMIT_BODY)
            return {"status": "rate_limited"}

        background_tasks.add_task(_process_callback, chat_id, user_id, message_id, action)
        return {"status": "ok"}

    message = body.get("message") or {}
    if message:
        chat = message.get("chat", {})
        chat_id = str(chat.get("id", ""))
        user_id = str(message.get("from", {}).get("id", "")) or None
        text = (message.get("text") or "").strip()
        first_name = message.get("chat", {}).get("first_name") or message.get("from", {}).get("first_name") or ""

        if not chat_id:
            return {"status": "no_message"}

        if not _is_chat_allowed(chat_id):
            logger.info("Telegram denied: chat is not on allowlist")
            background_tasks.add_task(_send_telegram, chat_id, _DENIED_BODY)
            return {"status": "denied"}

        if chat.get("type", "private") != "private":
            background_tasks.add_task(_send_telegram, chat_id, _GROUPS_DISABLED_BODY)
            return {"status": "private_chat_required"}

        if not text:
            background_tasks.add_task(
                _send_telegram,
                chat_id,
                "Por ahora envíame tu producto o canasta en texto, con marca y presentación si la conoces.",
                _initial_keyboard(),
            )
            return {"status": "text_required"}

        try:
            _check_telegram_rate_limit(user_id or chat_id)
        except HTTPException as exc:
            if exc.status_code != 429:
                raise
            background_tasks.add_task(_send_telegram, chat_id, _RATE_LIMIT_BODY)
            return {"status": "rate_limited"}

        background_tasks.add_task(_process_incoming_message, chat_id, user_id, text, first_name)
        return {"status": "ok"}

    return {"status": "no_update"}


@router.get("/health")
async def telegram_health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "telegram_configured": bool(TELEGRAM_TOKEN),
        "webhook_secret_configured": bool(TELEGRAM_WEBHOOK_SECRET),
        "market_bot_token_configured": bool(os.getenv("MARKET_BOT_API_TOKEN")),
        "allowlist_configured": bool(TELEGRAM_ALLOWED_CHAT_IDS),
        "public_mode_enabled": TELEGRAM_PUBLIC_MODE,
    }
