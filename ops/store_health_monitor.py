#!/usr/bin/env python3
"""
Store Health Monitor — P3: identificar stores stale e impacto en cobertura.

Calcula un health_score continuo (0–100) por store, clasifica su estado
(healthy / degraded / stale / dead), cuantifica el impacto de cobertura
por país y línea, y envía alerta a Slack cuando hay stores stale/dead.

Uso:
  python ops/store_health_monitor.py              # reporte consola
  python ops/store_health_monitor.py --slack      # reporte + alerta Slack
  python ops/store_health_monitor.py --dry-run    # solo datos, sin Slack
  python ops/store_health_monitor.py --json       # salida JSON pura
  python ops/store_health_monitor.py --alert-only # solo si hay degradación

Integración:
  - Cron: cada 4h (alineado al ciclo del colector)
  - Makefile: make store-health
  - GitHub Action: .github/workflows/content-automation.yml
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
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
    import urllib.request as _urllib

API_BASE = os.getenv("MARKET_API_URL", "https://cli-market-production.up.railway.app")
SOURCES_HEALTH_URL = f"{API_BASE}/v1/sources/health"
DASHBOARD_URL = f"{API_BASE}/dashboard/data"

# Peso de cada store en la cobertura de su país (estimado por volumen de snapshots).
# Supermercados pesan más que hogar/moda por frecuencia de compra y número de productos.
_LINE_WEIGHT = {
    "supermercados": 1.0,
    "farmacias": 0.7,
    "electro": 0.5,
    "departamentales": 0.4,
    "hogar": 0.4,
    "moda": 0.3,
}

# Estados y umbrales
_THRESHOLDS = {
    "healthy":  {"min_pct": 80, "max_consec": 0},
    "degraded": {"min_pct": 50, "max_consec": 2},
    "stale":    {"min_pct": 20, "max_consec": 5},
    "dead":     {"min_pct":  0, "max_consec": 99},
}

_STATE_EMOJI = {"healthy": "🟢", "degraded": "🟡", "stale": "🔴", "dead": "💀"}
_STATE_ORDER = {"dead": 0, "stale": 1, "degraded": 2, "healthy": 3}


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
        req = _urllib.Request(url, headers=headers)
        with _urllib.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"[store-health] fetch error {url}: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _hours_since(ts: str | None) -> float | None:
    if not ts:
        return None
    try:
        s = ts.replace("Z", "+00:00").replace(" ", "T", 1)
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    except Exception:
        return None


def _classify_state(success_pct: float, consec_failures: int, hours_since_ok: float | None) -> str:
    # Dead override: no success in 72h
    if hours_since_ok is not None and hours_since_ok >= 72:
        return "dead"
    # Stale override: no success in 24h
    if hours_since_ok is not None and hours_since_ok >= 24:
        return "stale"
    if success_pct < 20 or consec_failures > 5:
        return "dead"
    if success_pct < 50 or consec_failures > 2:
        return "stale"
    if success_pct < 80 or consec_failures > 0:
        return "degraded"
    return "healthy"


def _health_score(success_pct: float, consec_failures: int, hours_since_ok: float | None) -> float:
    """Score 0–100: combina tasa de éxito con penalización exponencial por tiempo sin dato."""
    base = success_pct
    # Penalización por fallos consecutivos: -10 por cada fallo adicional
    consec_penalty = min(40, consec_failures * 10)
    # Penalización por tiempo sin dato fresco
    time_penalty = 0.0
    if hours_since_ok is not None:
        if hours_since_ok > 72:
            time_penalty = 40
        elif hours_since_ok > 24:
            time_penalty = 25
        elif hours_since_ok > 12:
            time_penalty = 10
        elif hours_since_ok > 6:
            time_penalty = 5
    return max(0.0, base - consec_penalty - time_penalty)


# ---------------------------------------------------------------------------
# Coverage impact
# ---------------------------------------------------------------------------

def _build_store_catalog() -> dict[str, dict]:
    """Mapa store_id → {country, line} desde el endpoint /stores."""
    data = _fetch_json(f"{API_BASE}/stores") or {}
    return data.get("stores", {})


def _compute_coverage_impact(
    stale_stores: list[str],
    all_stores: list[dict],
    catalog: dict[str, dict],
) -> dict[str, dict]:
    """
    Por cada país: cuántos stores activos hay, cuántos están stale,
    qué % de peso de cobertura se pierde.
    """
    # Agrupar stores activos por país con su peso
    country_stores: dict[str, list[dict]] = {}
    for s in all_stores:
        store_id = s.get("store", "")
        meta = catalog.get(store_id, {})
        country = meta.get("country") or s.get("country", "??")
        line = meta.get("line") or s.get("line", "supermercados")
        weight = _LINE_WEIGHT.get(line, 0.3)
        country_stores.setdefault(country, []).append({
            "store": store_id,
            "line": line,
            "weight": weight,
            "is_stale": store_id in stale_stores,
        })

    impact: dict[str, dict] = {}
    for country, stores in country_stores.items():
        total_weight = sum(s["weight"] for s in stores)
        stale_weight = sum(s["weight"] for s in stores if s["is_stale"])
        stale_list = [s["store"] for s in stores if s["is_stale"]]
        coverage_loss_pct = round(stale_weight / total_weight * 100, 1) if total_weight > 0 else 0
        severity = (
            "critical" if coverage_loss_pct >= 30
            else "high" if coverage_loss_pct >= 15
            else "medium" if coverage_loss_pct >= 5
            else "low" if coverage_loss_pct > 0
            else "none"
        )
        impact[country] = {
            "total_stores": len(stores),
            "stale_stores": stale_list,
            "coverage_loss_pct": coverage_loss_pct,
            "severity": severity,
        }

    return {k: v for k, v in impact.items() if v["coverage_loss_pct"] > 0}


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def build_report() -> dict[str, Any]:
    sources_data = _fetch_json(SOURCES_HEALTH_URL)
    if not sources_data:
        # Fallback: extraer store_health del dashboard
        dash = _fetch_json(DASHBOARD_URL) or {}
        raw_stores = dash.get("store_health", [])
        stale_list = dash.get("kpis", {}).get("stale_stores", [])
    else:
        raw_stores = sources_data.get("stores", [])
        stale_list = []

    catalog = _build_store_catalog()

    scored: list[dict] = []
    stale_stores: list[str] = list(stale_list)

    for s in raw_stores:
        store_id = s.get("store", "")
        success_pct = float(s.get("success_pct", 0))
        consec = int(s.get("consecutive_failures", 0))
        last_ok = s.get("last_success")
        hours = _hours_since(last_ok)

        state = _classify_state(success_pct, consec, hours)
        score = _health_score(success_pct, consec, hours)

        meta = catalog.get(store_id, {})
        country = meta.get("country") or s.get("country", "??")
        line = meta.get("line") or s.get("line", "?")

        entry = {
            "store": store_id,
            "country": country,
            "line": line,
            "health_score": round(score, 1),
            "state": state,
            "success_pct": success_pct,
            "consecutive_failures": consec,
            "hours_since_last_ok": round(hours, 1) if hours is not None else None,
            "last_success": last_ok,
        }
        scored.append(entry)
        if state in ("stale", "dead") and store_id not in stale_stores:
            stale_stores.append(store_id)

    # Si no obtuvimos stores del endpoint, usar la lista del dashboard
    if not scored and stale_stores:
        for sid in stale_stores:
            meta = catalog.get(sid, {})
            scored.append({
                "store": sid,
                "country": meta.get("country", "??"),
                "line": meta.get("line", "?"),
                "health_score": 0.0,
                "state": "stale",
                "success_pct": 0,
                "consecutive_failures": None,
                "hours_since_last_ok": None,
                "last_success": None,
            })

    scored.sort(key=lambda x: (
        _STATE_ORDER.get(x["state"], 3),
        x["health_score"],
        x["store"],
    ))

    coverage_impact = _compute_coverage_impact(stale_stores, scored, catalog)

    by_state: dict[str, int] = {}
    for s in scored:
        by_state[s["state"]] = by_state.get(s["state"], 0) + 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_monitored": len(scored),
            "by_state": by_state,
            "stale_stores": stale_stores,
            "countries_affected": list(coverage_impact.keys()),
        },
        "stores": scored,
        "coverage_impact": coverage_impact,
        "needs_alert": bool(stale_stores),
    }


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _format_console(report: dict) -> str:
    lines: list[str] = []
    ts = report["generated_at"][:16].replace("T", " ")
    s = report["summary"]
    by_state = s["by_state"]

    lines.append(f"\n{'='*60}")
    lines.append(f"  STORE HEALTH MONITOR  [{ts} UTC]")
    lines.append(f"{'='*60}")
    lines.append(
        f"  Monitored: {s['total_monitored']}  |  "
        + "  ".join(f"{_STATE_EMOJI.get(k,'?')} {k}: {v}" for k, v in sorted(by_state.items()))
    )

    if s["stale_stores"]:
        lines.append(f"\n{'─'*60}")
        lines.append("  STORES DEGRADADOS (requieren atención)")
        lines.append(f"{'─'*60}")
        degraded = [x for x in report["stores"] if x["state"] in ("stale", "dead", "degraded")]
        for x in degraded:
            emoji = _STATE_EMOJI.get(x["state"], "?")
            h = f"{x['hours_since_last_ok']:.0f}h" if x.get("hours_since_last_ok") else "?"
            lines.append(
                f"  {emoji} {x['store']:22} [{x['country']}:{x['line']:14}]  "
                f"score={x['health_score']:5.1f}  lag={h}"
            )

    ci = report["coverage_impact"]
    if ci:
        lines.append(f"\n{'─'*60}")
        lines.append("  IMPACTO EN COBERTURA POR PAÍS")
        lines.append(f"{'─'*60}")
        for country, d in sorted(ci.items(), key=lambda x: -x[1]["coverage_loss_pct"]):
            sev = d["severity"].upper()
            stores_str = ", ".join(d["stale_stores"])
            lines.append(
                f"  {country}  -{d['coverage_loss_pct']:5.1f}%  [{sev}]  "
                f"({d['total_stores']} stores activos — stale: {stores_str})"
            )

    lines.append(f"\n{'─'*60}")
    healthy = [x for x in report["stores"] if x["state"] == "healthy"]
    lines.append(f"  Stores healthy: {len(healthy)}/{s['total_monitored']}")
    if not s["stale_stores"]:
        lines.append("  ✓ Todos los stores operativos")
    lines.append(f"{'='*60}\n")
    return "\n".join(lines)


def _format_slack(report: dict) -> str:
    s = report["summary"]
    ci = report["coverage_impact"]
    ts = report["generated_at"][:16].replace("T", " ")

    if not s["stale_stores"]:
        return f"✅ *Store Health* [{ts} UTC] — todos los stores operativos ({s['total_monitored']} monitoreados)"

    by_state = s["by_state"]
    state_str = " | ".join(
        f"{_STATE_EMOJI.get(k,'?')} {k.upper()}: {v}"
        for k, v in sorted(by_state.items())
        if k != "healthy"
    )

    lines = [
        f"🚨 *Store Health Alert* [{ts} UTC]",
        f"Estado: {state_str}",
        "",
        "*Stores con degradación:*",
    ]
    degraded = [x for x in report["stores"] if x["state"] in ("stale", "dead", "degraded")]
    for x in degraded:
        emoji = _STATE_EMOJI.get(x["state"], "?")
        h = f"{x['hours_since_last_ok']:.0f}h" if x.get("hours_since_last_ok") else "?"
        lines.append(f"  {emoji} `{x['store']}` [{x['country']}·{x['line']}] — lag {h}")

    if ci:
        lines.append("")
        lines.append("*Impacto en cobertura:*")
        for country, d in sorted(ci.items(), key=lambda x: -x[1]["coverage_loss_pct"]):
            sev_emoji = "🔴" if d["severity"] in ("critical","high") else "🟡"
            lines.append(
                f"  {sev_emoji} {country}: -{d['coverage_loss_pct']}% "
                f"({d['severity'].upper()}) — stale: {', '.join(d['stale_stores'])}"
            )

    lines.append("")
    lines.append(f"_Acción: revisar colector para los stores listados. "
                 f"Fuente: `{SOURCES_HEALTH_URL}`_")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Slack delivery
# ---------------------------------------------------------------------------

def _post_slack(message: str, channel_env: str = "SLACK_BITACORA_CHANNEL") -> bool:
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    channel = os.getenv(channel_env, os.getenv("SLACK_CHANNEL", "")).strip()
    if not token or not channel:
        print("[store-health] SLACK_BOT_TOKEN o canal no configurado", file=sys.stderr)
        return False
    try:
        if _HAS_HTTPX:
            r = httpx.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {token}"},
                json={"channel": channel, "text": message},
                timeout=15,
            )
            result = r.json()
        else:
            import json as _json
            payload = _json.dumps({"channel": channel, "text": message}).encode()
            req = _urllib.Request(
                "https://slack.com/api/chat.postMessage",
                data=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )
            with _urllib.urlopen(req, timeout=15) as resp:
                result = _json.loads(resp.read())
        ok = result.get("ok", False)
        if not ok:
            print(f"[store-health] Slack error: {result.get('error')}", file=sys.stderr)
        return ok
    except Exception as e:
        print(f"[store-health] Slack post failed: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Store Health Monitor — P3")
    parser.add_argument("--slack", action="store_true", help="Enviar reporte a Slack")
    parser.add_argument("--dry-run", action="store_true", help="Solo datos, sin Slack")
    parser.add_argument("--json", dest="json_out", action="store_true", help="Salida JSON")
    parser.add_argument("--alert-only", action="store_true",
                        help="Ejecutar pero postear Slack solo si hay degradación")
    args = parser.parse_args()

    report = build_report()

    if args.json_out:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(_format_console(report))

    needs_alert = report["needs_alert"]

    if not args.dry_run and (args.slack or args.alert_only):
        if needs_alert or args.slack:
            msg = _format_slack(report)
            _post_slack(msg)

    # Exit code 1 si hay stores stale/dead (útil en CI)
    return 1 if needs_alert else 0


if __name__ == "__main__":
    raise SystemExit(main())
