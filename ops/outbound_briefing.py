"""Daily outbound briefing — personalized retailer outreach messages → #outbound.

Maintains a target list with start dates and generates the correct message
for each target based on the day of their sequence (1, 3, 7, 10, 14).

Activation flow (no code edits needed):
  POST /admin/ops/activate-outbound-target  {"target_id": "tottus-pe", "start_date": "2026-06-14"}
  The API persists the date in the DB; this script fetches it at runtime.
  Falls back to start_date fields in TARGETS if the API is unreachable.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Target list ────────────────────────────────────────────────────────────────
# Add targets here as you add them to the sequence.
# start_date: when you sent the Day 1 LinkedIn DM.
# Set to None for targets not yet contacted (will appear as "PENDING Day 1").

TARGETS: list[dict] = [
    # ── Perú (Priority 1) ────────────────────────────────────────────────────
    {
        "id": "tottus-pe",
        "retailer": "Tottus",
        "country": "PE",
        "platform": "VTEX",
        "contact_name": "[Nombre]",
        "contact_role": "Gerente E-commerce",
        "linkedin_url": "https://www.linkedin.com/company/tottus-peru",
        "email": "[email]@tottus.com",
        "start_date": None,  # update when Day 1 sent: "2026-06-14"
        "hook": "Wong y Metro ya están indexados en CLI Market — cuando un agente de IA busca precios en Lima, aparecen ellos.",
        "competitors_indexed": ["Wong", "Metro", "Plaza Vea"],
    },
    {
        "id": "vivanda-pe",
        "retailer": "Vivanda",
        "country": "PE",
        "platform": "VTEX",
        "contact_name": "[Nombre]",
        "contact_role": "Gerente Digital",
        "linkedin_url": "https://www.linkedin.com/company/vivanda",
        "email": "[email]@vivanda.com.pe",
        "start_date": None,
        "hook": "Wong (mismo grupo Cencosud) ya está en el índice. Vivanda podría aparecer junto a él en búsquedas de IA.",
        "competitors_indexed": ["Wong", "Metro"],
    },
    {
        "id": "inkafarma-pe",
        "retailer": "Inkafarma",
        "country": "PE",
        "platform": "Propio",
        "contact_name": "[Nombre]",
        "contact_role": "Head Digital Commerce",
        "linkedin_url": "https://www.linkedin.com/company/inkafarma",
        "email": "[email]@inkafarma.pe",
        "start_date": None,
        "hook": "Los agentes de IA hacen 300-500 búsquedas de medicamentos/mes en Perú. Ninguna farmacia está indexada aún — primer mover gana.",
        "competitors_indexed": [],
    },
    {
        "id": "mifarma-pe",
        "retailer": "Mifarma",
        "country": "PE",
        "platform": "Propio",
        "contact_name": "[Nombre]",
        "contact_role": "Gerente E-commerce",
        "linkedin_url": "https://www.linkedin.com/company/mifarma",
        "email": "[email]@mifarma.pe",
        "start_date": None,
        "hook": "Si Inkafarma se indexa antes, aparece en todas las búsquedas de medicamentos de IA en Lima. Sin costo para Mifarma estar primero.",
        "competitors_indexed": [],
    },
    {
        "id": "sodimac-pe",
        "retailer": "Sodimac PE",
        "country": "PE",
        "platform": "VTEX",
        "contact_name": "[Nombre]",
        "contact_role": "E-commerce Manager",
        "linkedin_url": "https://www.linkedin.com/company/sodimac-peru",
        "email": "[email]@sodimac.com.pe",
        "start_date": None,
        "hook": "Promart ya está en el índice. Sodimac podría aparecer junto a él cuando los agentes buscan precios de hogar/ferretería en PE.",
        "competitors_indexed": ["Promart"],
    },
    # ── Colombia (Priority 2) ─────────────────────────────────────────────────
    {
        "id": "jumbo-co",
        "retailer": "Jumbo CO",
        "country": "CO",
        "platform": "VTEX",
        "contact_name": "[Nombre]",
        "contact_role": "E-commerce Manager",
        "linkedin_url": "https://www.linkedin.com/company/jumbo-colombia",
        "email": "[email]@cencosud.com.co",
        "start_date": None,
        "hook": "Éxito y Olímpica ya están en CLI Market. Cuando un agente busca precios en Bogotá, aparecen ellos — no Jumbo.",
        "competitors_indexed": ["Éxito", "Olímpica"],
    },
    {
        "id": "alkosto-co",
        "retailer": "Alkosto",
        "country": "CO",
        "platform": "VTEX",
        "contact_name": "[Nombre]",
        "contact_role": "Digital Director",
        "linkedin_url": "https://www.linkedin.com/company/alkosto",
        "email": "[email]@alkosto.com",
        "start_date": None,
        "hook": "En electro/hogar CO, Alkosto no tiene competidor indexado aún — primer mover en IA captura toda la demanda de agentes.",
        "competitors_indexed": [],
    },
    # ── México (Priority 3) ───────────────────────────────────────────────────
    {
        "id": "soriana-mx",
        "retailer": "Soriana",
        "country": "MX",
        "platform": "VTEX",
        "contact_name": "[Nombre]",
        "contact_role": "Gerente Digital",
        "linkedin_url": "https://www.linkedin.com/company/soriana",
        "email": "[email]@soriana.com",
        "start_date": None,
        "hook": "Chedraui y HEB ya están indexados en CLI Market MX. Soriana no aparece en búsquedas de IA en México.",
        "competitors_indexed": ["Chedraui", "HEB"],
    },
    {
        "id": "liverpool-mx",
        "retailer": "Liverpool",
        "country": "MX",
        "platform": "Magento",
        "contact_name": "[Nombre]",
        "contact_role": "Head of Digital",
        "linkedin_url": "https://www.linkedin.com/company/liverpool-mexico",
        "email": "[email]@liverpool.com.mx",
        "start_date": None,
        "hook": "Liverpool lidera moda/electro en MX pero no aparece en búsquedas de agentes de IA. Sin costo para cambiar eso.",
        "competitors_indexed": [],
    },
    # ── Chile (Priority 4) ────────────────────────────────────────────────────
    {
        "id": "jumbo-cl",
        "retailer": "Jumbo CL",
        "country": "CL",
        "platform": "VTEX",
        "contact_name": "[Nombre]",
        "contact_role": "Gerente E-commerce",
        "linkedin_url": "https://www.linkedin.com/company/jumbo-chile",
        "email": "[email]@cencosud.cl",
        "start_date": None,
        "hook": "Si ya tienes contacto en Cencosud CO por Jumbo Colombia, este es el mismo grupo — escalable.",
        "competitors_indexed": [],
    },
]

# Sequence schedule: day offset → action type
SEQUENCE_DAYS = {1: "linkedin", 3: "email", 7: "email_data", 10: "email_followup", 14: "breakup"}

# ── Message templates ──────────────────────────────────────────────────────────

def _msg_linkedin(t: dict) -> str:
    comps = ", ".join(t["competitors_indexed"]) if t["competitors_indexed"] else "otros retailers de tu categoría"
    return f"""📱 *LinkedIn DM — Día 1*
