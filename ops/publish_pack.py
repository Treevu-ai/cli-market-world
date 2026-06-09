"""Slack-first publish pack — gate + live metrics + copy-paste per channel."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from content_paths import content_root, linkedin_dir, rel_to_content

MAX_SLACK_CHARS = 3800
COVERAGE_THRESHOLD = 80.0
MOAT_THRESHOLD = 40_000
CAMPAIGN_START = os.getenv("LINKEDIN_CAMPAIGN_START", "2026-06-01")

PERSONAL_OFFSET = int(os.getenv("LINKEDIN_PERSONAL_DAY_OFFSET", "0"))
COMPANY_OFFSET = int(os.getenv("LINKEDIN_COMPANY_DAY_OFFSET", "-1"))

RICARDO_LABELS = {
    "LinkedIn Personal": "LINKEDIN PERSONAL",
    "LinkedIn Empresa": "LINKEDIN EMPRESA",
    "DEV.to": "DEV.TO",
    "Hacker News": "HACKER NEWS",
    "Reddit": "REDDIT",
}


def format_publish_date(for_date: date) -> str:
    """User-facing label — ISO date, not campaign day number."""
    return for_date.isoformat()


def ricardo_channel_label(label: str) -> str:
    if label.startswith("Twitter"):
        return "TWITTER / X"
    return RICARDO_LABELS.get(label, label.upper())


def ricardo_header(label: str, for_date: date) -> str:
    channel = ricardo_channel_label(label)
    return f"👋 *RICARDO — ESTE POST ES PARA {channel}* · `{for_date.isoformat()}`\n\n"


def publish_close_command(for_date: date) -> str:
    return f"make publish date={format_publish_date(for_date)}"


@dataclass
class ChannelCopy:
    name: str
    path_label: str
    status: str
    data_gated: bool
    post: str
    comment: str
    hashtags: str
    checklist: str
    asset_hint: str


def marketing_metrics_from_dashboard(data: dict[str, Any]) -> dict[str, Any]:
    k = data.get("kpis") or {}
    moat = data.get("moat_summary") or {}
    coll = data.get("collector") or {}
    coverage = float(k.get("coverage_7d_pct") or moat.get("coverage_7d_pct") or 0)
    if 0 < coverage <= 1:
        coverage *= 100
    total = int(k.get("total_indexed") or moat.get("total_indexed") or 0)
    snap = int(k.get("snapshots_24h") or moat.get("snapshots_24h") or 0)
    stores = int(k.get("stores_indexed") or moat.get("stores_indexed") or 0)
    gate_pass = bool(
        moat.get("marketing_gate_pass")
        if moat.get("marketing_gate_pass") is not None
        else (coverage >= COVERAGE_THRESHOLD and total >= MOAT_THRESHOLD)
    )
    return {
        "coverage_7d_pct": round(coverage, 1),
        "total_indexed": total,
        "snapshots_24h": snap,
        "stores_indexed": stores,
        "collector_status": coll.get("status") or moat.get("collector_status") or "?",
        "gate_pass": gate_pass,
    }


def gate_slack_lines(metrics: dict[str, Any]) -> list[str]:
    ok = metrics.get("gate_pass")
    head = "✅ *Data-gate ABIERTO*" if ok else "⛔ *Data-gate CERRADO* — usar post de contingencia"
    return [
        head,
        (
            f"• *{metrics['total_indexed']:,}* indexados · "
            f"*{metrics['snapshots_24h']:,}* refresh 24h · "
            f"*{metrics['coverage_7d_pct']:.0f}%* coverage 7d · "
            f"*{metrics['stores_indexed']}* retailers"
        ),
        f"• Collector: `{metrics['collector_status']}`",
        "_Cifras live (prod). Pegar en posts data-gated — no abrir dashboard._",
    ]


def moat_paste_line(metrics: dict[str, Any]) -> str:
    return (
        f"**{metrics['snapshots_24h']:,}** precios refresh 24h · "
        f"**{metrics['total_indexed']:,}** indexados · "
        f"**{metrics['stores_indexed']}** retailers · "
        f"**{metrics['coverage_7d_pct']:.0f}%** coverage 7d"
    )


def apply_live_metrics(text: str, metrics: dict[str, Any]) -> str:
    """Refresh moat lines in post copy with live dashboard numbers."""
    if not text.strip():
        return text
    snap = metrics["snapshots_24h"]
    total = metrics["total_indexed"]
    stores = metrics["stores_indexed"]
    out = text
    out = re.sub(
        r"\*\*[\d,]+\*\*\s*precios[^\n]*refresh\s*24h[^\n]*",
        moat_paste_line(metrics),
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(r"\*\*[\d,]+\*\*\s*precios en refresh 24h", f"**{snap:,}** precios en refresh 24h", out)
    out = re.sub(r"\*\*[\d,]+\*\*\s*indexados", f"**{total:,}** indexados", out)
    out = re.sub(r"\*\*[\d,]+\*\*\s*retailers[^\n]*", f"**{stores}** retailers fresh", out)
    out = re.sub(r"~\s*[\d,]+\s*precios en refresh 24h", f"~{snap:,} precios en refresh 24h", out)
    out = re.sub(r"\*\*100%\*\*", f"**{metrics['coverage_7d_pct']:.0f}%**", out, count=1)
    return out


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
        fm[key.strip()] = val.strip().strip('"')
    return fm, parts[2]


def _scheduled_on_date(path, for_date: date) -> bool:
    """Include draft unless frontmatter pins it to another publish date."""
    if not path.is_file():
        return False
    fm, _ = _parse_frontmatter(path.read_text(encoding="utf-8"))
    pub = (fm.get("published_at") or "").strip()
    if pub and pub != for_date.isoformat():
        return False
    return True


def _section(body: str, heading: str) -> str:
    pattern = rf"(?m)^#{{2,3}} {re.escape(heading)}\s*\n(.*?)(?=^#{{2,3}} |\Z)"
    m = re.search(pattern, body, re.DOTALL)
    return m.group(1).strip() if m else ""


def _load_channel_md(path) -> ChannelCopy | None:
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(raw)
    title_m = re.search(r"^# .+ — (.+)$", body, re.MULTILINE)
    status = (fm.get("status") or "?").lower()
    return ChannelCopy(
        name=title_m.group(1).strip() if title_m else path.stem,
        path_label=rel_to_content(path),
        status=status,
        data_gated=status == "data-gated" or "data-gate" in body.lower(),
        post=_section(body, "Post (copiar a LinkedIn — sin link en cuerpo)")
        or _section(body, "Post"),
        comment=_section(body, "Primer comentario"),
        hashtags=_section(body, "Hashtags"),
        checklist=_section(body, "Checklist"),
        asset_hint=_section(body, "Assets"),
    )


def _linkedin_company_dir():
    return content_root() / "linkedin-company"


_WEEKDAY_TWITTER = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}


def _load_twitter_day(path, for_date: date) -> tuple[str, str] | None:
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8")
    _, body = _parse_frontmatter(raw)
    heading = _WEEKDAY_TWITTER.get(for_date.weekday(), "")
    if not heading:
        return None
    post = _section(body, f"{heading} — Thread: What 43K prices taught us about LATAM retail")
    if not post:
        post = _section(body, heading)
    if not post:
        post = _section(body, f"{heading} — Stat drop") or _section(body, f"{heading} — Hot take")
    if not post:
        return None
    # Strip markdown code fence wrapper if present
    post = re.sub(r"^```\n?", "", post.strip())
    post = re.sub(r"\n?```$", "", post.strip())
    comment = (
        "Pro $39/mo — alertas + MCP + checkout para agentes que monitorean precios:\n"
        "https://cli-market.dev/#pro-checkout?utm_source=twitter&utm_campaign=week2"
    )
    return post, comment


def channels_for_date(for_date: date, campaign_day: int) -> list[tuple[str, Any]]:
    """Return (label, path) for active channels today."""
    root = content_root()
    items: list[tuple[str, Any]] = []

    personal = linkedin_dir() / f"Day-{campaign_day:02d}.md"
    if not personal.is_file():
        alt = linkedin_dir() / f"Day-{campaign_day + PERSONAL_OFFSET:02d}.md"
        personal = alt if alt.is_file() else personal
    if personal.is_file() and _scheduled_on_date(personal, for_date):
        items.append(("LinkedIn Personal", personal))

    cday = campaign_day + COMPANY_OFFSET
    company = _linkedin_company_dir() / f"Company-Day-{cday:02d}.md"
    if company.is_file() and _scheduled_on_date(company, for_date):
        items.append(("LinkedIn Empresa", company))

    articles = {
        date(2026, 6, 9): "devto-02-add-commerce-agent-4-lines.md",
        date(2026, 6, 16): "devto-01-commerce-infrastructure.md",
        date(2026, 6, 23): "devto-04-vtex-magento-dev-guide.md",
    }
    if for_date in articles:
        p = root / "devto" / articles[for_date]
        if p.is_file():
            items.append(("DEV.to", p))

    if for_date == date(2026, 6, 10):
        p = root / "hn" / "hn-01-show-hn.md"
        if p.is_file():
            items.append(("Hacker News", p))

    reddit_posts = {
        date(2026, 6, 9): "reddit-01-sideproject.md",
        date(2026, 6, 11): "reddit-02-python-tutorial.md",
        date(2026, 6, 18): "reddit-03-dataisbeautiful.md",
        date(2026, 6, 25): "reddit-04-aiagents.md",
    }
    if for_date in reddit_posts:
        p = root / "reddit" / reddit_posts[for_date]
        if p.is_file():
            items.append(("Reddit", p))

    week_num = ((for_date - date(2026, 6, 1)).days // 7) + 1
    tw = root / "twitter" / f"tweets-w{week_num}.md"
    if tw.is_file():
        items.append((f"Twitter/X W{week_num}", tw))

    return items


def _asset_line(copy: ChannelCopy, campaign_day: int) -> str:
    hint = (copy.asset_hint or "").strip()
    if hint:
        for line in hint.splitlines():
            if "png" in line.lower() or "jpg" in line.lower() or "adjuntar" in line.lower():
                return line.strip().strip("`")
    return f"linkedin/assets/day-{campaign_day:02d}/day-{campaign_day:02d}-linkedin.png"


def _channel_blocks(
    label: str,
    copy: ChannelCopy,
    metrics: dict[str, Any],
    *,
    campaign_day: int = 0,
) -> list[str]:
    gated_warn = ""
    if copy.data_gated and not metrics.get("gate_pass"):
        gated_warn = "⛔ _Data-gated — NO publicar hasta gate abierto._\n"

    post = apply_live_metrics(copy.post, metrics) if copy.post else ""
    hashtags = (copy.hashtags or "").strip()
    post_with_tags = post
    if post and hashtags:
        post_with_tags = f"{post.rstrip()}\n\n{hashtags}"

    lines = [
        f"━━━ *{label}* · `{copy.path_label}` ━━━",
        gated_warn.rstrip(),
        f"Estado: `{copy.status}`" + (" · data-gated" if copy.data_gated else ""),
        "",
        "*1) POST + hashtags + imagen* _(copiar y publicar)_",
        "",
    ]
    if post_with_tags:
        lines += [post_with_tags, ""]
    elif post:
        lines += [post, ""]

    if label.startswith("LinkedIn"):
        asset = _asset_line(copy, campaign_day)
        lines += [f"🖼 *Imagen:* `{asset}`", ""]

    lines += ["*2) PRIMER COMENTARIO* _(pegar justo después de publicar)_", ""]
    if copy.comment:
        lines += [copy.comment.strip(), ""]
    else:
        lines += ["_(sin borrador de comentario — añadir CTA manual)_", ""]

    return [ln for ln in lines if ln is not None]


def _split_messages(chunks: list[str]) -> list[str]:
    """Split into Slack-safe messages."""
    messages: list[str] = []
    buf: list[str] = []
    size = 0
    for chunk in chunks:
        part = chunk if chunk.endswith("\n") else chunk + "\n"
        if size + len(part) > MAX_SLACK_CHARS and buf:
            messages.append("\n".join(buf).strip())
            buf = []
            size = 0
        buf.append(part.rstrip("\n"))
        size += len(part)
    if buf:
        messages.append("\n".join(buf).strip())
    return messages


def build_slack_publish_messages(
    *,
    ds: str,
    campaign_day: int,
    for_date: date,
    metrics: dict[str, Any],
    post_utc_hour: int,
) -> list[str]:
    """Ordered Slack messages for #publicaciones — gate, metrics, copy per channel."""
    pub_date = format_publish_date(for_date)
    intro = [
        f"📋 *RICARDO — PUBLICACIONES DE HOY* · *{pub_date}*",
        f"Hora sugerida: *{post_utc_hour}:00 UTC* · sin link en cuerpo del post",
        "",
        "*Orden (cada red)*",
        "1️⃣ Revisar gate + cifras (abajo)",
        "2️⃣ Copiar *POST + hashtags* → adjuntar imagen → publicar",
        "3️⃣ Pegar *PRIMER COMENTARIO* con CTA",
        f"4️⃣ `{publish_close_command(for_date)}` cuando cierres",
        "",
        *gate_slack_lines(metrics),
        "",
        "*Línea moat (pegar si el post pide cifras)*",
        moat_paste_line(metrics),
        "",
    ]

    channel_items = channels_for_date(for_date, campaign_day)
    if not channel_items:
        intro += ["⚠️ Sin borradores activos para hoy en content repo.", ""]
        return _split_messages(["\n".join(intro)])

    body_parts: list[str] = []
    for label, path in channel_items:
        r_header = ricardo_header(label, for_date).rstrip()
        if label.startswith("LinkedIn") or label in ("DEV.to", "Hacker News", "Reddit"):
            copy = _load_channel_md(path)
            if copy:
                body_parts.append(r_header)
                body_parts.extend(
                    _channel_blocks(label, copy, metrics, campaign_day=campaign_day)
                )
                continue
        if label.startswith("Twitter"):
            tw = _load_twitter_day(path, for_date)
            if tw:
                post, comment = tw
                post = apply_live_metrics(post, metrics)
                body_parts += [
                    r_header,
                    f"━━━ *{label}* · `{rel_to_content(path)}` ━━━",
                    "",
                    "*1) THREAD / POST* _(copiar y publicar)_",
                    "",
                    post,
                    "",
                    f"💬 *RICARDO — PRIMER REPLY ({ricardo_channel_label(label)})* · `{pub_date}`",
                    "",
                    comment,
                    "",
                ]
                continue
        raw = path.read_text(encoding="utf-8")
        _, body = _parse_frontmatter(raw)
        excerpt = body.strip()
        if len(excerpt) > 2000:
            excerpt = excerpt[:2000] + "\n\n… _(ver archivo completo)_"
        body_parts += [
            r_header,
            f"━━━ *{label}* · `{rel_to_content(path)}` ━━━",
            "",
            "*1) POST*",
            "",
            excerpt,
            "",
        ]

    backlog = [
        "---",
        f"_Marcar publicado ({pub_date}):_ `cd cli-market-content && {publish_close_command(for_date)}`",
    ]
    content_msgs = _split_messages(["\n".join(intro)] + body_parts + ["\n".join(backlog)])
    content_msgs.append(
        build_publish_checklist_message(
            campaign_day=campaign_day,
            for_date=for_date,
            gate_pass=bool(metrics.get("gate_pass")),
        )
    )
    return content_msgs


