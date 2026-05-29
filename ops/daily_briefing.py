#!/usr/bin/env python3
"""CLI Market — Daily Briefing (product status + content calendar).

Generates two markdown reports under ops/daily/:
  YYYY-MM-DD-product.md   — collector KPIs, store health (from production dashboard)
  YYYY-MM-DD-content.md   — LinkedIn day N post draft, checklist, gates

Usage:
  python3 ops/daily_briefing.py              # both reports + optional Slack
  python3 ops/daily_briefing.py --product    # product only
  python3 ops/daily_briefing.py --content    # content only
  python3 ops/daily_briefing.py --dry-run    # write files, no Slack

Env:
  DASHBOARD_DATA_URL          — same as ops/monday.py
  SLACK_WEBHOOK_URL           — optional summary
  LINKEDIN_CAMPAIGN_START     — ISO date for Day 1 (default 2026-05-01)
  LINKEDIN_POST_UTC_HOUR      — default 13 (from linkedin-calendar)
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LINKEDIN_DIR = ROOT / "docs" / "linkedin"
DATA_GATE_PATH = ROOT / "docs" / "linkedin" / "data-gate.md"
DEV_CALENDAR_PATH = ROOT / "docs" / "dev-calendar.md"
DAILY_DIR = ROOT / "ops" / "daily"

CAMPAIGN_START = os.getenv("LINKEDIN_CAMPAIGN_START", "2026-05-01")
POST_UTC_HOUR = int(os.getenv("LINKEDIN_POST_UTC_HOUR", "13"))


def _load_monday():
    path = Path(__file__).parent / "monday.py"
    spec = importlib.util.spec_from_file_location("monday_ops", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        fm[key.strip()] = val.strip()
    return fm, parts[2]


def _section(body: str, heading: str) -> str:
    """Extract markdown under ## heading until next ## at same level."""
    pattern = rf"(?m)^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    m = re.search(pattern, body, re.DOTALL)
    return m.group(1).strip() if m else ""


def _campaign_day(for_date: date) -> int:
    start = date.fromisoformat(CAMPAIGN_START)
    return (for_date - start).days + 1


def _day_file(day: int) -> Path | None:
    primary = LINKEDIN_DIR / f"Day-{day:02d}.md"
    if primary.is_file():
        return primary
    alt = LINKEDIN_DIR / f"Day-{day}.md"
    return alt if alt.is_file() else None


def _load_day_doc(day: int) -> dict[str, Any] | None:
    path = _day_file(day)
    if not path:
        return None
    raw = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(raw)
    title_m = re.search(r"^# Day \d+ — (.+)$", body, re.MULTILINE)
    return {
        "day": day,
        "path": path.relative_to(ROOT).as_posix(),
        "fm": fm,
        "title": title_m.group(1).strip() if title_m else fm.get("title", f"Day {day}"),
        "hooks": _section(body, "Hooks (elegir 1)"),
        "post": _section(body, "Post (copiar a LinkedIn — sin link en cuerpo)"),
        "comment": _section(body, "Primer comentario"),
        "checklist": _section(body, "Checklist"),
        "hashtags": _section(body, "Hashtags"),
        "assets": _section(body, "Assets"),
    }


def _gate_snippets() -> list[str]:
    if not DATA_GATE_PATH.is_file():
        return []
    text = DATA_GATE_PATH.read_text(encoding="utf-8")
    lines: list[str] = []
    for line in text.splitlines():
        if "❌" in line or "BLOQUEADO" in line or "⛔" in line:
            lines.append(line.strip())
    return lines[:8]


def _dev_calendar_this_week(for_date: date) -> list[str]:
    if not DEV_CALENDAR_PATH.is_file():
        return []
    # Simple: return lines from "## Jun 2026" table mentioning current ISO week
    week = for_date.isocalendar()
    week_label = f"W{week.week}"
    rows: list[str] = []
    in_table = False
    for line in DEV_CALENDAR_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and "Semana" in line:
            in_table = True
        if in_table and line.startswith("|") and not line.startswith("|--"):
            if "Semana" in line:
                continue
            rows.append(line)
    # Fallback: last few table rows as "near-term content ops"
    return rows[-4:] if rows else []


