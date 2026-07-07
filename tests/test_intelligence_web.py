"""Tests for routers/intelligence_web.py — public Commerce Pulse embed/landing.

Ported from cli-market-backend alongside market_brief.py/market_pulse.py/
intelligence_web.py — these are public, unauthenticated endpoints (no
require_api_key), only rate-limited via check_rate_limit.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from market_core import ensure_db_initialized
from market_server import app

ensure_db_initialized()
client = TestClient(app)


def test_intelligence_landing_returns_html():
    r = client.get("/intelligence?country=PE")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "THIS WEEK IN LATAM COMMERCE" in r.text


def test_embed_commerce_pulse_returns_html():
    r = client.get("/embed/commerce-pulse?country=PE")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "THIS WEEK IN LATAM COMMERCE" in r.text


def test_embed_sets_frame_ancestors_csp():
    r = client.get("/embed/commerce-pulse?country=PE")
    assert r.status_code == 200
    csp = r.headers.get("content-security-policy", "")
    assert "frame-ancestors" in csp
    assert "cli-market.dev" in csp


def test_intelligence_data_json_returns_expected_keys():
    r = client.get("/public/intelligence/data?country=PE")
    assert r.status_code == 200
    data = r.json()
    for key in ("country", "week", "headline", "title", "kpis", "moat", "executive_highlights"):
        assert key in data
    assert data["country"] == "PE"


def test_intelligence_embed_snippet_returns_pasteable_html():
    r = client.get("/public/intelligence/embed-snippet")
    assert r.status_code == 200
    assert "iframe" in r.text
    assert "/embed/commerce-pulse" in r.text


def test_intelligence_data_defaults_to_pe_without_country_param():
    r = client.get("/public/intelligence/data")
    assert r.status_code == 200
    assert r.json()["country"] == "PE"
