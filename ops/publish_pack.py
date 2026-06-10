"""Slack-first publish pack — gate + live metrics + copy-paste per channel."""

from __future__ import annotations

import importlib.util
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
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
    if label.startswith("Reddit"):
        return label.upper()
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
    preamble: str
    sections: list[tuple[str, str]]
    hooks: str
    post: str
    comment: str
    hashtags: str
    checklist: str
    asset_hint: str


@dataclass
class GtmChannelDelivery:
    label: str
    channel_id: str
    messages: list[str]

    @property
    def text(self) -> str:
        """Legacy single-blob view (tests / logs)."""
        return "\n\n—\n\n".join(self.messages)


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


def moat_paste_line_slack(metrics: dict[str, Any]) -> str:
    """Slack mrkdwn — *bold* not **markdown**."""
    return (
        f"*{metrics['snapshots_24h']:,}* precios refresh 24h · "
        f"*{metrics['total_indexed']:,}* indexados · "
        f"*{metrics['stores_indexed']}* retailers · "
        f"*{metrics['coverage_7d_pct']:.0f}%* coverage 7d"
    )


def _slack_divider() -> str:
    return "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"


def _build_channel_slack_messages(
    label: str,
    path,
    *,
    for_date: date,
    metrics: dict[str, Any],
    campaign_day: int,
    post_utc_hour: int,
) -> list[str]:
    """One Slack post per step — easier to scan than a single wall of text."""
    channel = ricardo_channel_label(label)
    pub_date = format_publish_date(for_date)
    path_label = rel_to_content(path)
    messages: list[str] = []

    header_lines = [
        f"👋 *RICARDO — {channel}*",
        f"📅 *{pub_date}* · sugerido *{post_utc_hour}:00 UTC*",
        "",
        *gate_slack_lines(metrics),
        "",
        f"📁 Borrador: `{path_label}`",
    ]
    messages.append("\n".join(header_lines))

    if label.startswith("LinkedIn") or label in ("DEV.to", "Hacker News") or label.startswith("Reddit"):
        copy = _load_channel_md(path)
        if copy:
            gated = ""
            if copy.data_gated and not metrics.get("gate_pass"):
                gated = "⛔ _Data-gated — NO publicar hasta gate abierto._"

            meta = [
                _slack_divider(),
                "*BORRADOR — content repo*",
                f"Estado: `{copy.status}`" + (" · data-gated" if copy.data_gated else ""),
                "_Cada bloque = misma sección que en GitHub. Sin omitir._",
                _slack_divider(),
            ]
            messages.append("\n".join(meta))
            messages.extend(
                _slack_messages_from_channel_copy(copy, metrics, gated_warn=gated)
            )
            messages.append(
                "\n".join(
                    [
                        _slack_divider(),
                        f"✅ *Cerrar GTM:* `cd cli-market-content && {publish_close_command(for_date)}`",
                    ]
                )
            )
            return messages

    if label.startswith("Twitter"):
        tw = _load_twitter_day(path, for_date)
        if tw:
            heading, post = tw
            post = apply_live_metrics(post, metrics)
            messages.append(
                "\n".join(
                    [
                        _slack_divider(),
                        f"*{heading}*",
                        _slack_divider(),
                        "",
                        slack_copy_block(post),
                    ]
                )
            )
            messages.append(
                "\n".join(
                    [
                        _slack_divider(),
                        f"✅ *Cerrar:* `cd cli-market-content && {publish_close_command(for_date)}`",
                    ]
                )
            )
            return messages

    raw = path.read_text(encoding="utf-8")
    _, body = _parse_frontmatter(raw)
    excerpt = body.strip()
    if len(excerpt) > 2000:
        excerpt = excerpt[:2000] + "\n\n… _(ver archivo completo)_"
    messages.append(
        "\n".join(
            [
                _slack_divider(),
                "*PASO 1 — CONTENIDO*",
                _slack_divider(),
                "",
                slack_copy_block(excerpt),
                "",
                f"✅ *Cerrar:* `cd cli-market-content && {publish_close_command(for_date)}`",
            ]
        )
    )
    return messages


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


def _is_already_published_fm(fm: dict[str, str]) -> bool:
    return (fm.get("status") or "").strip().lower() == "published"