def build_product_report(data: dict, meta: dict, for_date: date) -> str:
    monday = _load_monday()
    body = monday.build_report(data, meta)
    ds = for_date.isoformat()
    body = re.sub(
        r"^# CLI Market — Monday Ops \d{4}-\d{2}-\d{2}",
        f"# CLI Market — Daily Product Status {ds}",
        body,
        count=1,
    )
    stamp = (
        f"_Generado {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
        f"fuente: `/dashboard/data`_"
    )
    if "\n" in body:
        title, rest = body.split("\n", 1)
        return f"{title}\n\n{stamp}\n{rest}"
    return f"{body}\n\n{stamp}\n"


def build_content_report(for_date: date) -> str:
    ds = for_date.isoformat()
    day = _campaign_day(for_date)
    lines = [
        f"# CLI Market — Daily Content Briefing {ds}",
        "",
        f"_Calendario LinkedIn 30d · Día de campaña **{day}** · publicar **{POST_UTC_HOUR}:00 UTC**_",
        "",
        f"Ancla campaña: `{CAMPAIGN_START}` (Day 1) · [[linkedin-calendar]] · [[linkedin/00-Index]]",
        "",
        "---",
        "",
    ]

    today = _load_day_doc(day)
    if today:
        fm = today["fm"]
        published = fm.get("published_at", "")
        status = fm.get("status", "?")
        pillar = fm.get("pillar", "?")
        lang = fm.get("lang", "es")
        pub_label = published if published else "⏳ pendiente"

        lines += [
            f"## Hoy — Día {day}: {today['title']}",
            "",
            f"| Campo | Valor |",
            f"|-------|-------|",
            f"| Archivo | `{today['path']}` |",
            f"| Estado | `{status}` |",
            f"| Publicado | {pub_label} |",
            f"| Pilar | {pillar} |",
            f"| Idioma | {lang} |",
            f"| Hora | {POST_UTC_HOUR}:00 UTC |",
            "",
        ]
        if today["hooks"]:
            lines += ["### Hooks", "", today["hooks"], ""]
        if today["post"]:
            preview = today["post"]
            if len(preview) > 1200:
                preview = preview[:1200] + "\n\n… _(ver archivo completo)_"
            lines += ["### Post (copiar a LinkedIn — sin link en cuerpo)", "", preview, ""]
        if today["comment"]:
            lines += ["### Primer comentario", "", today["comment"], ""]
        if today["hashtags"]:
            lines += ["### Hashtags", "", today["hashtags"], ""]
        if today["assets"]:
            lines += ["### Assets", "", today["assets"], ""]
        if today["checklist"]:
            lines += ["### Checklist", "", today["checklist"], ""]
    else:
        lines += [
            f"## Hoy — Día {day}",
            "",
            f"⚠️ No existe `docs/linkedin/Day-{day:02d}.md`. Fin de calendario 30d o revisar `LINKEDIN_CAMPAIGN_START`.",
            "",
        ]

    # Satellite: AR canasta on day 9
    if day == 9:
        ar = LINKEDIN_DIR / "Day-09-AR.md"
        if ar.is_file():
            lines += [
                "---",
                "",
                "## Opcional mismo día — Day-09-AR",
                "",
                "⛔ Ver [[linkedin/data-gate]] — **no publicar** hasta gate AR PASSED.",
                f"Archivo: `{ar.relative_to(ROOT).as_posix()}`",
                "",
            ]

    tomorrow = _load_day_doc(day + 1)
    lines += ["---", "", f"## Mañana — Día {day + 1} (preview)", ""]
    if tomorrow:
        pub = tomorrow["fm"].get("published_at", "") or "pendiente"
        lines += [
            f"- **{tomorrow['title']}** · `{tomorrow['path']}` · estado `{tomorrow['fm'].get('status', '?')}` · pub: {pub}",
            "",
        ]
        if tomorrow["hooks"]:
            first_hook = tomorrow["hooks"].splitlines()[0][:120]
            lines += [f"  Hook: {first_hook}", ""]
    else:
        lines += ["_Sin borrador para mañana._", ""]

    # Unpublished days in campaign window
    unpublished: list[str] = []
    for d in range(1, min(day + 1, 31)):
        doc = _load_day_doc(d)
        if not doc:
            continue
        if not doc["fm"].get("published_at"):
            unpublished.append(f"- Día {d}: {doc['title']} (`{doc['path']}`)")
    if unpublished:
        lines += ["---", "", "## Backlog — días sin `published_at`", ""]
        lines.extend(unpublished[:15])
        if len(unpublished) > 15:
            lines.append(f"- _… y {len(unpublished) - 15} más_")
        lines.append("")

    gates = _gate_snippets()
    if gates:
        lines += ["---", "", "## Gates activos (data-gate.md)", ""]
        lines.extend(gates)
        lines.append("")

    dev_rows = _dev_calendar_this_week(for_date)
    if dev_rows:
        lines += ["---", "", "## Dev / otros canales (dev-calendar)", ""]
        lines.extend(dev_rows)
        lines.append("")

    lines += [
        "---",
        "",
        "## Acciones rápidas",
        "",
        "1. Copiar post de `docs/linkedin/Day-XX.md` → LinkedIn (sin URL en cuerpo).",
        "2. Primer comentario con link UTM.",
        "3. Engagement 60 min.",
        "4. Marcar `published_at: YYYY-MM-DD` en frontmatter del día.",
        "",
    ]
    return "\n".join(lines)


