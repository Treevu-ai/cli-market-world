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
  DASHBOARD_DATA_URL              — same as ops/monday.py
  SLACK_BOT_TOKEN                 — bot con chat:write (recomendado)
  SLACK_CHANNEL_BITACORA          — default C0B6V3Y9ZSP (bitácora producto)
  SLACK_CHANNEL_PUBLICACIONES     — default C0B6ZJ1B9B8 (publicaciones redes)
  SLACK_WEBHOOK_BITACORA          — alternativa: webhook solo bitácora
  SLACK_WEBHOOK_PUBLICACIONES     — alternativa: webhook solo publicaciones
  LINKEDIN_CAMPAIGN_START         — ISO date for Day 1 (default 2026-05-01)
  LINKEDIN_POST_UTC_HOUR          — default 13 (from linkedin-calendar)
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

from content_paths import calendar_dir, content_root, linkedin_dir, metrics_dir, rel_to_content  # noqa: E402


def _path_label(path: Path) -> str:
    """Path for reports/logs — relative to content root when using external repo."""
    return rel_to_content(path)


def _day_path_label(day: int) -> str:
    return _path_label(linkedin_dir() / f"Day-{day:02d}.md")


def _daily_dir() -> Path:
    gen = content_root() / "generated" / "daily"
    if content_root().name != "docs":
        gen.mkdir(parents=True, exist_ok=True)
        return gen
    legacy = ROOT / "ops" / "daily"
    legacy.mkdir(parents=True, exist_ok=True)
    return legacy


def _data_gate_path() -> Path:
    return linkedin_dir() / "data-gate.md"


def _dev_calendar_path() -> Path:
    cal = calendar_dir() / "dev-calendar.md"
    if cal.is_file():
        return cal
    return ROOT / "docs" / "dev-calendar.md"

CAMPAIGN_START = os.getenv("LINKEDIN_CAMPAIGN_START", "2026-05-29")
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
    ld = linkedin_dir()
    primary = ld / f"Day-{day:02d}.md"
    if primary.is_file():
        return primary
    alt = ld / f"Day-{day}.md"
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
        "path": _path_label(path),
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
    if not _data_gate_path().is_file():
        return []
    text = _data_gate_path().read_text(encoding="utf-8")
    lines: list[str] = []
    for line in text.splitlines():
        if "❌" in line or "BLOQUEADO" in line or "⛔" in line:
            lines.append(line.strip())
    return lines[:8]


def _dev_calendar_this_week(for_date: date) -> list[str]:
    if not _dev_calendar_path().is_file():
        return []
    rows: list[str] = []
    in_table = False
    for line in _dev_calendar_path().read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and "Semana" in line:
            in_table = True
        if in_table and line.startswith("|") and not line.startswith("|--"):
            if "Semana" in line:
                continue
            rows.append(line)
    # Fallback: last few table rows as "near-term content ops"
    return rows[-4:] if rows else []


def _inject_after_tldr(body: str, section: str) -> str:
    """Insert markdown block after ## TL;DR section."""
    pattern = r"(## TL;DR\s*\n.*?\n)(\n---)"
    repl = r"\1\n" + section.rstrip() + r"\2"
    out, n = re.subn(pattern, repl, body, count=1, flags=re.DOTALL)
    return out if n else body


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
    try:
        from market_adoption import adoption_markdown_section
        from market_pepy import pepy_briefing_line

        body = _inject_after_tldr(body, adoption_markdown_section(days=30))
        pepy_line = pepy_briefing_line()
    except Exception:
        pepy_line = "PyPI (Pepy): unavailable"
    stamp = (
        f"_Generado {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
        f"fuente: `/dashboard/data` · {pepy_line}_"
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
            "| Campo | Valor |",
            "|-------|-------|",
            f"| Archivo | `{today['path']}` |",
            f"| Estado | `{status}` |",
            f"| Publicado | {pub_label} |",
            f"| Pilar | {pillar} |",
            f"| Idioma | {lang} |",
            f"| Hora | {POST_UTC_HOUR}:00 UTC |",
            "",
        ]
        asset_png = linkedin_dir() / "assets" / f"day-{day:02d}" / f"day-{day:02d}-linkedin.png"
        if asset_png.is_file():
            rel_asset = rel_to_content(asset_png)
            lines += [
                f"| **Imagen LinkedIn** | `{rel_asset}` |",
                "",
                "> Copiar el **Post** abajo y adjuntar esa imagen. Carousel: ver carpeta `assets/day-{:02d}/`.".format(day),
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
            f"⚠️ No existe `{_day_path_label(day)}`. Fin de calendario 30d o revisar `LINKEDIN_CAMPAIGN_START`.",
            "",
        ]

    # Satellite: AR canasta on day 9
    if day == 9:
        ar = linkedin_dir() / "Day-09-AR.md"
        if ar.is_file():
            lines += [
                "---",
                "",
                "## Opcional mismo día — Day-09-AR",
                "",
                "⛔ Ver [[linkedin/data-gate]] — **no publicar** hasta gate AR PASSED.",
                f"Archivo: `{_path_label(ar)}`",
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
        f"1. Copiar post de `{_day_path_label(day)}` → LinkedIn (sin URL en cuerpo).",
        "2. Primer comentario con link UTM.",
        "3. Engagement 60 min.",
        "4. Marcar `published_at: YYYY-MM-DD` en frontmatter del día.",
        "",
    ]
    return "\n".join(lines)


