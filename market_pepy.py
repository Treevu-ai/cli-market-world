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
PRO_TIME_RANGE = (os.getenv("PEPY_PRO_TIME_RANGE") or "ONE_YEAR").strip().upper()
DAILY_SERIES_DAYS = int(os.getenv("PEPY_DAILY_SERIES_DAYS", "14"))

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
    until: date | None = None,
) -> tuple[int, dict[str, int]]:
    total = 0
    by_version: dict[str, int] = {}
    for day_str, versions in downloads.items():
        if not isinstance(versions, dict):
            continue
        day = _parse_day(day_str)
        if day is None:
            continue
        if since and day < since:
            continue
        if until and day > until:
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


def _top_versions(by_version: dict[str, int], *, limit: int = 5) -> list[dict[str, Any]]:
    ranked = sorted(by_version.items(), key=lambda x: x[1], reverse=True)
    return [{"version": ver, "downloads": count} for ver, count in ranked[:limit]]


def _daily_series(
    downloads: dict[str, dict[str, int]],
    *,
    days: int = DAILY_SERIES_DAYS,
    end: date | None = None,
) -> list[dict[str, Any]]:
    """Zero-filled daily totals (organic/no-CI series when fed Pro data)."""
    end_day = end or date.today()
    start_day = end_day - timedelta(days=max(1, days) - 1)
    by_day: dict[str, int] = {}
    for day_str, versions in downloads.items():
        if not isinstance(versions, dict):
            continue
        day = _parse_day(day_str)
        if day is None or day < start_day or day > end_day:
            continue
        by_day[day_str[:10]] = by_day.get(day_str[:10], 0) + sum(int(v or 0) for v in versions.values())

    series: list[dict[str, Any]] = []
    cursor = start_day
    while cursor <= end_day:
        ds = cursor.isoformat()
        series.append({"date": ds, "downloads": by_day.get(ds, 0)})
        cursor += timedelta(days=1)
    return series


def _ci_share_pct(raw_30d: int, no_ci_30d: int | None) -> float | None:
    if no_ci_30d is None or raw_30d <= 0:
        return None
    return round(max(0.0, (raw_30d - no_ci_30d) / raw_30d * 100), 1)


def _pro_downloads_path(project: str, *, include_ci: bool) -> str:
    flag = "true" if include_ci else "false"
    return (
        f"/service-api/v1/pro/projects/{project}/downloads"
        f"?timeRange={PRO_TIME_RANGE}&includeCIDownloads={flag}"
    )