def _find_published_on_date(directory, glob_pattern: str, for_date: date):
    """Return draft whose frontmatter published_at matches for_date exactly."""
    if not directory.is_dir():
        return None
    iso = for_date.isoformat()
    for path in sorted(directory.glob(glob_pattern)):
        fm, _ = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if _is_already_published_fm(fm):
            continue
        if (fm.get("published_at") or "").strip() == iso:
            return path
    return None


def _resolve_linkedin_draft(directory, glob_pattern: str, offset_path, for_date: date):
    """Prefer calendar published_at; fall back to offset filename when unscheduled."""
    by_date = _find_published_on_date(directory, glob_pattern, for_date)
    if by_date is not None:
        return by_date
    if offset_path.is_file() and _scheduled_on_date(offset_path, for_date):
        return offset_path
    return None


def _section(body: str, heading: str) -> str:
    pattern = rf"(?m)^#{{2,3}} {re.escape(heading)}\s*\n(.*?)(?=^#{{2,3}} |\Z)"
    m = re.search(pattern, body, re.DOTALL)
    return m.group(1).strip() if m else ""


def _body_preamble(body: str) -> str:
    """Title + metadata lines before the first ## / ### section."""
    m = re.search(r"(?m)^#{2,3} ", body)
    if not m:
        return body.strip()
    return body[: m.start()].strip()


def _iter_body_sections(body: str) -> list[tuple[str, str]]:
    """All ## / ### sections in file order — mirrors content-repo markdown."""
    pattern = re.compile(r"(?m)^(#{2,3})\s+(.+?)\s*\n")
    matches = list(pattern.finditer(body))
    sections: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections.append((m.group(2).strip(), body[start:end].strip()))
    return sections


def _section_content_by_heading_prefix(
    sections: list[tuple[str, str]], *prefixes: str
) -> str:
    for heading, content in sections:
        for prefix in prefixes:
            if heading == prefix or heading.startswith(prefix):
                return content
    return ""


def _hooks_section(body: str, sections: list[tuple[str, str]]) -> str:
    text = _section_content_by_heading_prefix(
        sections, "Hook (elegir 1)", "Hooks (elegir 1)", "Hook", "Hooks"
    )
    if text:
        return text
    for heading in (
        "Hook (elegir 1)",
        "Hooks (elegir 1)",
        "Hook",
        "Hooks",
    ):
        text = _section(body, heading)
        if text:
            return text
    return ""


def _load_channel_md(path) -> ChannelCopy | None:
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(raw)
    title_m = re.search(r"^# .+ — (.+)$", body, re.MULTILINE)
    status = (fm.get("status") or "?").lower()
    preamble = _body_preamble(body)
    sections = _iter_body_sections(body)
    post = _section(body, "Post (copiar a LinkedIn — sin link en cuerpo)") or _section(
        body, "Post"
    )
    return ChannelCopy(
        name=title_m.group(1).strip() if title_m else path.stem,
        path_label=rel_to_content(path),
        status=status,
        data_gated=status == "data-gated" or "data-gate" in body.lower(),
        preamble=preamble,
        sections=sections,
        hooks=_hooks_section(body, sections),
        post=post,
        comment=_section(body, "Primer comentario"),
        hashtags=_section(body, "Hashtags"),
        checklist=_section_content_by_heading_prefix(sections, "Checklist"),
        asset_hint=_section_content_by_heading_prefix(sections, "Assets"),
    )


def _slack_messages_from_channel_copy(
    copy: ChannelCopy,
    metrics: dict[str, Any],
    *,
    gated_warn: str = "",
) -> list[str]:
    """One Slack message per markdown section — exact content-repo parity."""
    messages: list[str] = []
    if copy.preamble:
        preamble = apply_live_metrics(copy.preamble, metrics)
        messages.append(
            "\n".join(
                [
                    _slack_divider(),
                    "*ENCABEZADO*",
                    _slack_divider(),
                    "",
                    slack_copy_block(preamble),
                ]
            )
        )
    for heading, content in copy.sections:
        body = apply_live_metrics(content, metrics) if content else ""
        block = slack_copy_block(body) if body else "_(sección vacía en borrador)_"
        msg_lines = [
            _slack_divider(),
            f"*{heading}*",
            _slack_divider(),
            "",
        ]
        if gated_warn and heading.startswith("Post"):
            msg_lines.append(gated_warn.rstrip())
            msg_lines.append("")
        msg_lines.append(block)
        messages.append("\n".join(msg_lines))
    return messages


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


