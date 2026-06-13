#!/usr/bin/env python3
"""Reporte diario de métricas para CEO/Founder/Product Owner — CLI Market.

Dimensiones cubiertas:
  1. Producto / Adopción     — PyPI, Adoption Index, registros, búsquedas
  2. Data Moat               — snapshots, frescura, stores, cobertura
  3. Monetización / Revenue  — Pro activados, funnel, MRR proxy
  4. Infraestructura / Ops   — collector status, índice semántico, alertas
  5. GTM / Contenido         — publicaciones, canal del día, PyPI 100K plan

Envío:
  python ops/ceo_metrics_report.py              # imprime en terminal
  python ops/ceo_metrics_report.py --slack      # postea a #ceo-metrics (C0B9W7794BD)
  python ops/ceo_metrics_report.py --dry-run    # imprime sin postear
  python ops/ceo_metrics_report.py --remote     # KPIs desde producción (requiere MARKET_API_TOKEN)

Env vars:
  MARKET_API_TOKEN        — token para la API de producción
  SLACK_BOT_TOKEN         — bot de Slack (para --slack)
  DASHBOARD_DATA_URL      — override URL dashboard
  PEPY_API_KEY            — opcional, mejora datos PyPI
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

API_BASE = os.getenv(
    "MARKET_API_URL",
    "https://cli-market-production.up.railway.app",
)
MARKET_TOKEN = os.getenv("MARKET_API_TOKEN", "")
PYPI_PACKAGE = "cli-market-world"

# ── Valores esperados (north-star targets) ────────────────────────────────────

TARGETS = {
    "pypi_downloads_30d": 5_000,       # 5K installs/mes en tracción inicial
    "pypi_downloads_7d": 1_200,        # ~1.2K/sem
    "moat_total_indexed": 50_000,      # 50K snapshots en el moat
    "moat_snapshots_24h": 5_000,       # 5K nuevos snapshots/día
    "moat_stores_indexed": 38,         # 38 stores verificados activos
    "moat_coverage_7d_pct": 80.0,      # 80% stores con datos en 7d
    "moat_freshness_24h_pct": 70.0,    # 70% del moat fresco en 24h
    "index_linkage_pct": 80.0,         # 80% snapshots con identidad producto
    "adoption_score": 40,              # Adoption Index 40/100 (tracción inicial)
    "register_30d": 50,                # 50 registros/mes
    "pro_activated_30d": 5,            # 5 Pro activados/mes
    "search_per_register": 0.3,        # 30% de registros hacen búsqueda
}


# ── Fetchers ──────────────────────────────────────────────────────────────────

def _auth_headers() -> dict[str, str]:
    token = MARKET_TOKEN
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _get(path: str, *, timeout: float = 10.0) -> dict[str, Any] | None:
    headers = _auth_headers()
    if not headers:
        return None
    try:
        r = httpx.get(f"{API_BASE}{path}", headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _fetch_dashboard() -> dict[str, Any]:
    data = _get("/dashboard/data")
    return data or {}


def _fetch_funnel() -> dict[str, Any]:
    data = _get("/analytics/funnel?days=30")
    return data or {}


def _fetch_adoption() -> dict[str, Any]:
    data = _get("/analytics/adoption?days=30")
    return data or {}


def _fetch_pypi() -> dict[str, Any]:
    """Pull latest PyPI metadata (public, no auth)."""
    try:
        r = httpx.get(f"https://pypi.org/pypi/{PYPI_PACKAGE}/json", timeout=8)
        r.raise_for_status()
        info = r.json().get("info", {})
        return {"version": info.get("version", "?"), "ok": True}
    except Exception:
        return {"ok": False}


def _fetch_pepy() -> dict[str, Any]:
    """Downloads from pepy.tech (requires PEPY_API_KEY or public endpoint)."""
    pepy_key = os.getenv("PEPY_API_KEY", "").strip()
    if not pepy_key:
        # Try public endpoint (rate-limited)
        try:
            r = httpx.get(
                f"https://api.pepy.tech/api/v2/projects/{PYPI_PACKAGE}",
                timeout=8,
            )
            if r.status_code == 200:
                data = r.json()
                total = data.get("total_downloads", 0)
                return {"total": total, "ok": True}
        except Exception:
            pass
        return {"ok": False}
    try:
        r = httpx.get(
            f"https://api.pepy.tech/api/v2/projects/{PYPI_PACKAGE}",
            headers={"X-Api-Key": pepy_key},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        return {"total": data.get("total_downloads", 0), "ok": True}
    except Exception:
        return {"ok": False}


def _content_today() -> dict[str, Any]:
    """Consulta calendar_channels para saber qué se publicó/publica hoy."""
    try:
        content_root = os.getenv("CONTENT_REPO_PATH", str(ROOT.parent / "cli-market-content"))
        sys.path.insert(0, str(Path(content_root) / "scripts"))
        from calendar_channels import channels_for_date  # type: ignore[import]

        today = date.today().isoformat()
        channels = channels_for_date(today, repo_root=content_root)
        return {"date": today, "channels": channels, "ok": True}
    except Exception:
        return {"ok": False, "channels": []}


# ── Status emoji helpers ──────────────────────────────────────────────────────

def _status(val: float | int | None, target: float | int, *, higher_is_better: bool = True) -> str:
    if val is None:
        return "❓"
    ratio = val / target if target else 0
    if higher_is_better:
        if ratio >= 0.9:
            return "✅"
        if ratio >= 0.6:
            return "⚠️"
        return "🔴"
    else:
        if ratio <= 1.1:
            return "✅"
        if ratio <= 1.5:
            return "⚠️"
        return "🔴"


def _fmt(val: Any, *, pct: bool = False, k: bool = False) -> str:
    if val is None:
        return "—"
    if pct:
        return f"{float(val):.1f}%"
    if k and isinstance(val, (int, float)) and val >= 1000:
        return f"{val/1000:.1f}K"
    if isinstance(val, float):
        return f"{val:.1f}"
    return str(val)


def _row(dimension: str, metric: str, definition: str, utility: str,
         expected: str, actual: str, status: str) -> str:
    return (
        f"{status} *{metric}*\n"
        f"   _Def:_ {definition}\n"
        f"   _Util:_ {utility}\n"
        f"   _Esperado:_ {expected} · _Real:_ *{actual}*\n"
    )


# ── Report builder ────────────────────────────────────────────────────────────

def build_report(*, remote: bool = False) -> str:
    today = date.today().strftime("%A %d/%m/%Y")
    now_utc = datetime.now(timezone.utc).strftime("%H:%M UTC")

    dash = _fetch_dashboard() if remote else {}
    funnel = _fetch_funnel() if remote else {}
    adoption = _fetch_adoption() if remote else {}
    pypi = _fetch_pypi()
    pepy = _fetch_pepy()
    content = _content_today()

    kpis = dash.get("kpis", {})
    coll = dash.get("collector", {})
    moat = dash.get("moat_summary", {})
    index_data = dash.get("index", {})

    # Adoption index
    adoption_score = adoption.get("score") or dash.get("adoption_index", {}).get("score")
    adoption_grade = adoption.get("grade") or dash.get("adoption_index", {}).get("grade", "—")

    # Funnel
    funnel_kpis = funnel.get("kpis", {})
    act = funnel_kpis.get("activation", {})
    rev = funnel_kpis.get("revenue", {})
    register_30d = int(act.get("register", 0) or 0)
    first_search_30d = int(act.get("first_search", 0) or 0)
    search_per_register = act.get("search_per_register")
    pro_activated_30d = int(rev.get("activated", 0) or 0)

    # Moat
    total_indexed = int(kpis.get("total_indexed", 0) or 0)
    snapshots_24h = int(kpis.get("snapshots_24h", 0) or 0)
    stores_indexed = int(kpis.get("stores_indexed", 0) or 0)
    coverage_7d = float(kpis.get("coverage_7d_pct", 0) or 0)
    fresh_24h_pct = float(kpis.get("fresh_24h_pct", 0) or 0)
    collector_status = coll.get("status", "?") if coll else "?"
    collector_stale = bool(moat.get("collector_stale", False))

    # Index semántico
    linkage_pct = float((index_data or {}).get("linkage_pct", 0) or 0)
    index_size = int((index_data or {}).get("registry_size", 0) or 0)

    # PyPI
    pypi_version = pypi.get("version", "?")
    pepy_total = pepy.get("total") if pepy.get("ok") else None

    # Alerts from dashboard
    alerts = [a for a in dash.get("alerts", []) if a.get("severity") in ("critical", "warn")][:3]

    # Content GTM
    channels_today = content.get("channels", [])

    lines: list[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    source_tag = "🔴 *Sin datos prod (sin token)*" if not remote or not MARKET_TOKEN else "🟢 Live prod"
    lines.append(
        f"📊 *CEO Dashboard — CLI Market*\n"
        f"📅 {today} · {now_utc} · {source_tag}\n"
        f"{'─' * 42}"
    )

    # ── 1. PRODUCTO / ADOPCIÓN ─────────────────────────────────────────────────
    lines.append("\n*1️⃣  PRODUCTO / ADOPCIÓN*")

    lines.append(_row(
        "Producto", "Versión PyPI",
        "Versión publicada del paquete cli-market-world en PyPI.",
        "Indica si el release cycle está activo y en qué punto del roadmap está el producto.",
        "1.9.36",
        pypi_version,
        "✅" if pypi_version == "1.9.36" else "⚠️",
    ))

    lines.append(_row(
        "Producto", "Descargas totales PyPI",
        "Total histórico de descargas del paquete cli-market-world en PyPI (pepy.tech).",
        "North-star de adopción acumulada. Meta 100K PyPI = moat defensivo vs competencia.",
        "→ 100K (plan)",
        _fmt(pepy_total, k=True) if pepy_total else "Ver pepy.tech",
        "✅" if pepy_total and pepy_total >= 1000 else "⚠️" if pepy_total else "❓",
    ))

    lines.append(_row(
        "Adopción", "Adoption Index",
        "Score compuesto 0-100 que combina descargas PyPI, búsquedas CLI, uso MCP, y cuentas Pro. "
        "Calculado por market_adoption_index.py.",
        "KPI síntesis para el CEO: un número que responde '¿estamos creciendo?'",
        f"≥{TARGETS['adoption_score']}/100",
        f"{adoption_score:.0f}/100 ({adoption_grade})" if adoption_score else "—",
        _status(adoption_score, TARGETS["adoption_score"]),
    ))

    lines.append(_row(
        "Adopción", "Registros 30d",
        "Usuarios que completaron /auth/register en los últimos 30 días.",
        "Mide la parte alta del funnel. Bajo = GTM o DX bloqueando adquisición.",
        f"≥{TARGETS['register_30d']}",
        _fmt(register_30d) if remote else "—",
        _status(register_30d, TARGETS["register_30d"]) if remote else "❓",
    ))

    lines.append(_row(
        "Adopción", "Búsqueda/Registro (30d)",
        "% de usuarios registrados que hicieron al menos 1 búsqueda. Proxy de activación.",
        "Si es bajo (<30%), el problema es DX (onboarding). Si es alto con pocos registros, el problema es adquisición.",
        f"≥{int(TARGETS['search_per_register']*100)}%",
        _fmt(search_per_register * 100 if search_per_register else None, pct=True) if remote else "—",
        _status(search_per_register, TARGETS["search_per_register"]) if remote and search_per_register is not None else "❓",
    ))

    # ── 2. DATA MOAT ──────────────────────────────────────────────────────────
    lines.append(f"\n{'─'*42}\n*2️⃣  DATA MOAT (diferenciador defensivo)*")

    lines.append(_row(
        "Moat", "Snapshots indexados (total)",
        "Total de price snapshots únicos en la base de datos (price > 0, price < 999,999).",
        "Tamaño del moat. >50K = difícil de replicar en 6 meses. >100K = ventaja competitiva sostenida.",
        f"≥{_fmt(TARGETS['moat_total_indexed'], k=True)}",
        _fmt(total_indexed, k=True) if remote else "—",
        _status(total_indexed, TARGETS["moat_total_indexed"]) if remote else "❓",
    ))

    lines.append(_row(
        "Moat", "Snapshots frescos <24h",
        "Snapshots con queried_at en las últimas 24 horas. Mide actividad del collector.",
        "Frescura operativa. Si cae a 0: el collector falló y el moat se está 'muriendo'.",
        f"≥{_fmt(TARGETS['moat_snapshots_24h'], k=True)}/día",
        _fmt(snapshots_24h, k=True) if remote else "—",
        _status(snapshots_24h, TARGETS["moat_snapshots_24h"]) if remote else "❓",
    ))

    lines.append(_row(
        "Moat", "Stores activos",
        "Número de retailers distintos con al menos 1 snapshot en la DB.",
        "Amplitud del moat. 38 = full coverage Perú. <30 = hay stores caídos o no indexados.",
        f"≥{TARGETS['moat_stores_indexed']}",
        _fmt(stores_indexed) if remote else "—",
        _status(stores_indexed, TARGETS["moat_stores_indexed"]) if remote else "❓",
    ))

    lines.append(_row(
        "Moat", "Cobertura 7 días (%)",
        "% de stores en el catálogo con datos en los últimos 7 días.",
        "Salud del moat a mediano plazo. <70% indica stores caídos o collector intermitente.",
        f"≥{TARGETS['moat_coverage_7d_pct']}%",
        _fmt(coverage_7d, pct=True) if remote else "—",
        _status(coverage_7d, TARGETS["moat_coverage_7d_pct"]) if remote else "❓",
    ))

    lines.append(_row(
        "Moat", "Frescura 24h (%)",
        "% del total de snapshots que tienen queried_at < 24h. Freshness ratio.",
        "Calidad operativa. <50% = el collector no está cubriendo el catálogo completo en el ciclo diario.",
        f"≥{TARGETS['moat_freshness_24h_pct']}%",
        _fmt(fresh_24h_pct, pct=True) if remote else "—",
        _status(fresh_24h_pct, TARGETS["moat_freshness_24h_pct"]) if remote else "❓",
    ))

    coll_emoji = "✅" if collector_status == "ok" and not collector_stale else "🔴" if collector_stale else "⚠️"
    coll_label = f"{collector_status}" + (" ⚡ STALE" if collector_stale else "")
    lines.append(_row(
        "Ops", "Estado Collector",
        "Status del daemon de recolección de precios: ok / degraded / stale / down.",
        "Operativo crítico. Si es 'stale', los precios están desactualizados y los usuarios lo notan.",
        "ok (no stale)",
        coll_label if remote else "—",
        coll_emoji if remote else "❓",
    ))

    # ── 3. MONETIZACIÓN ───────────────────────────────────────────────────────
    lines.append(f"\n{'─'*42}\n*3️⃣  MONETIZACIÓN / REVENUE*")

    lines.append(_row(
        "Revenue", "Pro activados 30d",
        "Cuentas que pasaron a tier 'pro' en los últimos 30 días (manual o PayPal).",
        "Revenue leading indicator. Target 5/mes = $195 MRR incremental (a $39/mo).",
        f"≥{TARGETS['pro_activated_30d']}",
        _fmt(pro_activated_30d) if remote else "—",
        _status(pro_activated_30d, TARGETS["pro_activated_30d"]) if remote else "❓",
    ))

    lines.append(_row(
        "Revenue", "MRR estimado",
        "Pro activados acumulados × $39/mes (proxy). No incluye churns ni enterprise.",
        "Velocímetro de ingresos. Permite proyectar runway y tomar decisiones de inversión GTM.",
        "→ $1K MRR (goal Q3)",
        f"${pro_activated_30d * 39}+ (est.)" if remote and pro_activated_30d > 0 else "pre-revenue",
        "✅" if remote and pro_activated_30d * 39 >= 1000 else "⚠️" if remote and pro_activated_30d > 0 else "❓",
    ))

    lines.append(_row(
        "Revenue", "Búsquedas primeras 30d",
        "Usuarios que hicieron su primera búsqueda CLI en los últimos 30 días.",
        "Activation metric. Búsqueda = momento de valor. Correlaciona con conversión a Pro.",
        f"≥{int(TARGETS['register_30d'] * TARGETS['search_per_register'])}",
        _fmt(first_search_30d) if remote else "—",
        _status(first_search_30d, int(TARGETS["register_30d"] * TARGETS["search_per_register"])) if remote else "❓",
    ))

    # ── 4. INFRAESTRUCTURA / OPS ──────────────────────────────────────────────
    lines.append(f"\n{'─'*42}\n*4️⃣  INFRAESTRUCTURA / OPS*")

    lines.append(_row(
        "Index", "Linkage % (índice semántico)",
        "% de price snapshots vinculados a un producto Golden Record (prod_*) en cli-market-index.",
        "Calidad del índice. Alto linkage = búsquedas más precisas, MCP tools más útiles.",
        f"≥{TARGETS['index_linkage_pct']}%",
        _fmt(linkage_pct, pct=True) if remote else "—",
        _status(linkage_pct, TARGETS["index_linkage_pct"]) if remote else "❓",
    ))

    lines.append(_row(
        "Index", "Golden Records (índice)",
        "Número de productos únicos en el índice semántico de cli-market-index.",
        "Riqueza del catálogo. Más Golden Records = mejor experiencia de búsqueda y MCP.",
        "→ 10K productos",
        _fmt(index_size, k=True) if remote and index_size else "—",
        _status(index_size, 10_000) if remote and index_size else "❓",
    ))

    if alerts and remote:
        lines.append(f"\n⚠️ *Alertas activas ({len(alerts)}):*")
        for a in alerts:
            lines.append(f"   • [{a.get('severity','?').upper()}] {a.get('message','?')}")

    # ── 5. GTM / CONTENIDO ────────────────────────────────────────────────────
    lines.append(f"\n{'─'*42}\n*5️⃣  GTM / CONTENIDO*")

    if channels_today:
        ch_str = " · ".join(channels_today)
        lines.append(f"📢 *Canales hoy:* {ch_str}")
    else:
        lines.append("📢 *Canales hoy:* no hay publicaciones programadas para hoy")

    lines.append(_row(
        "GTM", "Plan PyPI 100K",
        "Meta de 100,000 descargas totales en PyPI como indicador de defensibilidad del moat.",
        "North-star GTM. Cuando alcancemos 100K, el costo de replicar el moat supera 12 meses.",
        "100K total",
        f"{_fmt(pepy_total, k=True)} ({pepy_total/100_000*100:.1f}%)" if pepy_total else "Ver pepy.tech",
        _status(pepy_total or 0, 100_000) if pepy_total else "❓",
    ))

    # ── Footer ─────────────────────────────────────────────────────────────────
    lines.append(
        f"\n{'─'*42}\n"
        f"_Generado: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
        f"Fuente: {'prod API + PyPI' if remote else 'PyPI only (sin MARKET_API_TOKEN)'}_\n"
        f"_Para datos prod: exportar MARKET_API_TOKEN en Railway → cron diario 13:30 UTC_"
    )

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="CEO daily metrics report — CLI Market")
    parser.add_argument("--slack", action="store_true", help="Postear a #ceo-metrics (C0B9W7794BD)")
    parser.add_argument("--dry-run", action="store_true", help="Solo imprimir, no postear")
    parser.add_argument("--remote", action="store_true", help="Datos desde producción")
    args = parser.parse_args()

    text = build_report(remote=args.remote)
    print(text)

    if args.slack and not args.dry_run:
        from slack_notify import deliver_to_ceo_metrics
        deliver_to_ceo_metrics(text)
        print("\n→ Enviado a #ceo-metrics (C0B9W7794BD)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