*Para:* {t["contact_name"]} · {t["contact_role"]} @ {t["retailer"]}
*LinkedIn:* {t["linkedin_url"]}

---
Hola [Nombre], vi que {t["retailer"]} tiene una operación digital sólida en {t["country"]}.

{t["hook"]}

CLI Market es el índice de precios para agentes de IA en LATAM — {comps} ya están indexados y aparecen en búsquedas de Claude, ChatGPT y otros agentes. La integración toma 30 segundos y es gratuita para retailers.

¿Tienes 15 minutos esta semana para mostrarte cómo funciona?

— Antonio · cli-market.dev/retailers
---"""


def _msg_email(t: dict) -> str:
    comps = ", ".join(t["competitors_indexed"]) if t["competitors_indexed"] else "retailers de tu categoría"
    subj_a = "Tus productos ya pueden aparecer en búsquedas de IA — sin costo"
    subj_b = f"{comps} {'ya están' if t['competitors_indexed'] else 'están'} en CLI Market. ¿Y {t['retailer']}?"
    return f"""📧 *Email — Día 3*
*Para:* {t["email"]}
*Asunto A:* {subj_a}
*Asunto B (FOMO):* {subj_b}

---
Hola [Nombre],

Te escribo porque {t["hook"]}

CLI Market indexa precios de {comps} y de 38 retailers en 8 países para que los agentes de IA puedan hacer comparaciones en tiempo real. Cuando un usuario le pregunta a Claude o ChatGPT "¿dónde compro más barato X en {t["country"]}?", consultan nuestro índice.

Para {t["retailer"]} el proceso es simple:
1. Generas un token de solo lectura en {t["platform"]} (sin acceso a pedidos ni clientes)
2. Lo ingresas en cli-market.dev/retailers
3. En 30 segundos tus productos aparecen en búsquedas de IA

Costo: $0. Gratis para siempre para retailers.

¿Puedo mostrarte cómo en 15 minutos?

Antonio Cuba
Founder, CLI Market · cli-market.dev
retailers@cli-market.dev
---"""


def _msg_email_data(t: dict) -> str:
    return f"""📧 *Email con dato — Día 7*
*Para:* {t["email"]}
*Asunto:* Dato: búsquedas de IA para productos de {t["retailer"]} esta semana

---
Hola [Nombre],

Esta semana hubo búsquedas de agentes de IA para productos de tu categoría en {t["country"]} — {t["competitors_indexed"][0] if t["competitors_indexed"] else "retailers que sí están indexados"} apareció en los resultados. {t["retailer"]} no.

La integración toma 30 segundos y es gratuita.

¿Damos el paso esta semana?

