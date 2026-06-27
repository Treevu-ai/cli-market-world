"""P0 market mcp-setup command."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import market_cli


def test_detect_ide_cursor(monkeypatch):
    monkeypatch.delenv("WINDSURF_SESSION", raising=False)
    monkeypatch.setenv("CURSOR_TRACE_ID", "trace-1")
    assert market_cli._detect_ide() == "cursor"


def test_mcp_config_location_prefers_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    cfg_dir, cfg_path, project_level = market_cli._mcp_config_location("cursor")
    assert project_level is True
    assert Path(cfg_path).parent.name == ".cursor"
    assert Path(cfg_path).name == "mcp.json"
    assert str(tmp_path) in str(Path(cfg_path).parent)


def test_merge_mcp_config_preserves_existing_servers(tmp_path):
    cfg_path = tmp_path / "mcp.json"
    cfg_path.write_text(
        json.dumps({"mcpServers": {"other": {"command": "echo"}}}),
        encoding="utf-8",
    )
    entry = market_cli._mcp_server_entry(token="sk-test", api_url="https://api.example", ide="cursor", profile="legacy")
    merged = market_cli._merge_mcp_config(str(cfg_path), "cursor", entry)
    assert "other" in merged["mcpServers"]
    assert merged["mcpServers"]["cli-market"]["command"] == "market-mcp"
    assert merged["mcpServers"]["cli-market"]["env"]["MARKET_API_TOKEN"] == "sk-test"


def test_mcp_server_entry_vscode_stdio():
    entry = market_cli._mcp_server_entry(
        token="sk-test",
        api_url="https://api.example",
        ide="vscode",
    )
    assert entry["type"] == "stdio"
    assert entry["command"] == "market-mcp"
    assert entry["env"]["MCP_TOOL_PROFILE"] == "default"
    assert entry["env"]["MARKET_API_TOKEN"] == "sk-test"


def test_merge_mcp_config_vscode_servers_key(tmp_path):
    cfg_path = tmp_path / "mcp.json"
    cfg_path.write_text(
        json.dumps({"servers": {"other": {"type": "stdio", "command": "echo"}}}),
        encoding="utf-8",
    )
    entry = market_cli._mcp_server_entry(token="sk-test", api_url="https://api.example", ide="vscode", profile="legacy")
    merged = market_cli._merge_mcp_config(str(cfg_path), "vscode", entry)
    assert "other" in merged["servers"]
    assert merged["servers"]["cli-market"]["type"] == "stdio"
    assert merged["servers"]["cli-market"]["command"] == "market-mcp"


def test_mcp_setup_dry_run_vscode(monkeypatch, capsys):
    monkeypatch.setattr(market_cli, "get_token", lambda: "sk-dry-run-token")
    monkeypatch.setattr(
        market_cli,
        "_mcp_config_location",
        lambda ide: ("/tmp/.vscode", "/tmp/.vscode/mcp.json", True),
    )
    market_cli.cmd_mcp_setup(argparse_ns(ide="vscode", dry_run=True))
    out = capsys.readouterr().out
    assert "Dry-run" in out
    assert '"servers"' in out
    assert '"type": "stdio"' in out
    assert "market-mcp" in out


def test_resolve_mcp_token_skips_placeholder_and_demo(monkeypatch):
    monkeypatch.setattr(market_cli, "get_token", lambda: "sk-CLI-MARKET-PLACEHOLDER")
    monkeypatch.setenv("MARKET_API_TOKEN", "demo-abc")
    monkeypatch.setenv("CLI_MARKET_API_KEY", "sk-real-admin-token")
    assert market_cli._resolve_mcp_token() == "sk-real-admin-token"


def test_write_mcp_config_legacy_profile(tmp_path, monkeypatch):
    cfg_dir = tmp_path / ".cursor"
    cfg_path = cfg_dir / "mcp.json"
    monkeypatch.setattr(market_cli, "get_token", lambda: "sk-write-test")
    monkeypatch.setattr(
        market_cli,
        "_mcp_config_location",
        lambda ide: (str(cfg_dir), str(cfg_path), True),
    )
    result = market_cli._write_mcp_config("cursor", profile="legacy")
    saved = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert saved["mcpServers"]["cli-market"]["env"]["MCP_TOOL_PROFILE"] == "legacy"
    assert result["tool_count"] == 57


def test_write_mcp_config_creates_cursor_file(tmp_path, monkeypatch):
    cfg_dir = tmp_path / ".cursor"
    cfg_path = cfg_dir / "mcp.json"
    monkeypatch.setattr(market_cli, "get_token", lambda: "sk-write-test")
    monkeypatch.setattr(
        market_cli,
        "_mcp_config_location",
        lambda ide: (str(cfg_dir), str(cfg_path), True),
    )
    result = market_cli._write_mcp_config("cursor")
    assert cfg_path.is_file()
    saved = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert saved["mcpServers"]["cli-market"]["command"] == "market-mcp"
    assert result["cfg_path"] == str(cfg_path)


def test_mcp_setup_dry_run(monkeypatch, capsys):
    monkeypatch.setattr(market_cli, "get_token", lambda: "sk-dry-run-token")
    monkeypatch.setattr(market_cli, "_mcp_config_location", lambda ide: ("/tmp/.cursor", "/tmp/.cursor/mcp.json", True))
    market_cli.cmd_mcp_setup(argparse_ns(ide="cursor", dry_run=True))
    out = capsys.readouterr().out
    assert "Dry-run" in out
    assert "market-mcp" in out


def test_mcp_setup_writes_and_reports(monkeypatch, tmp_path):
    cfg_dir = tmp_path / ".cursor"
    cfg_path = cfg_dir / "mcp.json"
    events: list[str] = []

    monkeypatch.setattr(market_cli, "get_token", lambda: "sk-live-token")
    monkeypatch.setattr(market_cli, "_mcp_config_location", lambda ide: (str(cfg_dir), str(cfg_path), True))
    monkeypatch.setattr(market_cli, "_ping_api", lambda: (True, "200 OK (12ms)"))
    monkeypatch.setattr(
        market_cli,
        "_report_onboarding_event",
        lambda event, **kwargs: events.append(event),
    )
    market_cli.cmd_mcp_setup(argparse_ns(ide="cursor", dry_run=False))

    assert cfg_path.is_file()
    saved = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert saved["mcpServers"]["cli-market"]["command"] == "market-mcp"
    assert events == ["mcp_setup_completed"]


def argparse_ns(**kwargs):
    import argparse

    defaults = {"ide": "cursor", "dry_run": False, "profile": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)