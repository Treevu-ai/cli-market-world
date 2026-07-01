#!/usr/bin/env python3
"""Production Acceptance Matrix (PAM) — CLI Market.

Runs structured smoke/E2E checks against production (or staging) touchpoints.

Usage:
    python ops/production_acceptance.py
    python ops/production_acceptance.py --phase public --tier 1
    python ops/production_acceptance.py --phase user,admin --tier 2
    python ops/production_acceptance.py --phase admin --tier 3 --include-destructive
    python ops/production_acceptance.py --dry-run
    python ops/production_acceptance.py --sync-json
    python ops/production_acceptance.py --include-destructive

Environment:
    MARKET_API_URL          API base (default: pam_matrix defaults)
    MARKET_API_TOKEN        Admin bearer (admin phase)
    MARKET_USER_TOKEN       Optional sk- key; else auto-registers via /auth/register
    PAM_LANDING_URL         Override landing base
    PAM_REPORT_DIR          Report output dir (default: ops/reports)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OPS_DIR = Path(__file__).resolve().parent
PHASE_ORDER = ("public", "landing", "user", "admin", "post")
MATRIX_YAML = OPS_DIR / "pam_matrix.yaml"
MATRIX_JSON = OPS_DIR / "pam_matrix.json"
DEFAULT_REPORT_DIR = OPS_DIR / "reports"
ROTATION_LOCAL = OPS_DIR / ".rotation-local.txt"


def _load_admin_token() -> str:
    token = (os.getenv("MARKET_API_TOKEN") or "").strip()
    if token:
        return token
    if ROTATION_LOCAL.exists():
        for line in ROTATION_LOCAL.read_text(encoding="utf-8").splitlines():
            if line.startswith("MARKET_API_TOKEN="):
                return line.split("=", 1)[1].strip()
    return ""

ALLOWED_API_HOSTS = (
    "cli-market-api.fly.dev",
    "localhost",
    "127.0.0.1",
)
ALLOWED_LANDING_HOSTS = (
    "cli-market.dev",
    "www.cli-market.dev",
    "localhost",
    "127.0.0.1",
)


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "PyYAML required to read pam_matrix.yaml. "
            "pip install pyyaml  OR  run with --sync-json then use pam_matrix.json"
        ) from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_matrix(path: Path | None = None) -> dict:
    if path and path.exists():
        if path.suffix in (".yaml", ".yml"):
            return _load_yaml(path)
        return json.loads(path.read_text(encoding="utf-8"))
    if MATRIX_JSON.exists():
        return json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
    if MATRIX_YAML.exists():
        return _load_yaml(MATRIX_YAML)
    raise FileNotFoundError(f"No matrix found in {OPS_DIR}")


def sync_json_from_yaml() -> None:
    data = _load_yaml(MATRIX_YAML)
    MATRIX_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {MATRIX_JSON}")


def validate_base_url(url: str, *, landing: bool = False) -> None:
    allowed = ALLOWED_LANDING_HOSTS if landing else ALLOWED_API_HOSTS
    if url.startswith("https://"):
        if not any(h in url for h in allowed):
            raise ValueError(f"URL host not in allowlist: {url}")
        return
    if url.startswith("http://localhost") or url.startswith("http://127.0.0.1"):
        return
    raise ValueError(f"Refusing non-HTTPS URL: {url}")


def get_by_path(obj: Any, dotted: str) -> Any:
    cur = obj
    for part in dotted.split("."):
        if part.isdigit():
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur


def render_template(value: Any, ctx: dict[str, Any]) -> Any:
    if isinstance(value, str):
        def repl(m: re.Match) -> str:
            key = m.group(1)
            if key.startswith("threshold."):
                th = ctx.get("_thresholds", {})
                return str(th.get(key.split(".", 1)[1], m.group(0)))
            if key == "run_id":
                return ctx.get("run_id", "")
            try:
                return str(get_by_path(ctx, key))
            except (KeyError, IndexError, TypeError):
                return str(ctx.get(key, m.group(0)))

        return re.sub(r"\{\{([^}]+)\}\}", repl, value)
    if isinstance(value, dict):
        return {k: render_template(v, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [render_template(v, ctx) for v in value]
    return value


def capture_values(data: dict, rules: dict[str, str], ctx: dict[str, Any]) -> None:
    for key, path in rules.items():
        try:
            ctx[key] = get_by_path(data, path)
        except (KeyError, IndexError, TypeError):
            ctx[f"_missing_{key}"] = True


def build_url(case: dict, matrix: dict, ctx: dict[str, Any]) -> str:
    base_key = case.get("base", "api")
    if base_key == "landing":
        base = os.getenv("PAM_LANDING_URL", matrix["defaults"].get("landing_base", ""))
    else:
        base = os.getenv("MARKET_API_URL", matrix["defaults"].get("api_base", ""))
    validate_base_url(base, landing=(base_key == "landing"))
    path = render_template(case.get("path", "/"), ctx)
    return base.rstrip("/") + path


def auth_header(case: dict, ctx: dict[str, Any]) -> dict[str, str]:
    auth = case.get("auth", "none")
    if auth == "none":
        return {}
    if auth == "admin":
        token = os.getenv("MARKET_API_TOKEN", "")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}
    if auth in ("user", "api_key"):
        token = os.getenv("MARKET_USER_TOKEN") or ctx.get("user_api_key", "")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}
    return {}


def check_expect(
    expect: dict,
    *,
    status: int,
    headers: dict[str, str],
    body_text: str,
    data: Any,
    latency_ms: float,
    ctx: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    exp_status = expect.get("status")
    if exp_status is not None and status != exp_status:
        errors.append(f"status {status} != {exp_status}")
    status_in = expect.get("status_in")
    if status_in and status not in status_in:
        errors.append(f"status {status} not in {status_in}")

    ct_need = expect.get("content_type_contains")
    if ct_need:
        ct = headers.get("Content-Type", "")
        if ct_need.lower() not in ct.lower():
            errors.append(f"content-type '{ct}' missing '{ct_need}'")

    body_need = expect.get("body_contains")
    if body_need and body_need not in body_text:
        errors.append(f"body missing substring: {body_need!r}")

    max_lat = expect.get("latency_ms_max")
    if max_lat is not None:
        max_val = float(render_template(max_lat, ctx))
        if latency_ms > max_val:
            errors.append(f"latency {latency_ms:.0f}ms > {max_val:.0f}ms")

    # JSON assertions only apply to 2xx — allowed 4xx/5xx in status_in may omit a body.
    if status < 200 or status >= 300:
        return errors

    if isinstance(data, list):
        min_count = expect.get("json_min_count")
        if min_count is not None and len(data) < int(min_count):
            errors.append(f"json list len {len(data)} < {min_count}")
        if expect.get("json") or expect.get("json_has") or expect.get("json_min"):
            errors.append("expected JSON object, got list")
        return errors

    if not isinstance(data, dict):
        if expect.get("json") or expect.get("json_has") or expect.get("json_min") or expect.get("json_path_min_count"):
            errors.append("expected JSON object")
        return errors

    for key, val in (expect.get("json") or {}).items():
        if data.get(key) != val:
            errors.append(f"json.{key}={data.get(key)!r} != {val!r}")

    for key in expect.get("json_has") or []:
        if key not in data:
            errors.append(f"json missing key: {key}")

    for dotted, minimum in (expect.get("json_min") or {}).items():
        try:
            actual = get_by_path(data, dotted)
            min_val = float(render_template(minimum, ctx)) if isinstance(minimum, str) else minimum
            if actual is None or float(actual) < float(min_val):
                errors.append(f"json.{dotted}={actual!r} < {min_val}")
        except (KeyError, TypeError, ValueError):
            errors.append(f"json.{dotted} missing or not numeric")

    for dotted, maximum in (expect.get("json_max") or {}).items():
        try:
            actual = get_by_path(data, dotted)
            max_val = float(render_template(maximum, ctx)) if isinstance(maximum, str) else maximum
            if actual is None or float(actual) > float(max_val):
                errors.append(f"json.{dotted}={actual!r} > {max_val}")
        except (KeyError, TypeError, ValueError):
            errors.append(f"json.{dotted} missing or not numeric")

    min_count = expect.get("json_min_count")
    if min_count is not None:
        if not isinstance(data, list) or len(data) < int(min_count):
            errors.append(f"json list len {len(data) if isinstance(data, list) else 'n/a'} < {min_count}")

    for dotted, minimum in (expect.get("json_path_min_count") or {}).items():
        try:
            actual = get_by_path(data, dotted)
            if not isinstance(actual, dict) or len(actual) < int(minimum):
                errors.append(f"json.{dotted} count < {minimum}")
        except (KeyError, TypeError):
            errors.append(f"json.{dotted} missing")

    return errors


def _http_request(
    url: str,
    method: str,
    headers: dict[str, str],
    data_bytes: bytes | None,
    timeout: float,
) -> tuple[int, dict[str, str], str, Any, float]:
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency_ms = (time.perf_counter() - t0) * 1000
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
            resp_headers = {k: v for k, v in resp.headers.items()}
    except urllib.error.HTTPError as exc:
        latency_ms = (time.perf_counter() - t0) * 1000
        raw = exc.read().decode("utf-8", errors="replace")
        status = exc.code
        resp_headers = {k: v for k, v in exc.headers.items()}
    else:
        parsed: Any = None
        if raw.strip():
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = None
        return status, resp_headers, raw, parsed, latency_ms
    parsed = None
    if raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
    return status, resp_headers, raw, parsed, latency_ms


def _poll_collector_batch(
    case: dict,
    matrix: dict,
    ctx: dict[str, Any],
    *,
    url: str,
    headers: dict[str, str],
    timeout: float,
    expect: dict,
) -> tuple[int, dict[str, str], str, Any, float, list[str]]:
    poll = case.get("poll_until_match") or case.get("poll_after_destructive") or {}
    interval = float(poll.get("interval_s", 8))
    max_wait = float(poll.get("max_wait_s", 180))
    deadline = time.monotonic() + max_wait
    last: tuple[int, dict[str, str], str, Any, float] = (0, {}, "", {}, 0.0)
    while time.monotonic() < deadline:
        status, resp_headers, raw, parsed, latency_ms = _http_request(
            url, "GET", headers, None, timeout
        )
        last = (status, resp_headers, raw, parsed, latency_ms)
        data = parsed if isinstance(parsed, dict) else {}
        if data.get("in_progress") or data.get("status") == "running":
            time.sleep(interval)
            continue
        errs = check_expect(
            expect,
            status=status,
            headers=resp_headers,
            body_text=raw,
            data=data,
            latency_ms=latency_ms,
            ctx=ctx,
        )
        if not errs:
            return status, resp_headers, raw, parsed, latency_ms, []
        time.sleep(interval)
    _, _, raw, parsed, latency_ms = last
    data = parsed if isinstance(parsed, dict) else {}
    errs = check_expect(
        expect,
        status=last[0],
        headers=last[1],
        body_text=raw,
        data=data,
        latency_ms=latency_ms,
        ctx=ctx,
    )
    if not errs:
        return last[0], last[1], raw, parsed, latency_ms, []
    errs.append(f"poll timed out after {max_wait:.0f}s waiting for collector batch")
    return last[0], last[1], raw, parsed, latency_ms, errs


def run_case(
    case: dict,
    matrix: dict,
    ctx: dict[str, Any],
    *,
    include_destructive: bool,
    phases: set[str] | None = None,
) -> dict[str, Any]:
    cid = case["id"]
    result: dict[str, Any] = {
        "id": cid,
        "name": case.get("name", cid),
        "tier": case.get("tier", 2),
        "phase": case.get("phase", "public"),
        "status": "PASS",
        "latency_ms": None,
        "http_status": None,
        "errors": [],
        "notes": case.get("notes"),
    }

    if case.get("destructive") and not include_destructive:
        result["status"] = "SKIP"
        result["skip_reason"] = "destructive (use --include-destructive)"
        return result

    if case.get("after_destructive") and not include_destructive:
        result["status"] = "SKIP"
        result["skip_reason"] = "after_destructive (use --include-destructive)"
        return result

    max_tier = int(ctx.get("_max_tier", 2))
    if case.get("skip_if_post_phase") and phases and "post" in phases and max_tier < 3:
        result["status"] = "SKIP"
        result["skip_reason"] = "skip_if_post_phase (batch validated in post.health_collector_batch)"
        return result

    for env_key in case.get("skip_if_env_missing") or []:
        if not os.getenv(env_key):
            result["status"] = "SKIP"
            result["skip_reason"] = f"missing env {env_key}"
            return result

    for req in case.get("requires") or []:
        if not ctx.get(f"_done_{req}"):
            result["status"] = "SKIP"
            result["skip_reason"] = f"requires {req}"
            return result

    for key in case.get("skip_if_missing") or []:
        if ctx.get(f"_missing_{key}") or key not in ctx:
            result["status"] = "SKIP"
            result["skip_reason"] = f"missing context {key}"
            return result

    auth = case.get("auth", "none")
    if auth == "admin" and not os.getenv("MARKET_API_TOKEN"):
        result["status"] = "SKIP"
        result["skip_reason"] = "MARKET_API_TOKEN not set"
        return result
    if auth in ("user", "api_key") and not (os.getenv("MARKET_USER_TOKEN") or ctx.get("user_api_key")):
        result["status"] = "SKIP"
        result["skip_reason"] = "no user token (register failed?)"
        return result

    url = build_url(case, matrix, ctx)
    method = case.get("method", "GET").upper()
    headers = {"User-Agent": "CLI-Market-PAM/1.0", "Accept": "*/*"}
    headers.update(auth_header(case, ctx))

    body = case.get("body")
    data_bytes = None
    if body is not None:
        body = render_template(body, ctx)
        data_bytes = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    timeout = float(case.get("timeout_s") or matrix["defaults"].get("timeout_s", 30))
    latency_cap = case.get("expect", {}).get("latency_ms_max")
    if latency_cap is not None:
        try:
            cap_ms = float(render_template(latency_cap, ctx))
            timeout = max(timeout, cap_ms / 1000.0 + 5.0)
        except (TypeError, ValueError):
            pass
    if case["id"] == "public.dashboard_html":
        timeout = max(timeout, 60.0)

    expect = render_template(case.get("expect") or {}, ctx)
    use_poll = bool(case.get("poll_until_match") or case.get("poll_after_destructive"))

    try:
        if use_poll and method == "GET":
            status, resp_headers, raw, parsed, latency_ms, errs = _poll_collector_batch(
                case, matrix, ctx, url=url, headers=headers, timeout=timeout, expect=expect
            )
        else:
            status, resp_headers, raw, parsed, latency_ms = _http_request(
                url, method, headers, data_bytes, timeout
            )
            errs = check_expect(
                expect,
                status=status,
                headers=resp_headers,
                body_text=raw,
                data=parsed if isinstance(parsed, dict) else (parsed if isinstance(parsed, list) else {}),
                latency_ms=latency_ms,
                ctx=ctx,
            )
    except Exception as exc:
        result["status"] = "FAIL"
        result["errors"] = [str(exc)[:200]]
        return result

    result["latency_ms"] = round(latency_ms, 1)
    result["http_status"] = status
    if use_poll:
        result["polled"] = True

    if errs:
        result["status"] = "FAIL"
        result["errors"] = errs
    else:
        ctx[f"_done_{cid}"] = True
        if case.get("destructive") and include_destructive:
            ctx["_destructive_ran"] = True
        if isinstance(parsed, dict) and case.get("capture"):
            capture_values(parsed, case["capture"], ctx)

    return result


def ensure_user_api_key(ctx: dict[str, Any], matrix: dict, cases: list[dict]) -> None:
    """Populate user_api_key from MARKET_USER_TOKEN when user-phase cases need it.

    Registration now requires email + OTP so auto-registration against live prod
    is not possible. Set MARKET_USER_TOKEN=sk-... before running user-phase PAM.
    """
    if os.getenv("MARKET_USER_TOKEN") or ctx.get("user_api_key"):
        if os.getenv("MARKET_USER_TOKEN"):
            ctx["user_api_key"] = os.environ["MARKET_USER_TOKEN"]
        return
    needs_user = any(c.get("auth") in ("user", "api_key") for c in cases)
    if needs_user:
        print(
            "  note: user-phase tests require MARKET_USER_TOKEN=sk-... "
            "(registration is a 2-step OTP flow on prod — auto-bootstrap unavailable)",
            file=sys.stderr,
        )


def should_auto_post(phases: set[str], tier: int) -> bool:
    """Add post phase for batch validation; skip for tier 3 admin-only destructive runs."""
    if tier < 2:
        return False
    if tier >= 3 and phases <= {"admin"}:
        return False
    return True


def _console_print(text: str) -> None:
    """Print safely on Windows consoles that lack Unicode (e.g. cp1252)."""
    try:
        print(text)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(text.encode(enc, errors="replace").decode(enc, errors="replace"))


def print_manual_checklist(matrix: dict, max_tier: int | None = None) -> None:
    items = matrix.get("manual_checklist") or []
    if not items:
        return
    _console_print("\n-- Manual checklist (not automated) --")
    for item in items:
        item_tier = int(item.get("tier", 2))
        if max_tier is not None and item_tier > max_tier:
            continue
        _console_print(f"  [T{item_tier}] {item['id']}: {item['name']}")
        if item.get("steps"):
            _console_print(f"       {item['steps']}")


def print_summary(results: list[dict], matrix: dict, args: argparse.Namespace) -> int:
    by_status: dict[str, int] = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1

    print("\n-- PAM Summary --")
    for phase in sorted({r["phase"] for r in results}):
        phase_rows = [r for r in results if r["phase"] == phase]
        p = sum(1 for r in phase_rows if r["status"] == "PASS")
        f = sum(1 for r in phase_rows if r["status"] == "FAIL")
        s = sum(1 for r in phase_rows if r["status"] == "SKIP")
        print(f"  {phase:8}  PASS {p}  FAIL {f}  SKIP {s}")

    print(f"\n  TOTAL     PASS {by_status.get('PASS', 0)}  FAIL {by_status.get('FAIL', 0)}  SKIP {by_status.get('SKIP', 0)}")

    fails = [r for r in results if r["status"] == "FAIL"]
    if fails:
        print("\n-- Failures --")
        for r in fails:
            print(f"  FAIL {r['id']}: {', '.join(r['errors'])}")

    if args.phase == "manual" or "manual" in (args.phase or ""):
        print_manual_checklist(matrix, max_tier=args.tier)

    tier1_fails = [r for r in results if r["status"] == "FAIL" and r.get("tier") == 1]
    return 1 if tier1_fails else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI Market Production Acceptance Matrix")
    parser.add_argument("--matrix", type=Path, default=None, help="pam_matrix.yaml or .json")
    parser.add_argument("--phase", default="public,user,landing", help="Comma phases or 'all'")
    parser.add_argument(
        "--tier",
        type=int,
        default=1,
        help="Max tier: 1=release core, 2=extended+post, 3=destructive admin+manual payments",
    )
    parser.add_argument("--include-destructive", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sync-json", action="store_true")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    if args.sync_json:
        sync_json_from_yaml()
        return 0

    matrix = load_matrix(args.matrix)
    phases_raw = args.phase
    if phases_raw == "all":
        phases = {"public", "user", "admin", "landing", "post", "manual"}
    else:
        phases = {p.strip() for p in phases_raw.split(",")}

    if should_auto_post(phases, args.tier):
        phases.add("post")

    if "manual" in phases:
        print_manual_checklist(matrix, max_tier=args.tier)
        if phases == {"manual"}:
            return 0

    cases = [
        c for c in matrix.get("cases", [])
        if c.get("phase") in phases and int(c.get("tier", 2)) <= args.tier
    ]
    def _phase_idx(phase: str) -> int:
        try:
            return PHASE_ORDER.index(phase)
        except ValueError:
            return len(PHASE_ORDER)

    cases.sort(
        key=lambda c: (
            _phase_idx(c.get("phase", "")),
            c.get("run_order", 50),
            c.get("tier", 9),
            c.get("id", ""),
        )
    )

    ctx: dict[str, Any] = {
        "run_id": uuid.uuid4().hex[:8],
        "_thresholds": matrix.get("thresholds", {}),
        "_max_tier": args.tier,
    }

    api_base = os.getenv("MARKET_API_URL", matrix["defaults"].get("api_base", ""))
    admin_token = _load_admin_token()
    if admin_token and not os.getenv("MARKET_API_TOKEN"):
        os.environ["MARKET_API_TOKEN"] = admin_token
    print(f"PAM run {ctx['run_id']}  tier<={args.tier}  phases={','.join(sorted(phases))}")
    print(f"  API: {api_base}")
    if admin_token:
        print("  admin: MARKET_API_TOKEN loaded")

    if args.dry_run:
        for c in cases:
            print(f"  [{c.get('tier')}] {c['phase']:8} {c['method']:4} {c.get('path', '/')}  {c['id']}")
        print(f"\n{len(cases)} automated cases")
        print_manual_checklist(matrix, max_tier=args.tier)
        return 0

    ensure_user_api_key(ctx, matrix, cases)

    results: list[dict] = []
    for case in cases:
        label = f"{case['id']}"
        sys.stdout.write(f"> {label} ... ")
        sys.stdout.flush()
        res = run_case(
            case,
            matrix,
            ctx,
            include_destructive=args.include_destructive,
            phases=phases,
        )
        results.append(res)
        icon = {"PASS": "OK", "FAIL": "FAIL", "SKIP": "SKIP"}.get(res["status"], "?")
        extra = ""
        if res.get("latency_ms") is not None:
            extra = f" {res['latency_ms']:.0f}ms"
        if res.get("http_status") is not None:
            extra += f" HTTP {res['http_status']}"
        if res["status"] == "SKIP":
            extra += f" ({res.get('skip_reason', '')})"
        print(f"{icon}{extra}")

    report_dir = Path(os.getenv("PAM_REPORT_DIR", str(DEFAULT_REPORT_DIR)))
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = args.report or (report_dir / f"pam-{stamp}.json")
    report = {
        "run_id": ctx["run_id"],
        "at": datetime.now(timezone.utc).isoformat(),
        "api_base": api_base,
        "phases": sorted(phases),
        "tier_max": args.tier,
        "summary": {
            s: sum(1 for r in results if r["status"] == s)
            for s in ("PASS", "FAIL", "SKIP")
        },
        "results": results,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nReport: {report_path}")

    return print_summary(results, matrix, args)


if __name__ == "__main__":
    raise SystemExit(main())