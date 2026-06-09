"""Command & Control morning cron endpoint."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from fastapi.testclient import TestClient
from market_server import app

client = TestClient(app)


def test_admin_cron_command_control_requires_admin(monkeypatch):
    import server_deps

    monkeypatch.setenv("MARKET_API_TOKEN", "admin-test-token")
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "admin-test-token")
    r = client.post("/admin/cron/command-control")
    assert r.status_code == 401


def test_admin_cron_command_control_posts(monkeypatch):
    import server_deps

    monkeypatch.setenv("MARKET_API_TOKEN", "admin-test-token")
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "admin-test-token")
    monkeypatch.setattr(
        "command_control_daily.publish_command_control",
        lambda remote=True, brief=True, save=True: {
            "ok": True,
            "posted": True,
            "remote": remote,
            "brief": brief,
            "preview": "Command & Control test",
        },
    )

    r = client.post(
        "/admin/cron/command-control",
        headers={"Authorization": "Bearer admin-test-token"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["posted"] is True
    assert body["brief"] is True


def test_admin_cron_command_control_full_checklist(monkeypatch):
    import server_deps

    monkeypatch.setenv("MARKET_API_TOKEN", "admin-test-token")
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "admin-test-token")
    calls: list[bool] = []

    def _fake_publish(*, remote=True, brief=True, save=True):
        calls.append(brief)
        return {"ok": True, "posted": True, "remote": remote, "brief": brief, "preview": "full"}

    monkeypatch.setattr("command_control_daily.publish_command_control", _fake_publish)

    r = client.post(
        "/admin/cron/command-control?full=true",
        headers={"Authorization": "Bearer admin-test-token"},
    )
    assert r.status_code == 200
    assert calls == [False]