def _repo_file_link(rel_path: str) -> str:
    repo = os.getenv("GITHUB_REPOSITORY", "")
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    if repo:
        return f"<{server}/{repo}/blob/main/{rel_path}|Ver reporte completo>"
    return f"_Repo:_ `{rel_path}`"


def _slack_configured() -> bool:
    return bool(
        os.getenv("SLACK_BOT_TOKEN")
        or os.getenv("SLACK_WEBHOOK_BITACORA")
        or os.getenv("SLACK_WEBHOOK_PUBLICACIONES")
    )


def build_slack_product_message(
    ds: str,
    data: dict,
    meta: dict,
    product_rel: str,
) -> str:
    monday = _load_monday()
    k = data.get("kpis", {})
    health = data.get("store_health", [])
    critical = [
        h for h in health if float(h.get("success_pct", 0) or 0) < 30
    ]
    warn = sorted(
        [
            h
            for h in health
            if 30 <= float(h.get("success_pct", 0) or 0) < 90
        ],
        key=lambda x: float(x.get("success_pct", 0) or 0),
    )[:8]

    lines = [
        f"📊 *Bitácora producto* · {ds}",
        "",
        monday.tldr(data),
        "",
    ]

    try:
        from market_adoption import adoption_slack_lines

        lines.extend(adoption_slack_lines(days=30))
    except Exception:
        pass

    try:
        from market_golive import go_live_slack_lines

        golive = go_live_slack_lines(days=30, dashboard_data=data)
        if golive:
            lines.extend(golive)
    except Exception:
        pass

    lines += [
        f"• Indexados: *{k.get('total_indexed', 0):,}* · 24h: *{k.get('snapshots_24h', 0):,}* · "
        f"Tiendas: *{k.get('stores_indexed', 0)}* · Coverage 7d: *{k.get('coverage_7d_pct', 0)}%*",
        "",
    ]

    if critical:
        lines.append("*🔴 Críticas (<30%)*")
        for h in critical:
            sid = h.get("store", "?")
            info = meta.get(sid, {})
            lines.append(
                f"• {info.get('name', sid)} ({info.get('country', '??')}) — "
                f"{float(h.get('success_pct', 0) or 0):.0f}%"
            )
        lines.append("")
    else:
        lines.append("✅ Sin tiendas críticas hoy.")
        lines.append("")

    if warn:
        lines.append("*🟡 Vigilar*")
        for h in warn:
            sid = h.get("store", "?")
            pct = float(h.get("success_pct", 0) or 0)
            lines.append(f"• {sid} — {pct:.0f}%")
        lines.append("")

    coll = data.get("collector", {})
    moat = data.get("moat_summary", {})
    lines.append(
        f"Collector: *{coll.get('status', '?')}* · Moat stale: *{moat.get('collector_stale', False)}*"
    )
    lines.append("")
    lines.append(_repo_file_link(product_rel))
    return "\n".join(lines)


