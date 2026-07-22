"""Tests for routers/media.py — ticket OCR and voice transcription endpoints."""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized
from market_server import app

import server_deps

ensure_db_initialized()
client = TestClient(app)

_FAKE_IMAGE = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # minimal JPEG header

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_token(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)


# ── /v1/ticket/scan ──────────────────────────────────────────────────────────

def test_ticket_scan_no_tesseract_returns_placeholder():
    """When tesseract is not installed, endpoint returns placeholder text and 200."""
    with patch("routers.media.subprocess.run", side_effect=FileNotFoundError):
        r = client.post(
            "/v1/ticket/scan",
            files={"file": ("ticket.jpg", io.BytesIO(_FAKE_IMAGE), "image/jpeg")},
            headers=_AUTH,
        )
    assert r.status_code == 200
    data = r.json()
    assert "ocr_text" in data
    assert "Tesseract" in data["ocr_text"] or data["items_matched"] == 0


def test_ticket_scan_tesseract_empty_output():
    """Tesseract returns empty output → items_detected=0, no error."""
    mock_result = MagicMock(returncode=0, stdout="")
    with patch("routers.media.subprocess.run", return_value=mock_result):
        r = client.post(
            "/v1/ticket/scan",
            files={"file": ("ticket.jpg", io.BytesIO(_FAKE_IMAGE), "image/jpeg")},
            headers=_AUTH,
        )
    assert r.status_code == 200
    data = r.json()
    assert data["items_detected"] == 0
    assert data["items_matched"] == 0
    assert data["potential_savings"] == 0.0


def test_ticket_scan_tesseract_short_lines_ignored():
    """Lines with ≤3 chars are filtered out."""
    mock_result = MagicMock(returncode=0, stdout="ab\ncd\nef")
    with patch("routers.media.subprocess.run", return_value=mock_result):
        r = client.post(
            "/v1/ticket/scan",
            files={"file": ("ticket.jpg", io.BytesIO(_FAKE_IMAGE), "image/jpeg")},
            headers=_AUTH,
        )
    assert r.status_code == 200
    assert r.json()["items_detected"] == 0


def test_ticket_scan_tesseract_failure_returncode():
    """Non-zero returncode → ocr_text='', no crash."""
    mock_result = MagicMock(returncode=1, stdout="some garbage")
    with patch("routers.media.subprocess.run", return_value=mock_result):
        r = client.post(
            "/v1/ticket/scan",
            files={"file": ("ticket.jpg", io.BytesIO(_FAKE_IMAGE), "image/jpeg")},
            headers=_AUTH,
        )
    assert r.status_code == 200
    assert r.json()["ocr_text"] == ""


# ── /v1/ticket/scan-url ──────────────────────────────────────────────────────

def test_ticket_scan_url_rejects_loopback():
    r = client.post("/v1/ticket/scan-url", json={"url": "http://127.0.0.1/image.jpg"}, headers=_AUTH)
    assert r.status_code == 400


def test_ticket_scan_url_rejects_metadata():
    r = client.post("/v1/ticket/scan-url", json={"url": "http://169.254.169.254/latest"}, headers=_AUTH)
    assert r.status_code == 400


def test_ticket_scan_url_returns_ocr_on_success():
    """With mocked fetch + no tesseract → placeholder in ocr_text."""
    with (
        patch("routers.media._fetch_public_url", return_value=_FAKE_IMAGE),
        patch("routers.media.subprocess.run", side_effect=FileNotFoundError),
    ):
        r = client.post("/v1/ticket/scan-url", json={"url": "https://example.com/ticket.jpg"}, headers=_AUTH)
    assert r.status_code == 200
    assert "ocr_text" in r.json()


# ── /v1/voice/transcribe ─────────────────────────────────────────────────────

def test_voice_transcribe_no_whisper_returns_placeholder():
    with patch("routers.media.subprocess.run", side_effect=FileNotFoundError):
        r = client.post(
            "/v1/voice/transcribe",
            files={"file": ("audio.ogg", io.BytesIO(b"fake-audio"), "audio/ogg")},
            headers=_AUTH,
        )
    assert r.status_code == 200
    data = r.json()
    assert "transcript" in data
    assert "Whisper" in data["transcript"] or "whisper" in data["transcript"].lower()
    assert data["language"] == "es"


def test_voice_transcribe_whisper_nonzero_returncode():
    mock_result = MagicMock(returncode=1, stdout="", stderr="error")
    with patch("routers.media.subprocess.run", return_value=mock_result):
        r = client.post(
            "/v1/voice/transcribe",
            files={"file": ("audio.ogg", io.BytesIO(b"fake-audio"), "audio/ogg")},
            headers=_AUTH,
        )
    assert r.status_code == 200
    data = r.json()
    assert "Transcripción" in data["transcript"] or "transcript" in data


# ── /v1/voice/transcribe-url ─────────────────────────────────────────────────

def test_voice_transcribe_url_rejects_private_ip():
    r = client.post("/v1/voice/transcribe-url", json={"url": "http://10.0.0.1/audio.ogg"}, headers=_AUTH)
    assert r.status_code == 400


def test_voice_transcribe_url_no_whisper_returns_placeholder():
    with (
        patch("routers.media._fetch_public_url", return_value=b"fake-audio"),
        patch("routers.media.subprocess.run", side_effect=FileNotFoundError),
    ):
        r = client.post("/v1/voice/transcribe-url", json={"url": "https://example.com/audio.ogg"}, headers=_AUTH)
    assert r.status_code == 200
    assert "transcript" in r.json()


# ── auth is required on all four endpoints ────────────────────────────────────

def test_ticket_scan_requires_auth():
    r = client.post(
        "/v1/ticket/scan",
        files={"file": ("ticket.jpg", io.BytesIO(_FAKE_IMAGE), "image/jpeg")},
    )
    assert r.status_code == 401


def test_ticket_scan_url_requires_auth():
    r = client.post("/v1/ticket/scan-url", json={"url": "https://example.com/ticket.jpg"})
    assert r.status_code == 401


def test_voice_transcribe_requires_auth():
    r = client.post(
        "/v1/voice/transcribe",
        files={"file": ("audio.ogg", io.BytesIO(b"fake-audio"), "audio/ogg")},
    )
    assert r.status_code == 401


def test_voice_transcribe_url_requires_auth():
    r = client.post("/v1/voice/transcribe-url", json={"url": "https://example.com/audio.ogg"})
    assert r.status_code == 401
