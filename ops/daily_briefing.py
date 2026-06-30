#!/usr/bin/env python3
"""CLI Market — Daily Briefing (product status + content calendar).

Generates two markdown reports:
  ops/daily/YYYY-MM-DD-product.md — collector KPIs, store health (product repo)
  generated/daily/YYYY-MM-DD-content.md — channel calendar + LinkedIn (content repo)

Usage:
  python3 ops/daily_briefing.py              # both reports + optional Slack
  python3 ops/daily_briefing.py --product    # product only
  python3 ops/daily_briefing.py --content    # content only
  python3 ops/daily_briefing.py --dry-run    # write files, no Slack

Env:
  DASHBOARD_DATA_URL              — same as ops/monday.py
  SLACK_BOT_TOKEN                 — bot con chat:write (recomendado)
  SLACK_CHANNEL_BITACORA          — default C0B6V3Y9ZSP (bitácora producto)
  SLACK_CHANNEL_PUBLICACIONES     — default C0B6ZJ1B9B8 (índice GTM)
  SLACK_CHANNEL_LINKEDIN_PERSONAL … SLACK_CHANNEL_OUTBOUND — copy por red (ver AGENTS.md)
  SLACK_WEBHOOK_BITACORA          — alternativa: webhook solo bitácora
  SLACK_WEBHOOK_PUBLICACIONES     — alternativa: webhook solo publicaciones
  LINKEDIN_CAMPAIGN_START         — ISO date for Day 1 (default 2026-06-01)
  LINKEDIN_POST_UTC_HOUR          — default 13 (from linkedin-calendar)
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


def _product_daily_dir() -> Path:
    """Product KPI reports live in the product repo (ops/daily/)."""
    d = ROOT / "ops" / "daily"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _content_daily_dir() -> Path:
    """Content calendar reports live in cli-market-content when external."""
    root = content_root()
    if root.name != "docs":
        gen = root / "generated" / "daily"
        gen.mkdir(parents=True, exist_ok=True)
        return gen
    legacy = ROOT / "ops" / "daily"
    legacy.mkdir(parents=True, exist_ok=True)
    return legacy


def _product_path_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _data_gate_path() -> Path:
    return linkedin_dir() / "data-gate.md"


def _dev_calendar_path() -> Path:
    cal = calendar_dir() / "dev-calendar.md"
    if cal.is_file():
        return cal
    return ROOT / "docs" / "dev-calendar.md"

CAMPAIGN_START = os.getenv("LINKEDIN_CAMPAIGN_START", "2026-06-01")
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


def _load_calendar_channels_module():
    cal_path = content_root() / "scripts" / "calendar_channels.py"
    if not cal_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("calendar_channels", cal_path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _channels_for_date(for_date: date) -> list[tuple[str, Path]]:
    cal = _load_calendar_channels_module()
    if cal is None:
        return []
    return cal.channels_for_date(for_date, _campaign_day(for_date), content_root())


def _load_doc_from_path(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(raw)
    title_m = re.search(r"^# .+ — (.+)$", body, re.MULTILINE)
    day_m = re.search(r"Day-(\d+)", path.name)
    day_num = int(day_m.group(1)) if day_m else _campaign_day(date.today())
    return {
        "day": day_num,
        "path": _path_label(path),
        "fm": fm,
        "title": title_m.group(1).strip() if title_m else fm.get("title", path.stem),
        "hooks": _section(body, "Hook (elegir 1)") or _section(body, "Hooks (elegir 1)"),
        "post": _section(body, "Post (copiar a LinkedIn — sin link en cuerpo)")
        or _section(body, "Post"),
        "comment": _section(body, "Primer comentario"),
        "checklist": _section(body, "Checklist"),
        "hashtags": _section(body, "Hashtags"),
        "assets": _section(body, "Assets"),
    }


def _load_day_doc(day: int) -> dict[str, Any] | None:
    path = _day_file(day)
    if not path:
        return None
    doc = _load_doc_from_path(path)
    if doc:
        doc["day"] = day
    return doc


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


def _append_linkedin_detail(lines: list[str], doc: dict[str, Any], *, heading: str) -> None:
    fm = doc["fm"]
    published = fm.get("published_at", "")
    status = fm.get("status", "?")
    pillar = fm.get("pillar", "?")
    lang = fm.get("lang", "es")
    pub_label = published if published else "⏳ pendiente"
    day_num = doc["day"]

    lines += [
        heading,
        "",
        "| Campo | Valor |",
        "|-------|-------|",
        f"| Archivo | `{doc['path']}` |",
        f"| Estado | `{status}` |",
        f"| Publicado | {pub_label} |",
        f"| Pilar | {pillar} |",
        f"| Idioma | {lang} |",
        f"| Hora | {POST_UTC_HOUR}:00 UTC |",
        "",
    ]
    asset_png = linkedin_dir() / "assets" / f"day-{day_num:02d}" / f"day-{day_num:02d}-linkedin.png"
    if asset_png.is_file():
        rel_asset = rel_to_content(asset_png)
        lines += [
            f"| **Imagen LinkedIn** | `{rel_asset}` |",
            "",
            (
                "> Copiar el **Post** abajo y adjuntar esa imagen. "
                f"Carousel: ver carpeta `assets/day-{day_num:02d}/`."
            ),
            "",
        ]
    if doc["hooks"]:
        lines += ["### Hooks", "", doc["hooks"], ""]
    if doc["post"]:
        preview = doc["post"]
        if len(preview) > 1200:
            preview = preview[:1200] + "\n\n… _(ver archivo completo)_"
        lines += ["### Post (copiar a LinkedIn — sin link en cuerpo)", "", preview, ""]
    if doc["comment"]:
        lines += ["### Primer comentario", "", doc["comment"], ""]
    if doc["hashtags"]:
        lines += ["### Hashtags", "", doc["hashtags"], ""]
    if doc["assets"]:
        lines += ["### Assets", "", doc["assets"], ""]
    if doc["checklist"]:
        lines += ["### Checklist", "", doc["checklist"], ""]


def build_content_report(for_date: date) -> str:
    ds = for_date.isoformat()
    day = _campaign_day(for_date)
    channels_today = _channels_for_date(for_date)
    lines = [
        f"# CLI Market — Daily Content Briefing {ds}",
        "",
        (
            f"_Calendario unificado · Día de campaña **{day}** · "
            f"publicar **{POST_UTC_HOUR}:00 UTC**_"
        ),
        "",
        f"Ancla campaña: `{CAMPAIGN_START}` (Day 1) · fuente: `scripts/calendar_channels.py`",
        "",
        "---",
        "",
        "## Canales hoy",
        "",
    ]

    if channels_today:
        lines += ["| Canal | Archivo |", "|-------|---------|"]
        for name, path in channels_today:
            lines.append(f"| {name} | `{_path_label(path)}` |")
        lines.append("")
    else:
        lines += [
            "_Sin canales programados._ Revisar `LINKEDIN_CAMPAIGN_START` o `calendar_channels.py`.",
            "",
        ]

    personal_path = next((p for c, p in channels_today if c == "LinkedIn Personal"), None)
    company_path = next((p for c, p in channels_today if c == "LinkedIn Empresa"), None)

    if personal_path:
        personal = _load_doc_from_path(personal_path)
        if personal:
            _append_linkedin_detail(
                lines,
                personal,
                heading=f"## LinkedIn Personal — Día {personal['day']}: {personal['title']}",
            )
    elif day >= 1:
        lines += [
            f"## LinkedIn Personal — Día {day}",
            "",
            f"⚠️ Sin borrador resuelto para hoy (`{_day_path_label(day)}`).",
            "",
        ]

    if company_path:
        company = _load_doc_from_path(company_path)
        if company:
            fm = company["fm"]
            lines += [
                "---",
                "",
                f"## LinkedIn Empresa — {company['title']}",
                "",
                f"- Archivo: `{company['path']}` · estado `{fm.get('status', '?')}` · "
                f"pub: {fm.get('published_at', '') or '⏳ pendiente'}",
                "",
            ]
            if company["post"]:
                preview = company["post"]
                if len(preview) > 800:
                    preview = preview[:800] + "\n\n… _(ver archivo completo)_"
                lines += ["### Post empresa", "", preview, ""]

    others = [(c, p) for c, p in channels_today if not c.startswith("LinkedIn")]
    if others:
        lines += ["---", "", "## Otros canales (archivos)", ""]
        for name, path in others:
            lines.append(f"- **{name}** · `{_path_label(path)}`")
        lines.append("")

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

    tomorrow_date = for_date + timedelta(days=1)
    tomorrow_day = _campaign_day(tomorrow_date)
    tomorrow_channels = _channels_for_date(tomorrow_date)
    lines += ["---", "", f"## Mañana — {tomorrow_date.isoformat()} (Día {tomorrow_day})", ""]
    if tomorrow_channels:
        for name, path in tomorrow_channels:
            doc = _load_doc_from_path(path) if name.startswith("LinkedIn") else None
            if doc:
                pub = doc["fm"].get("published_at", "") or "pendiente"
                lines.append(
                    f"- **{name}**: {doc['title']} · `{doc['path']}` · "
                    f"estado `{doc['fm'].get('status', '?')}` · pub: {pub}"
                )
            else:
                lines.append(f"- **{name}** · `{_path_label(path)}`")
        lines.append("")
    else:
        lines += ["_Sin canales programados para mañana._", ""]

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
        "1. En content repo: `make content` (copy listo) o leer secciones arriba.",
        f"2. Publicar canales de **Canales hoy** ({POST_UTC_HOUR}:00 UTC LinkedIn).",
        f"3. Marcar publicado: `make publish date={ds}` (content repo).",
        "4. Engagement 60 min en LinkedIn.",
        "",
    ]
    return "\n".join(lines)


def _repo_file_link(rel_path: str) -> str:
    """Product reports → product repo; content reports → cli-market-content."""
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    content_repo = os.getenv(
        "GITHUB_CONTENT_REPOSITORY",
        os.getenv("CLI_MARKET_CONTENT_GITHUB_REPO", "Treevu-ai/cli-market-content"),
    ).strip()
    product_branch = os.getenv("GITHUB_REF_NAME", "main").strip()
    content_branch = os.getenv("GITHUB_CONTENT_REF", "main").strip()
    if rel_path.startswith("generated/") and content_repo:
        repo = content_repo
        branch = content_branch
    else:
        repo = os.getenv("GITHUB_REPOSITORY", "")
        branch = product_branch
    if repo:
        return f"<{server}/{repo}/blob/{branch}/{rel_path}|Ver reporte completo>"
    return f"_Repo:_ `{rel_path}`"


def _split_slack_delivery(text: str, limit: int = 3900) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for line in text.splitlines(keepends=True):
        if size + len(line) > limit and buf:
            chunks.append("".join(buf))
            buf = []
            size = 0
        buf.append(line)
        size += len(line)
    if buf:
        chunks.append("".join(buf))
    return chunks


def _slack_configured() -> bool:
    return bool(
        os.getenv("SLACK_BOT_TOKEN")
        or os.getenv("SLACK_WEBHOOK_BITACORA")
        or os.getenv("SLACK_WEBHOOK_PUBLICACIONES")
    )


def _read_revenue_from_gtm_hub() -> dict:
    """Lee tabla Revenue de cli-market-content/strategy/GTM-Hub.md."""
    try:
        gtm = content_root() / "strategy" / "GTM-Hub.md"
        if not gtm.exists():
            return {}
        text = gtm.read_text(encoding="utf-8")
        result = {}
        for line in text.splitlines():
            if "**MRR total**" in line:
                parts = [p.strip() for p in line.split("|")]
                result["mrr"] = parts[2] if len(parts) > 2 else None
            elif "**ARR implícito**" in line:
                parts = [p.strip() for p in line.split("|")]
                result["arr"] = parts[2] if len(parts) > 2 else None
            elif "Clientes activos (pagos)" in line:
                parts = [p.strip() for p in line.split("|")]
                result["clientes"] = parts[2] if len(parts) > 2 else None
        return result
    except Exception:
        return {}


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

    revenue = _read_revenue_from_gtm_hub()
    if revenue:
        mrr = revenue.get("mrr") or "[ACTUALIZAR]"
        arr = revenue.get("arr") or "[ACTUALIZAR]"
        clientes = revenue.get("clientes") or "[ACTUALIZAR]"
        needs_update = "[ACTUALIZAR]" in f"{mrr}{arr}{clientes}"
        rev_icon = "⚠️" if needs_update else "💰"
        lines.append(f"{rev_icon} *Revenue* — MRR: *{mrr}* · ARR: *{arr}* · Clientes pagos: *{clientes}*")
        if needs_update:
            lines.append("_→ Actualizar en `strategy/GTM-Hub.md` › Revenue — tabla viva_")
        lines.append("")

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


def main() -> None:
    dry = "--dry-run" in sys.argv
    product_only = "--product" in sys.argv
    content_only = "--content" in sys.argv
    both = not product_only and not content_only

    today = datetime.now(timezone.utc).date()
    ds = today.isoformat()
    product_dir = _product_daily_dir()
    content_dir = _content_daily_dir()

    monday = _load_monday()
    data: dict | None = None
    meta: dict | None = None
    product_path = product_dir / f"{ds}-product.md"
    content_path = content_dir / f"{ds}-content.md"

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

        product_rel = _product_path_label(product_path)
        day = _campaign_day(today)

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
                build_gtm_channel_deliveries,
                marketing_metrics_from_dashboard,
            )
            from slack_notify import deliver

            metrics = marketing_metrics_from_dashboard(data or {})
            summary, deliveries = build_gtm_channel_deliveries(
                campaign_day=day,
                for_date=today,
                metrics=metrics,
                post_utc_hour=POST_UTC_HOUR,
                dashboard_data=data,
            )
            deliver_to_publicaciones(summary)
            for d in deliveries:
                for msg in d.messages:
                    for chunk in _split_slack_delivery(msg):
                        deliver(chunk, channel=d.channel_id)
            labels = ", ".join(d.label for d in deliveries) or "ninguno"
            print(
                f"Slack → publicaciones (índice) + {len(deliveries)} canal"
                f"{'es' if len(deliveries) != 1 else ''} GTM ({labels})."
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