def _merge_daily_series(series_list: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    by_date: dict[str, int] = {}
    for series in series_list:
        for point in series:
            if not isinstance(point, dict):
                continue
            ds = str(point.get("date") or "")[:10]
            if not ds:
                continue
            by_date[ds] = by_date.get(ds, 0) + int(point.get("downloads") or 0)
    return [{"date": ds, "downloads": by_date[ds]} for ds in sorted(by_date)]


def _merge_top_versions(lists: list[list[dict[str, Any]]], *, limit: int = 5) -> list[dict[str, Any]]:
    merged: dict[str, int] = {}
    for lst in lists:
        for item in lst:
            if not isinstance(item, dict):
                continue
            ver = str(item.get("version") or "")
            if not ver:
                continue
            merged[ver] = merged.get(ver, 0) + int(item.get("downloads") or 0)
    return _top_versions(merged, limit=limit)


def pepy_summary(*, project: str | None = None, force: bool = False) -> dict[str, Any]:
    """Aggregate Pepy stats for a PyPI project.

    Window metrics (7d/30d) prefer Pepy Pro with CI filtered out; raw v2 totals kept for CI share.
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

    downloads_raw = base.get("downloads") if isinstance(base.get("downloads"), dict) else {}
    today = date.today()
    last_7_raw, _ = _sum_downloads(downloads_raw, since=today - timedelta(days=6))
    last_30_raw, by_ver_raw_30 = _sum_downloads(downloads_raw, since=today - timedelta(days=29))
    last_1_raw, _ = _sum_downloads(downloads_raw, since=today)

    pro = _fetch_json(_pro_downloads_path(proj, include_ci=False))
    downloads_no_ci: dict[str, dict[str, int]] = {}
    pro_ok = False
    if isinstance(pro, dict) and isinstance(pro.get("downloads"), dict):
        downloads_no_ci = pro["downloads"]
        pro_ok = True

    last_7_no_ci, _ = _sum_downloads(downloads_no_ci, since=today - timedelta(days=6))
    last_30_no_ci, by_ver_no_ci_30 = _sum_downloads(downloads_no_ci, since=today - timedelta(days=29))
    last_1_no_ci, _ = _sum_downloads(downloads_no_ci, since=today)

    use_pro = pro_ok and bool(downloads_no_ci)
    last_7 = last_7_no_ci if use_pro else last_7_raw
    last_30 = last_30_no_ci if use_pro else last_30_raw
    last_1 = last_1_no_ci if use_pro else last_1_raw
    by_ver_30 = by_ver_no_ci_30 if use_pro else by_ver_raw_30

    meta = base.get("metadata") if isinstance(base.get("metadata"), dict) else {}
    out.update(
        {
            "ok": True,
            "total_downloads": int(base.get("total_downloads") or 0),
            "downloads_last_24h": last_1,
            "downloads_last_7d": last_7,
            "downloads_last_30d": last_30,
            "downloads_last_7d_raw": last_7_raw,
            "downloads_last_30d_raw": last_30_raw,
            "downloads_last_7d_no_ci": last_7_no_ci if use_pro else None,
            "downloads_last_30d_no_ci": last_30_no_ci if use_pro else None,
            "ci_share_pct_30d": _ci_share_pct(last_30_raw, last_30_no_ci if use_pro else None),
            "top_version_30d": _top_version(by_ver_30),
            "top_versions_30d": _top_versions(by_ver_30),
            "daily_series_14d": _daily_series(downloads_no_ci) if use_pro else _daily_series(downloads_raw),
            "latest_version": meta.get("latest_version"),
            "versions_tracked": len(base.get("versions") or []),
            "pro_ok": pro_ok,
            "pro_time_range": PRO_TIME_RANGE,
            "windows_source": "pro_no_ci" if use_pro else "v2_raw",
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
    ci = data.get("ci_share_pct_30d")
    ci_txt = f" · CI {ci:.0f}%" if isinstance(ci, (int, float)) else ""
    src = "no-CI" if data.get("windows_source") == "pro_no_ci" else "raw"
    return (
        f"PyPI (Pepy {src}): {total:,} total · {d30:,} 30d · {d7:,} 7d"
        f"{ci_txt} · top 30d: {ver}"
    )


def pepy_multi_summary(*, projects: list[str] | None = None, force: bool = False) -> dict[str, Any]:
    """Fetch stats for multiple PyPI projects and return combined aggregates + per-project detail."""
    projs = projects or pypi_projects()
    packages: dict[str, dict[str, Any]] = {}
    any_ok = False
    agg_total = 0
    agg_24h = 0
    agg_7d = 0
    agg_30d = 0
    agg_7d_raw = 0
    agg_30d_raw = 0
    agg_7d_no_ci = 0
    agg_30d_no_ci = 0
    daily_parts: list[list[dict[str, Any]]] = []
    version_parts: list[list[dict[str, Any]]] = []
    fetched_at = datetime.now(timezone.utc).isoformat()

    for p in projs:
        data = pepy_summary(project=p, force=force)
        packages[p] = data
        if not data.get("ok"):
            continue
        any_ok = True
        agg_total += int(data.get("total_downloads") or 0)
        agg_24h += int(data.get("downloads_last_24h") or 0)
        agg_7d += int(data.get("downloads_last_7d") or 0)
        agg_30d += int(data.get("downloads_last_30d") or 0)
        agg_7d_raw += int(data.get("downloads_last_7d_raw") or 0)
        agg_30d_raw += int(data.get("downloads_last_30d_raw") or 0)
        no_ci_7 = data.get("downloads_last_7d_no_ci")
        no_ci_30 = data.get("downloads_last_30d_no_ci")
        if no_ci_7 is not None:
            agg_7d_no_ci += int(no_ci_7)
        if no_ci_30 is not None:
            agg_30d_no_ci += int(no_ci_30)
        series = data.get("daily_series_14d")
        if isinstance(series, list):
            daily_parts.append(series)
        versions = data.get("top_versions_30d")
        if isinstance(versions, list):
            version_parts.append(versions)

    has_no_ci = any(
        isinstance(d, dict) and d.get("downloads_last_30d_no_ci") is not None for d in packages.values()
    )

    combined: dict[str, Any] = {
        "ok": any_ok,
        "projects": projs,
        "total_downloads": agg_total,
        "downloads_last_24h": agg_24h,
        "downloads_last_7d": agg_7d,
        "downloads_last_30d": agg_30d,
        "downloads_last_7d_raw": agg_7d_raw,
        "downloads_last_30d_raw": agg_30d_raw,
        "downloads_last_7d_no_ci": agg_7d_no_ci if has_no_ci else None,
        "downloads_last_30d_no_ci": agg_30d_no_ci if has_no_ci else None,
        "ci_share_pct_30d": _ci_share_pct(agg_30d_raw, agg_30d_no_ci if has_no_ci else None),
        "daily_series_14d": _merge_daily_series(daily_parts) if daily_parts else [],
        "top_versions_30d": _merge_top_versions(version_parts) if version_parts else [],
        "pro_time_range": PRO_TIME_RANGE,
        "windows_source": "pro_no_ci"
        if has_no_ci
        else ("v2_raw" if any_ok else None),
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