def _slack_summary(
    ds: str,
    data: dict,
    day: int,
    today: dict[str, Any] | None,
    product_path: str,
    content_path: str,
) -> str:
    k = data.get("kpis", {})
    critical = sum(
        1 for h in data.get("store_health", [])
        if float(h.get("success_pct", 0) or 0) < 30
    )
    title = today["title"] if today else f"Día {day} (sin archivo)"
    pub = (today or {}).get("fm", {}).get("published_at", "") or "pendiente"
    return (
        f"📋 CLI Market Daily Briefing {ds}\n\n"
        f"*Producto:* {k.get('total_indexed', 0):,} indexados · "
        f"{k.get('snapshots_24h', 0):,} 24h · "
        f"{critical} críticas\n"
        f"*Contenido:* Día {day} — {title} · pub LI: {pub} · {POST_UTC_HOUR}:00 UTC\n\n"
        f"Reportes:\n• {product_path}\n• {content_path}"
    )


def main() -> None:
    dry = "--dry-run" in sys.argv
    product_only = "--product" in sys.argv
    content_only = "--content" in sys.argv
    both = not product_only and not content_only

    slack_url = os.getenv("SLACK_WEBHOOK_URL", "")
    for i, a in enumerate(sys.argv):
        if a == "--slack" and i + 1 < len(sys.argv):
            slack_url = sys.argv[i + 1]

    today = datetime.now(timezone.utc).date()
    ds = today.isoformat()
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    monday = _load_monday()
    data: dict | None = None
    meta: dict | None = None
    product_path = DAILY_DIR / f"{ds}-product.md"
    content_path = DAILY_DIR / f"{ds}-content.md"

    if both or product_only:
        print("Fetching dashboard (product)...")
        data = monday.fetch_data()
        meta = monday.load_store_meta()
        product_path.write_text(build_product_report(data, meta, today), encoding="utf-8")
        print(f"Product report: {product_path}" + (" [dry-run]" if dry else ""))

    if both or content_only:
        content_path.write_text(build_content_report(today), encoding="utf-8")
        print(f"Content report: {content_path}" + (" [dry-run]" if dry else ""))

    if slack_url and not dry and data is not None:
        day = _campaign_day(today)
        today_doc = _load_day_doc(day)
        msg = _slack_summary(
            ds,
            data,
            day,
            today_doc,
            product_path.relative_to(ROOT).as_posix(),
            content_path.relative_to(ROOT).as_posix(),
        )
        monday.notify_slack(slack_url, msg)
        print("Slack notified.")

    # Also refresh weekly price pulse when we fetched dashboard
    if data is not None and meta is not None and (both or product_only):
        week = monday._iso_week(datetime.now(timezone.utc))
        pulse_path = ROOT / "docs" / "metrics" / f"price-pulse-{week}.md"
        pulse_path.parent.mkdir(parents=True, exist_ok=True)
        pulse_path.write_text(monday.build_price_pulse(data, meta), encoding="utf-8")
        print(f"Price pulse updated: {pulse_path}")


if __name__ == "__main__":
    main()
