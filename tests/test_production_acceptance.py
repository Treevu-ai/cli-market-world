"""Regression test for ops/production_acceptance.py's content-type check.

check_expect() looked up response headers via headers.get("Content-Type")
(exact case). HTTP header names are case-insensitive (RFC 7230 §3.2), and
Starlette/FastAPI emit lowercase "content-type" on the wire, so every real
production check against public.dashboard_html failed with
"content-type '' missing 'text/html'" even though the endpoint was
correctly returning text/html — confirmed live via urllib.request against
the real production dashboard endpoint (6/6 requests returned a lowercase
"content-type" key, deterministic, not flaky).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

import production_acceptance as pam


def test_content_type_check_passes_with_lowercase_header():
    errors = pam.check_expect(
        {"status": 200, "content_type_contains": "text/html"},
        status=200,
        headers={"content-type": "text/html; charset=utf-8"},
        body_text="<html></html>",
        data={},
        latency_ms=100.0,
        ctx={},
    )
    assert errors == []


def test_content_type_check_passes_with_titlecase_header():
    errors = pam.check_expect(
        {"status": 200, "content_type_contains": "text/html"},
        status=200,
        headers={"Content-Type": "text/html; charset=utf-8"},
        body_text="<html></html>",
        data={},
        latency_ms=100.0,
        ctx={},
    )
    assert errors == []


def test_content_type_check_fails_when_header_truly_missing():
    errors = pam.check_expect(
        {"status": 200, "content_type_contains": "text/html"},
        status=200,
        headers={},
        body_text="<html></html>",
        data={},
        latency_ms=100.0,
        ctx={},
    )
    assert len(errors) == 1
    assert "content-type '' missing 'text/html'" in errors[0]


def test_content_type_check_fails_on_wrong_content_type():
    errors = pam.check_expect(
        {"status": 200, "content_type_contains": "text/html"},
        status=200,
        headers={"content-type": "application/json"},
        body_text="{}",
        data={},
        latency_ms=100.0,
        ctx={},
    )
    assert len(errors) == 1
    assert "application/json" in errors[0]