def _load_weekday_section(path, for_date: date) -> tuple[str, str] | None:
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8")
    _, body = _parse_frontmatter(raw)
    weekday = _WEEKDAY_TWITTER.get(for_date.weekday(), "")
    if not weekday:
        return None
    for heading, content in _iter_body_sections(body):
        if not heading.startswith(weekday):
            continue
        post = content.strip()
        post = re.sub(r"^```\n?", "", post)
        post = re.sub(r"\n?```$", "", post)
        return heading, post.strip()
    return None


def _load_twitter_day(path, for_date: date) -> tuple[str, str] | None:
    return _load_weekday_section(path, for_date)


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


def channels_for_date(for_date: date, campaign_day: int) -> list[tuple[str, Any]]:
    """Return (label, path) for active channels today."""
    cal = _load_calendar_channels_module()
    if cal is not None:
        return cal.channels_for_date(for_date, campaign_day, content_root())

    return _channels_for_date_fallback(for_date, campaign_day)


def _channels_for_date_fallback(for_date: date, campaign_day: int) -> list[tuple[str, Path]]:
    """Minimal fallback when content repo calendar_channels.py is unavailable."""
    root = content_root()
    items: list[tuple[str, Path]] = []

    personal_offset = linkedin_dir() / f"Day-{campaign_day:02d}.md"
    if not personal_offset.is_file():
        alt = linkedin_dir() / f"Day-{campaign_day + PERSONAL_OFFSET:02d}.md"
        personal_offset = alt if alt.is_file() else personal_offset
    personal = _resolve_linkedin_draft(
        linkedin_dir(), "Day-*.md", personal_offset, for_date
    )
    if personal is not None:
        items.append(("LinkedIn Personal", personal))

    cday = campaign_day + COMPANY_OFFSET
    company_offset = _linkedin_company_dir() / f"Company-Day-{cday:02d}.md"
    company = _resolve_linkedin_draft(
        _linkedin_company_dir(), "Company-Day-*.md", company_offset, for_date
    )
    if company is not None:
        items.append(("LinkedIn Empresa", company))

    week_num = ((for_date - date(2026, 6, 1)).days // 7) + 1
    tw = root / "twitter" / f"tweets-w{week_num}.md"
    if tw.is_file():
        items.append((f"Twitter/X W{week_num}", tw))

    return items


def slack_copy_block(text: str) -> str:
    """Fenced Slack block — copy-paste body without mrkdwn mutation."""
    body = (text or "").strip()
    if not body:
        return ""
    safe = body.replace("```", "'''")
    return f"```\n{safe}\n```"


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
    del campaign_day  # assets live inside copy.sections from content repo
    gated_warn = ""
    if copy.data_gated and not metrics.get("gate_pass"):
        gated_warn = "⛔ _Data-gated — NO publicar hasta gate abierto._\n"

    lines = [
        f"━━━ *{label}* · `{copy.path_label}` ━━━",
        gated_warn.rstrip(),
        f"Estado: `{copy.status}`" + (" · data-gated" if copy.data_gated else ""),
        "_Borrador completo — mismas secciones que en content repo._",
        "",
    ]
    if copy.preamble:
        lines += [
            "*ENCABEZADO*",
            "",
            slack_copy_block(apply_live_metrics(copy.preamble, metrics)),
            "",
        ]
    for heading, content in copy.sections:
        body = apply_live_metrics(content, metrics) if content else ""
        lines += [f"*{heading}*", ""]
        if body:
            lines += [slack_copy_block(body), ""]
        else:
            lines += ["_(sección vacía)_", ""]

    return [ln for ln in lines if ln is not None]


def _single_channel_slack_parts(
    label: str,
    path,
    *,
    for_date: date,
    metrics: dict[str, Any],
    campaign_day: int,
) -> list[str]:
    """Slack body lines for one GTM channel (no gate intro)."""
    pub_date = format_publish_date(for_date)
    r_header = ricardo_header(label, for_date).rstrip()
    if label.startswith("LinkedIn") or label in ("DEV.to", "Hacker News") or label.startswith("Reddit"):
        copy = _load_channel_md(path)
        if copy:
            return [r_header, *_channel_blocks(label, copy, metrics, campaign_day=campaign_day)]
    if label.startswith("Twitter") or label.startswith("WhatsApp") or label.startswith("Instagram"):
        section = _load_weekday_section(path, for_date)
        if section:
            heading, post = section
            post = apply_live_metrics(post, metrics)
            return [
                r_header,
                f"━━━ *{label}* · `{rel_to_content(path)}` ━━━",
                "",
                f"*{heading}*",
                "",
                slack_copy_block(post),
                "",
            ]
    raw = path.read_text(encoding="utf-8")
    _, body = _parse_frontmatter(raw)
    excerpt = body.strip()
    if len(excerpt) > 2000:
        excerpt = excerpt[:2000] + "\n\n… _(ver archivo completo)_"
    return [
        r_header,
        f"━━━ *{label}* · `{rel_to_content(path)}` ━━━",
        "",
        "*1) POST*",
        "",
        excerpt,
        "",
    ]


def _channel_delivery_preamble(
    label: str,
    *,
    for_date: date,
    metrics: dict[str, Any],
    post_utc_hour: int,
) -> list[str]:
    return [
        f"📋 *{ricardo_channel_label(label)}* · `{format_publish_date(for_date)}` · {post_utc_hour}:00 UTC",
        "",
        *gate_slack_lines(metrics),
        "",
        "*Línea moat (pegar si el post pide cifras)*",
        moat_paste_line(metrics),
        "",
    ]


def build_gtm_channel_deliveries(
    *,
    campaign_day: int,
    for_date: date,
    metrics: dict[str, Any],
    post_utc_hour: int,
) -> tuple[str, list[GtmChannelDelivery]]:
    """Summary → #publicaciones; copy → canal Slack de cada red."""
    from slack_notify import (
        channel_publicaciones,
        channel_threads,
        slack_channel_for_gtm_label,
    )

    pub_date = format_publish_date(for_date)
    channel_items = channels_for_date(for_date, campaign_day)
    mirror_threads = os.getenv("SLACK_MIRROR_TWITTER_TO_THREADS", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )

    summary = [
        f"📋 *RICARDO — ÍNDICE PUBLICACIONES* · *{pub_date}*",
        f"Hora sugerida: *{post_utc_hour}:00 UTC*",
        "",
        *gate_slack_lines(metrics),
        "",
    ]
    if not channel_items:
        summary.append("⚠️ Sin borradores activos para hoy en content repo.")
        summary.append("")
        return "\n".join(summary), []

    summary.append("*Canales hoy* _(cada red = varios mensajes: contexto → post → comentario)_")
    for label, path in channel_items:
        ch = slack_channel_for_gtm_label(label) or channel_publicaciones()
        summary.append(f"• *{label}* → `{rel_to_content(path)}` · Slack `{ch}`")
    summary += [
        "",
        "*Línea moat (si el post pide cifras)*",
        moat_paste_line_slack(metrics),
        "",
        f"_Cerrar GTM:_ `cd cli-market-content && {publish_close_command(for_date)}`",
        "",
        build_publish_checklist_message(
            campaign_day=campaign_day,
            for_date=for_date,
            gate_pass=bool(metrics.get("gate_pass")),
        ),
    ]

    deliveries: list[GtmChannelDelivery] = []
    for label, path in channel_items:
        channel_id = slack_channel_for_gtm_label(label) or channel_publicaciones()
        msgs = _build_channel_slack_messages(
            label,
            path,
            for_date=for_date,
            metrics=metrics,
            campaign_day=campaign_day,
            post_utc_hour=post_utc_hour,
        )
        deliveries.append(
            GtmChannelDelivery(label=label, channel_id=channel_id, messages=msgs)
        )
        if mirror_threads and label.startswith("Twitter"):
            deliveries.append(
                GtmChannelDelivery(
                    label="Threads (mirror X)",
                    channel_id=channel_threads(),
                    messages=[
                        "🧵 *THREADS* — mismo copy que X. Adapta longitud/formato si hace falta.",
                        *msgs[1:],
                    ],
                )
            )

    return "\n".join(summary), deliveries


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
        body_parts.extend(
            _single_channel_slack_parts(
                label,
                path,
                for_date=for_date,
                metrics=metrics,
                campaign_day=campaign_day,
            )
        )

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