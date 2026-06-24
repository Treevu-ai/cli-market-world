#!/usr/bin/env python3
"""
Pro Conversion Audit — P2: segmentar los Pro requests no convertidos.

Analiza el funnel de adopción para identificar usuarios que solicitaron Pro
pero no activaron, los segmenta por causa probable y calcula un score de
probabilidad de conversión para priorizar el outreach.

Uso:
  python ops/pro_conversion_audit.py              # reporte consola
  python ops/pro_conversion_audit.py --slack      # reporte + resumen Slack
  python ops/pro_conversion_audit.py --json       # salida JSON pura
  python ops/pro_conversion_audit.py --days 60    # ventana de análisis

Segmentos (por delta entre register y pro_request):
  HOT   < 1 día  → intención inmediata → causa probable: fricción checkout
  WARM  1–7 días → evaluación activa   → causa probable: precio o feature gap
  COLD  > 7 días → contempladores      → causa probable: timing / no urgente

Score de conversión (0–100):
  + Búsquedas antes del request (+20 si >= 3)
  + Onboarding completo (+15)
  + Request < 24h de registro (+25 — alta intención)
  + Request en horario laboral 9–18h (+10)
  - Tiempo transcurrido desde request (decae -5 por semana)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ops"))

try:
    from load_env import load_repo_env
    load_repo_env()
except Exception:
    pass

try:
    import httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False

API_BASE = os.getenv("MARKET_API_URL", "https://cli-market-production.up.railway.app")
ADOPTION_URL = f"{API_BASE}/analytics/adoption"
FUNNEL_URL = f"{API_BASE}/analytics/funnel"


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def _fetch_json(url: str, timeout: int = 45) -> dict | None:
    token = os.getenv("MARKET_API_TOKEN", "").strip()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        if _HAS_HTTPX:
            r = httpx.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.json()
        import urllib.request as _urllib
        req = _urllib.Request(url, headers=headers)
        with _urllib.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"[pro-audit] fetch error {url}: {e}", file=sys.stderr)
        return None


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        s = ts.replace("Z", "+00:00").replace(" ", "T", 1)
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _conversion_score(user: dict, now: datetime) -> int:
    """Score 0–100: probabilidad de conversión en próximos 14 días."""
    score = 30  # base

    registered_at = _parse_ts(user.get("registered_at"))
    request_pro_at = _parse_ts(user.get("request_pro_at"))

    if request_pro_at and registered_at:
        delta_h = (request_pro_at - registered_at).total_seconds() / 3600
        if delta_h < 24:
            score += 25  # intención inmediata
        elif delta_h < 72:
            score += 10

        # Request en horario laboral (UTC-5 LATAM ≈ 14–23 UTC)
        req_hour = request_pro_at.hour
        if 14 <= req_hour <= 23:
            score += 10

    if user.get("has_search"):
        score += 10
    if user.get("has_onboarding_complete"):
        score += 15

    # Decaimiento por tiempo desde el request
    if request_pro_at:
        weeks_since = (now - request_pro_at).days / 7
        score -= min(30, int(weeks_since) * 5)

    return max(0, min(100, score))


def _segment(delta_hours: float | None) -> str:
    if delta_hours is None:
        return "unknown"
    if delta_hours < 24:
        return "HOT"
    if delta_hours < 168:  # 7 días
        return "WARM"
    return "COLD"


def _segment_cause(segment: str) -> str:
    return {
        "HOT":     "fricción checkout — el flujo de pago tiene un quiebre",
        "WARM":    "precio o feature gap — evalúa pero algo lo detiene",
        "COLD":    "timing — no estaba listo, posible nurture sequence",
        "unknown": "sin datos suficientes",
    }[segment]


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def build_audit(days: int = 30) -> dict[str, Any]:
    now = datetime.now(timezone.utc)

    # Intentar endpoint de funnel detallado (requiere auth admin)
    funnel_data = _fetch_json(f"{FUNNEL_URL}?days={days}")
    users_raw: list[dict] = []
    if funnel_data and "users" in funnel_data:
        users_raw = funnel_data["users"]

    # Fallback: usar endpoint de adopción agregado
    adoption_data = _fetch_json(f"{ADOPTION_URL}?days={days}") or {}

    agg = adoption_data.get("funnel", adoption_data)
    total_installs = agg.get("install", agg.get("installs", 0))
    total_register = agg.get("register", agg.get("registrations", 0))
    total_search = agg.get("first_search", 0)
    total_pro_req = agg.get("request_pro", 0)
    total_activated = agg.get("activated", 0)
    total_unconverted = max(0, total_pro_req - total_activated)

    # Segmentación por usuario (si tenemos datos per-user)
    segmented: list[dict] = []
    for u in users_raw:
        req_ts = _parse_ts(u.get("request_pro_at"))
        reg_ts = _parse_ts(u.get("registered_at"))
        act_ts = _parse_ts(u.get("activated_at"))

        if not req_ts:
            continue  # no pidió Pro
        if act_ts:
            continue  # ya activó — excluir

        delta_h = (req_ts - reg_ts).total_seconds() / 3600 if reg_ts else None
        seg = _segment(delta_h)
        score = _conversion_score(u, now)

        weeks_since_req = (now - req_ts).days / 7 if req_ts else None

        segmented.append({
            "username": u.get("username"),
            "segment": seg,
            "cause": _segment_cause(seg),
            "conversion_score": score,
            "registered_at": u.get("registered_at"),
            "request_pro_at": u.get("request_pro_at"),
            "delta_register_to_request_hours": round(delta_h, 1) if delta_h is not None else None,
            "weeks_since_request": round(weeks_since_req, 1) if weeks_since_req else None,
            "has_search": u.get("has_search", False),
            "has_onboarding_complete": u.get("has_onboarding_complete", False),
            "sources": u.get("sources", []),
        })

    # Ordenar por score descendente (prioridad de outreach)
    segmented.sort(key=lambda x: (-x["conversion_score"], x.get("request_pro_at") or ""))

    # Conteos por segmento (tanto de datos per-user como estimado si no hay)
    seg_counts: dict[str, int] = {"HOT": 0, "WARM": 0, "COLD": 0, "unknown": 0}
    for u in segmented:
        seg_counts[u["segment"]] = seg_counts.get(u["segment"], 0) + 1

    # Si no tenemos datos per-user, estimamos distribución por benchmarks industria
    estimated = not bool(segmented)
    if estimated and total_unconverted > 0:
        seg_counts = {
            "HOT":  int(total_unconverted * 0.30),
            "WARM": int(total_unconverted * 0.50),
            "COLD": int(total_unconverted * 0.20),
        }

    # Tasa de conversión actual y objetivo
    conv_rate_current = round(total_activated / total_pro_req * 100, 1) if total_pro_req > 0 else 0
    conv_rate_target = 22.0  # objetivo P2: cerrar ≥12 de 48 en 30 días

    return {
        "generated_at": now.isoformat(),
        "window_days": days,
        "funnel_aggregate": {
            "installs_30d": total_installs,
            "registrations": total_register,
            "first_search": total_search,
            "pro_requests": total_pro_req,
            "activated": total_activated,
            "unconverted_pro_requests": total_unconverted,
            "conversion_rate_pct": conv_rate_current,
            "conversion_target_pct": conv_rate_target,
            "gap_pp": round(conv_rate_target - conv_rate_current, 1),
        },
        "segments": {
            "HOT":  {"count": seg_counts["HOT"],  "cause": _segment_cause("HOT"),  "action": "Fix checkout UX — simplificar pago, reducir pasos"},
            "WARM": {"count": seg_counts["WARM"], "cause": _segment_cause("WARM"), "action": "Survey 5 preguntas — precio / feature gap / otra razón"},
            "COLD": {"count": seg_counts.get("COLD", 0), "cause": _segment_cause("COLD"), "action": "Nurture sequence — caso de uso + ROI en 2 semanas"},
        },
        "estimated_segmentation": estimated,
        "top_prospects": segmented[:20],  # top 20 por score para outreach manual
    }


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _fmt_console(report: dict) -> str:
    lines: list[str] = []
    ts = report["generated_at"][:16].replace("T", " ")
    fa = report["funnel_aggregate"]
    segs = report["segments"]

    lines.append(f"\n{'='*65}")
    lines.append(f"  PRO CONVERSION AUDIT  [{ts} UTC]  (ventana: {report['window_days']}d)")
    lines.append(f"{'='*65}")

    lines.append(f"\n  FUNNEL ACTUAL")
    lines.append(f"  {'Installs (30d)':<30} {fa['installs_30d']:>6}")
    lines.append(f"  {'Registrations':<30} {fa['registrations']:>6}")
    lines.append(f"  {'First search':<30} {fa['first_search']:>6}")
    lines.append(f"  {'Pro requests':<30} {fa['pro_requests']:>6}")
    lines.append(f"  {'Activated (pagaron)':<30} {fa['activated']:>6}")
    lines.append(f"  {'Unconverted Pro requests':<30} {fa['unconverted_pro_requests']:>6}  ← TARGET")
    lines.append(f"")
    lines.append(f"  Conversión actual:  {fa['conversion_rate_pct']}%")
    lines.append(f"  Objetivo P2:        {fa['conversion_target_pct']}%")
    lines.append(f"  Gap a cerrar:       +{fa['gap_pp']} pp en 30 días")

    lines.append(f"\n{'─'*65}")
    lines.append(f"  SEGMENTACIÓN POR CAUSA")
    lines.append(f"{'─'*65}")
    if report.get("estimated_segmentation"):
        lines.append(f"  [Nota: segmentación estimada — sin datos per-user disponibles]")

    seg_labels = {"HOT": "🔥 HOT", "WARM": "♨️  WARM", "COLD": "🧊 COLD"}
    for seg, data in segs.items():
        lines.append(f"\n  {seg_labels.get(seg, seg)} ({data['count']} usuarios)")
        lines.append(f"    Causa: {data['cause']}")
        lines.append(f"    Acción: {data['action']}")

    prospects = report.get("top_prospects", [])
    if prospects:
        lines.append(f"\n{'─'*65}")
        lines.append(f"  TOP {len(prospects)} PROSPECTS PARA OUTREACH (por score)")
        lines.append(f"{'─'*65}")
        lines.append(f"  {'Usuario':<22} {'Seg':<6} {'Score':>5}  {'Δ reg→req':<12} {'Sem.desde req'}")
        for p in prospects[:15]:
            dh = f"{p['delta_register_to_request_hours']:.0f}h" if p.get('delta_register_to_request_hours') else "?"
            ws = f"{p['weeks_since_request']:.1f}w" if p.get('weeks_since_request') else "?"
            lines.append(
                f"  {str(p['username'] or '?'):<22} {p['segment']:<6} {p['conversion_score']:>4}   {dh:<12} {ws}"
            )

    lines.append(f"\n{'='*65}\n")
    return "\n".join(lines)


def _fmt_slack(report: dict) -> str:
    fa = report["funnel_aggregate"]
    segs = report["segments"]
    ts = report["generated_at"][:16].replace("T", " ")

    lines = [
        f"📊 *Pro Conversion Audit* [{ts} UTC]",
        f"",
        f"*Funnel:* {fa['installs_30d']} installs → {fa['registrations']} registros → {fa['pro_requests']} Pro requests → {fa['activated']} pagaron",
        f"*Sin convertir:* {fa['unconverted_pro_requests']} usuarios | Conversión actual: {fa['conversion_rate_pct']}% → objetivo: {fa['conversion_target_pct']}%",
        f"",
        f"*Segmentos:*",
    ]
    emoji = {"HOT": "🔥", "WARM": "♨️", "COLD": "🧊"}
    for seg, data in segs.items():
        lines.append(f"  {emoji.get(seg,'?')} *{seg}* ({data['count']} usuarios) — {data['action']}")

    prospects = report.get("top_prospects", [])
    if prospects:
        lines.append(f"")
        lines.append(f"*Top 5 para outreach inmediato:*")
        for p in prospects[:5]:
            lines.append(f"  • `{p['username']}` — score {p['conversion_score']} | seg {p['segment']}")

    return "\n".join(lines)


def _post_slack(message: str) -> bool:
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    channel = os.getenv("SLACK_BITACORA_CHANNEL", os.getenv("SLACK_CHANNEL", "")).strip()
    if not token or not channel:
        print("[pro-audit] Slack no configurado", file=sys.stderr)
        return False
    try:
        if _HAS_HTTPX:
            r = httpx.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {token}"},
                json={"channel": channel, "text": message},
                timeout=15,
            )
            return r.json().get("ok", False)
    except Exception as e:
        print(f"[pro-audit] Slack error: {e}", file=sys.stderr)
    return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Pro Conversion Audit — P2")
    parser.add_argument("--days", type=int, default=30, help="Ventana de análisis en días")
    parser.add_argument("--slack", action="store_true", help="Postear resumen a Slack")
    parser.add_argument("--json", dest="json_out", action="store_true", help="Salida JSON")
    args = parser.parse_args()

    report = build_audit(days=args.days)

    if args.json_out:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(_fmt_console(report))

    if args.slack:
        _post_slack(_fmt_slack(report))

    # Exit 1 si hay unconverted por encima del umbral (útil en CI)
    return 1 if report["funnel_aggregate"]["unconverted_pro_requests"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
