"""Pepy.tech PyPI download stats — server-side only (PEPY_API_KEY)."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from typing import Any

PEPY_BASE = "https://api.pepy.tech"
# Per-project caches (support multiple PyPI packages: cli-market-core + cli-market-world)
_CACHE: dict[str, dict[str, Any]] = {}
_CACHE_AT: dict[str, float] = {}
_CACHE_TTL_S = int(os.getenv("PEPY_CACHE_TTL_S", "3600"))

DEFAULT_PYPI_PROJECTS: list[str] = ["cli-market-core", "cli-market-world"]


def _api_key() -> str:
    return (os.getenv("PEPY_API_KEY") or os.getenv("PEPYTECH_API_KEY") or "").strip()


def project_name() -> str:
    """Single project (for scripts / backward compat). Defaults to cli-market-world."""
    return (os.getenv("PEPY_PROJECT") or "cli-market-world").strip().lower()


def pypi_projects() -> list[str]:
    """List of PyPI projects to track for Adoption Index (combined traction)."""
    env = os.getenv("PEPY_PROJECTS")
    if env:
        return [x.strip().lower() for x in env.split(",") if x.strip()]
    return list(DEFAULT_PYPI_PROJECTS)


def _fetch_json(path: str) -> dict[str, Any] | list[Any] | None:
    key = _api_key()
    if not key:
        return None
    url = f"{PEPY_BASE}{path}"
    req = urllib.request.Request(
        url,
        headers={
            "X-API-Key": key,
            "Accept": "application/json",
            "User-Agent": "CLI-Market-Pepy/1 (+https://cli-market.dev)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError:
        return None
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None


def _parse_day(value: str) -> date | None:
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _sum_downloads(
    downloads: dict[str, dict[str, int]],
    *,
    since: date | None = None,
) -> tuple[int, dict[str, int]]:
    total = 0
    by_version: dict[str, int] = {}
    for day_str, versions in downloads.items():
        if not isinstance(versions, dict):
            continue
        day = _parse_day(day_str)
        if since and day and day < since:
            continue
        for ver, count in versions.items():
            n = int(count or 0)
            total += n
            by_version[ver] = by_version.get(ver, 0) + n
    return total, by_version


def _top_version(by_version: dict[str, int]) -> str | None:
    if not by_version:
        return None
    return max(by_version.items(), key=lambda x: x[1])[0]


def pepy_summary(*, project: str | None = None, force: bool = False) -> dict[str, Any]:
    """Aggregate Pepy stats for a (or the configured) PyPI project.
    project: explicit project name. If None, falls back to PEPY_PROJECT or "cli-market-world".
    """
    proj = (project or project_name()).strip().lower()
    now = time.time()
    if not force and proj in _CACHE and (now - _CACHE_AT.get(proj, 0.0)) < _CACHE_TTL_S:
        return dict(_CACHE[proj])

    out: dict[str, Any] = {
        "project": proj,
        "configured": bool(_api_key()),
        "source": "pepy.tech",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    if not out["configured"]:
        out["ok"] = False
        out["message"] = "PEPY_API_KEY not set"
        return out

    base = _fetch_json(f"/api/v2/projects/{proj}?includeMetadata=true")
    if not isinstance(base, dict):
        out["ok"] = False
        out["message"] = "pepy fetch failed"
        return out

    downloads = base.get("downloads") if isinstance(base.get("downloads"), dict) else {}
    today = date.today()
    last_7, _ = _sum_downloads(downloads, since=today - timedelta(days=6))
    last_30, by_ver_30 = _sum_downloads(downloads, since=today - timedelta(days=29))
    last_1, _ = _sum_downloads(downloads, since=today)

    pro = _fetch_json(
        f"/service-api/v1/pro/projects/{proj}/downloads"
        "?timeRange=THREE_MONTHS&includeCIDownloads=false"
    )
    downloads_no_ci: dict[str, dict[str, int]] = {}
    if isinstance(pro, dict) and isinstance(pro.get("downloads"), dict):
        downloads_no_ci = pro["downloads"]
    last_30_no_ci, _ = _sum_downloads(downloads_no_ci, since=today - timedelta(days=29))

    meta = base.get("metadata") if isinstance(base.get("metadata"), dict) else {}
    out.update(
        {
            "ok": True,
            "total_downloads": int(base.get("total_downloads") or 0),
            "downloads_last_24h": last_1,
            "downloads_last_7d": last_7,
            "downloads_last_30d": last_30,
            "downloads_last_30d_no_ci": last_30_no_ci or None,
            "top_version_30d": _top_version(by_ver_30),
            "latest_version": meta.get("latest_version"),
            "versions_tracked": len(base.get("versions") or []),
        }
    )

    _CACHE[proj] = dict(out)
    _CACHE_AT[proj] = now
    return dict(out)


def pepy_briefing_line() -> str:
    """One-line summary for ops briefings."""
    data = pepy_summary()
    if not data.get("ok"):
        return "PyPI (Pepy): no configurado o sin datos."
    total = data.get("total_downloads") or 0
    d30 = data.get("downloads_last_30d") or 0
    d7 = data.get("downloads_last_7d") or 0
    ver = data.get("top_version_30d") or "—"
    return f"PyPI (Pepy): {total:,} total · {d30:,} últimos 30d · {d7:,} 7d · top versión 30d: {ver}"


def pepy_multi_summary(*, projects: list[str] | None = None, force: bool = False) -> dict[str, Any]:
    """Fetch stats for multiple PyPI projects and return combined aggregates + per-project detail.
    Used by Adoption Index to make total PyPI traction (core + world) visible and pull the numbers out.
    """
    projs = projects or pypi_projects()
    packages: dict[str, dict[str, Any]] = {}
    any_ok = False
    agg_total = 0
    agg_24h = 0
    agg_7d = 0
    agg_30d = 0
    agg_30d_no_ci = 0
    fetched_at = datetime.now(timezone.utc).isoformat()

    for p in projs:
        data = pepy_summary(project=p, force=force)
        packages[p] = data
        if data.get("ok"):
            any_ok = True
            agg_total += int(data.get("total_downloads") or 0)
            agg_24h += int(data.get("downloads_last_24h") or 0)
            agg_7d += int(data.get("downloads_last_7d") or 0)
            agg_30d += int(data.get("downloads_last_30d") or 0)
            no_ci = data.get("downloads_last_30d_no_ci")
            if no_ci is not None:
                agg_30d_no_ci += int(no_ci)

    combined: dict[str, Any] = {
        "ok": any_ok,
        "projects": projs,
        "total_downloads": agg_total,
        "downloads_last_24h": agg_24h,
        "downloads_last_7d": agg_7d,
        "downloads_last_30d": agg_30d,
        "downloads_last_30d_no_ci": agg_30d_no_ci or None if any(
            isinstance(d, dict) and d.get("downloads_last_30d_no_ci") for d in packages.values()
        ) else None,
        "fetched_at": fetched_at,
    }

    return {
        "ok": any_ok,
        "source": "pepy.tech (multi)",
        "projects": projs,
        "combined": combined,
        "packages": packages,
        "fetched_at": fetched_at,
    }