def build_publish_checklist_message(
    *,
    campaign_day: int,
    for_date: date,
    gate_pass: bool,
) -> str:
    """Short closing checklist — tick mentally without leaving Slack."""
    pub_date = format_publish_date(for_date)
    channel_items = channels_for_date(for_date, campaign_day)
    lines = [
        f"✅ *Checklist publicación* · {pub_date}",
        "",
        "Marca al terminar cada paso (reacciona ✅ en Slack o mentalmente):",
        "",
        f"☐ Gate — {'abierto · publicar normal' if gate_pass else 'cerrado · contingencia'}",
    ]

    for label, _path in channel_items:
        if label == "LinkedIn Personal":
            lines.append("☐ LI Personal — post + hashtags + imagen")
            lines.append("☐ LI Personal — primer comentario")
        elif label == "LinkedIn Empresa":
            lines.append("☐ LI Empresa — post + hashtags + imagen")
            lines.append("☐ LI Empresa — primer comentario")
        elif label.startswith("Twitter"):
            lines.append(f"☐ {label} — thread / tweet")
            lines.append(f"☐ {label} — reply CTA")
        else:
            lines.append(f"☐ {label} — post publicado")
            lines.append(f"☐ {label} — comentario / CTA")

    lines += [
        "☐ Asset / imagen adjunta (si aplica)",
        f"☐ `{publish_close_command(for_date)}`",
        "",
        f"_Cuando todo esté hecho, GTM del {pub_date} cerrado._",
    ]
    return "\n".join(lines)