cli-market.dev/retailers
---"""


def _msg_breakup(t: dict) -> str:
    return f"""📧 *Breakup email — Día 14*
*Para:* {t["email"]}
*Asunto:* ¿Lo dejamos para Q3?

---
Hola [Nombre],

Entiendo que hay prioridades. Si el momento no es ahora, lo retomamos en Q3.

Si prefieres avanzar antes: cli-market.dev/retailers — 30 segundos, sin costo.

Éxitos,
Antonio · CLI Market
---"""


# ── Core logic ─────────────────────────────────────────────────────────────────

def _fetch_activations(api_url: str, api_token: str) -> dict[str, str]:
    """Fetch {target_id: start_date} from the API. Returns {} on any error."""
    try:
        import urllib.request
        req = urllib.request.Request(
            f"{api_url.rstrip('/')}/admin/ops/outbound-activations",
            headers={"Authorization": f"Bearer {api_token}"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            import json
            return json.loads(resp.read())
    except Exception as exc:
        logger.warning("outbound: could not fetch activations from API (%s) — using TARGETS fallback", exc)
        return {}


def _resolve_start_dates(api_activations: dict[str, str]) -> dict[str, str | None]:
    """Merge API activations (authoritative) with TARGETS fallback start_dates."""
    resolved: dict[str, str | None] = {}
    for t in TARGETS:
        tid = t["id"]
        if tid in api_activations:
            resolved[tid] = api_activations[tid]
        else:
            resolved[tid] = t["start_date"]
    return resolved


def _day_offset(start: date, today: date) -> int:
    return (today - start).days + 1


def build_briefing(today: date | None = None, api_activations: dict[str, str] | None = None) -> str:
    today = today or date.today()
    if api_activations is None:
        api_activations = {}
    start_dates = _resolve_start_dates(api_activations)

    lines: list[str] = [
        f"🎯 *Outbound Briefing — {today.strftime('%a %d %b %Y')}*",
        f"{'─' * 42}",
    ]

    pending: list[dict] = []
    due_today: list[tuple[dict, int, str]] = []

    for t in TARGETS:
        sd = start_dates.get(t["id"])
        if sd is None:
            pending.append(t)
            continue
        start = date.fromisoformat(sd)
        day = _day_offset(start, today)
        if day in SEQUENCE_DAYS:
            due_today.append((t, day, SEQUENCE_DAYS[day]))
        elif day > 14:
            pass  # sequence complete

    # Pending — Day 1 not yet sent
    if pending:
        lines.append(f"\n*📋 PENDIENTES — Día 1 no enviado aún ({len(pending)} targets)*")
        for t in pending:
            comps = f" ({', '.join(t['competitors_indexed'])} ya indexados)" if t["competitors_indexed"] else ""
            lines.append(
                f"• *{t['retailer']}* ({t['country']} · {t['platform']}){comps}\n"
                f"  └ {t['hook']}\n"
                f"  └ LinkedIn: {t['linkedin_url']}"
            )
        lines.append(
            "\n_Para activar: POST /admin/ops/activate-outbound-target — o llena el form del Workflow Builder en #outbound_"
        )

    # Due today
    if due_today:
        lines.append(f"\n*🔔 ACCIÓN HOY — {len(due_today)} mensajes para enviar*")
        for t, _day, action in due_today:
            lines.append(f"\n{'─' * 30}")
            if action == "linkedin":
                lines.append(_msg_linkedin(t))
            elif action == "email":
                lines.append(_msg_email(t))
            elif action == "email_data":
                lines.append(_msg_email_data(t))
            elif action == "email_followup":
                lines.append(_msg_email(t))
            elif action == "breakup":
                lines.append(_msg_breakup(t))

    if not pending and not due_today:
        lines.append("\n✅ Sin acciones de outbound para hoy.")

    lines.append(f"\n{'─' * 42}")
    lines.append("_Para agregar un target: edita `TARGETS` en `ops/outbound_briefing.py`_")

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Outbound briefing diario → #outbound")
    parser.add_argument("--slack", action="store_true", help="Postear a #outbound")
    parser.add_argument("--dry-run", action="store_true", help="Solo imprimir")
    parser.add_argument("--date", help="Fecha YYYY-MM-DD (default: hoy)")
    parser.add_argument("--api-url", default=os.getenv("MARKET_API_URL", ""), help="Base URL del API")
    parser.add_argument("--api-token", default=os.getenv("MARKET_API_TOKEN", ""), help="Bearer token del API")
    args = parser.parse_args()

    today = date.fromisoformat(args.date) if args.date else date.today()

    api_activations: dict[str, str] = {}
    if args.api_url and args.api_token:
        api_activations = _fetch_activations(args.api_url, args.api_token)

    text = build_briefing(today, api_activations)
    print(text)

    if args.slack and not args.dry_run:
        sys.path.insert(0, str(Path(__file__).parent))
        from slack_notify import deliver
        deliver(text, channel="C0B9NEEB97U")
        print("\n→ Enviado a #outbound", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
