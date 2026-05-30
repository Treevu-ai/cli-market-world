"""Tests for ops/sync_content_template.py."""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_sync_skips_assets_and_existing_days(tmp_path, monkeypatch):
    target = tmp_path / "content"
    target.mkdir()
    (target / "linkedin").mkdir()
    (target / "linkedin" / "assets" / "day-01").mkdir(parents=True)
    existing_png = target / "linkedin" / "assets" / "day-01" / "day-01-linkedin.png"
    existing_png.write_bytes(b"keep-me")
    day01 = target / "linkedin" / "Day-01.md"
    day01.write_text("published local copy", encoding="utf-8")

    monkeypatch.setenv("CLI_MARKET_CONTENT_DIR", str(target))
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.setattr(sys, "argv", ["sync_content_template.py"])

    import ops.sync_content_template as sync_mod

    rc = sync_mod.main()
    assert rc == 0
    assert existing_png.read_bytes() == b"keep-me"
    assert "published local copy" in day01.read_text(encoding="utf-8")
    assert (target / "metrics" / "price-pulse-2026-W22.md").is_file()


def test_sync_dry_run_only_prefix(tmp_path, monkeypatch, capsys):
    target = tmp_path / "content"
    target.mkdir()
    monkeypatch.setenv("CLI_MARKET_CONTENT_DIR", str(target))
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.setenv("PYTHONPATH", str(REPO_ROOT / "ops"))

    argv = ["sync_content_template.py", "--dry-run", "--only", "metrics"]
    monkeypatch.setattr(sys, "argv", argv)

    import ops.sync_content_template as sync_mod

    rc = sync_mod.main()
    assert rc == 0
    out = capsys.readouterr().out
    assert "would copy:" in out or "Sync:" in out
    assert "linkedin/Day-" not in out or "metrics" in out
