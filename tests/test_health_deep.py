"""Tests for GET /health/deep — unified deep health check."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from market_core import ensure_db_initialized
from market_server import app

ensure_db_initialized()
client = TestClient(app)


def test_health_deep_returns_200():
    r = client.get("/health/deep")
    assert r.status_code == 200


def test_health_deep_has_status():
    r = client.get("/health/deep")
    data = r.json()
    assert "status" in data
    assert data["status"] in ("healthy", "degraded", "unhealthy")


def test_health_deep_has_checks():
    r = client.get("/health/deep")
    data = r.json()
    assert "checks" in data
    checks = data["checks"]
    assert "database" in checks


def test_health_deep_database_check():
    r = client.get("/health/deep")
    db_check = r.json()["checks"]["database"]
    assert db_check["status"] == "ok"
    assert "backend" in db_check
    assert db_check["backend"] in ("postgresql", "sqlite")


def test_health_deep_has_failures_count():
    r = client.get("/health/deep")
    data = r.json()
    assert "failures" in data
    assert isinstance(data["failures"], int)