def build_slack_content_message(
    ds: str,
    day: int,
    today: dict[str, Any] | None,
    content_rel: str,
) -> str:
    lines = [
        f"📣 *Publicaciones redes* · {ds}",
        f"Publicar *{POST_UTC_HOUR}:00 UTC* · sin link en cuerpo del post",
        "",
    ]

    if not today:
        lines.append(f"⚠️ No hay borrador `{_day_path_label(day)}`.")
        lines.append(_repo_file_link(content_rel))
        return "\n".join(lines)

    fm = today["fm"]
    pub = fm.get("published_at", "") or "⏳ pendiente"
    lines += [
        f"*{today['title']}*",
        f"Estado: `{fm.get('status', '?')}` · Publicado: {pub} · Pilar: `{fm.get('pillar', '?')}`",
        f"Archivo: `{today['path']}`",
        "",
    ]

    if today["post"]:
        lines += ["*Post (copiar a LinkedIn)*", "", today["post"], ""]
    if today["comment"]:
        lines += ["*Primer comentario*", "", today["comment"], ""]
    if today["hashtags"]:
        lines += ["*Hashtags*", "", today["hashtags"], ""]
    if today["checklist"]:
        lines += ["*Checklist*", "", today["checklist"], ""]

    tomorrow = _load_day_doc(day + 1)
    if tomorrow:
        lines += [
            "---",
            f"*Mañana (Día {day + 1}):* {tomorrow['title']} · `{tomorrow['path']}`",
            "",
        ]

    lines.append(_repo_file_link(content_rel))
    return "\n".join(lines)


def main() -> None:
    dry = "--dry-run" in sys.argv
    product_only = "--product" in sys.argv
    content_only = "--content" in sys.argv
    both = not product_only and not content_only

    today = datetime.now(timezone.utc).date()
    ds = today.isoformat()
    daily = _daily_dir()
    daily.mkdir(parents=True, exist_ok=True)

    monday = _load_monday()
    data: dict | None = None
    meta: dict | None = None
    product_path = daily / f"{ds}-product.md"
    content_path = daily / f"{ds}-content.md"

    if both or product_only:
        print("Fetching dashboard (product)...")
        data = monday.fetch_data()
        meta = monday.load_store_meta()
        product_path.write_text(build_product_report(data, meta, today), encoding="utf-8")
        print(f"Product report: {product_path}" + (" [dry-run]" if dry else ""))

    if both or content_only:
        content_path.write_text(build_content_report(today), encoding="utf-8")
        print(f"Content report: {content_path}" + (" [dry-run]" if dry else ""))

    if _slack_configured() and not dry:
        ops_dir = Path(__file__).resolve().parent
        if str(ops_dir) not in sys.path:
            sys.path.insert(0, str(ops_dir))
        from slack_notify import deliver_to_bitacora, deliver_to_publicaciones

        product_rel = _path_label(product_path)
        content_rel = _path_label(content_path)
        day = _campaign_day(today)
        today_doc = _load_day_doc(day)

        if (both or product_only) and data is not None and meta is not None:
            product_slack = build_slack_product_message(ds, data, meta, product_rel)
            deliver_to_bitacora(product_slack)
            print("Slack → bitácora (producto).")

            from procure_daily import procure_daily_configured, trigger_procure_daily_summary

            if procure_daily_configured():
                procure_result = trigger_procure_daily_summary(today)
                if procure_result.get("ok"):
                    ordered = procure_result.get("ordered", 0)
                    print(f"Slack → Procure resumen diario ({ordered} órdenes).")
                else:
                    print(f"Procure daily summary failed: {procure_result.get('error', procure_result)}")

        if both or content_only:
            if data is None:
                print("Fetching dashboard (gate + métricas para publicaciones)...")
                data = monday.fetch_data()
            from publish_pack import (
                build_slack_publish_messages,
                marketing_metrics_from_dashboard,
            )

            metrics = marketing_metrics_from_dashboard(data or {})
            publish_msgs = build_slack_publish_messages(
                ds=ds,
                campaign_day=day,
                for_date=today,
                metrics=metrics,
                post_utc_hour=POST_UTC_HOUR,
            )
            for i, msg in enumerate(publish_msgs, 1):
                prefix = (
                    f"📣 *Publicaciones ({i}/{len(publish_msgs)})*\n\n"
                    if len(publish_msgs) > 1
                    else ""
                )
                deliver_to_publicaciones(prefix + msg)
            print(
                f"Slack → publicaciones ({len(publish_msgs)} mensaje"
                f"{'s' if len(publish_msgs) != 1 else ''}, gate + copy listo)."
            )

    # Also refresh weekly price pulse when we fetched dashboard
    if data is not None and meta is not None and (both or product_only):
        week = monday._iso_week(datetime.now(timezone.utc))
        pulse_path = metrics_dir() / f"price-pulse-{week}.md"
        pulse_path.parent.mkdir(parents=True, exist_ok=True)
        pulse_path.write_text(monday.build_price_pulse(data, meta), encoding="utf-8")
        print(f"Price pulse updated: {pulse_path}")


if __name__ == "__main__":
    main()
