"""Tests para ops/horeca/sync_estacion90_menu.py — sin FTP ni red real."""

import hashlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "ops" / "horeca"))

import sync_estacion90_menu as sync_mod


def test_main_dry_run_valid_json(tmp_path, capsys):
    menu = tmp_path / "menu.json"
    menu.write_text('{"store": "estacion90_pe", "categories": []}', encoding="utf-8")

    code = sync_mod.main(["--dry-run", "--local-path", str(menu)])

    assert code == 0
    assert "JSON válido" in capsys.readouterr().out


def test_main_dry_run_rejects_invalid_json(tmp_path, capsys):
    menu = tmp_path / "menu.json"
    menu.write_text("{not valid json", encoding="utf-8")

    code = sync_mod.main(["--dry-run", "--local-path", str(menu)])

    assert code == 1
    assert "no es JSON válido" in capsys.readouterr().err


def test_main_missing_local_file(tmp_path, capsys):
    code = sync_mod.main(["--dry-run", "--local-path", str(tmp_path / "missing.json")])

    assert code == 1
    assert "No existe" in capsys.readouterr().err


def test_upload_creates_missing_remote_dirs_and_stores_file(tmp_path):
    menu = tmp_path / "menu.json"
    menu.write_text('{"store": "estacion90_pe"}', encoding="utf-8")

    ftps = MagicMock()
    # cwd() raises on the first call per directory segment (segment doesn't
    # exist yet), so _ensure_remote_dir falls through to mkd() + a second cwd().
    ftps.cwd.side_effect = [
        sync_mod.ftplib.error_perm("550 no such dir"),
        None,
        sync_mod.ftplib.error_perm("550 no such dir"),
        None,
    ]

    with patch.object(sync_mod, "_connect", return_value=ftps) as connect:
        sync_mod.upload(
            menu, "public_html/api/menu.json",
            host="ftp.example.com", user="u", password="p", port=21,
        )

    connect.assert_called_once_with("ftp.example.com", "u", "p", 21)
    ftps.mkd.assert_any_call("public_html")
    ftps.mkd.assert_any_call("api")
    assert ftps.storbinary.call_args[0][0] == "STOR menu.json"
    ftps.quit.assert_called_once()


def _ok_response(content: bytes) -> httpx.Response:
    request = httpx.Request("GET", "https://estacion90.pe/api/menu.json")
    return httpx.Response(200, content=content, request=request)


def test_verify_returns_true_when_hashes_match(tmp_path):
    menu = tmp_path / "menu.json"
    content = b'{"store": "estacion90_pe"}'
    menu.write_bytes(content)

    response = _ok_response(content)
    with patch.object(sync_mod.httpx, "get", return_value=response):
        assert sync_mod.verify(menu, "https://estacion90.pe/api/menu.json", retries=1) is True


def test_verify_retries_then_fails_on_persistent_mismatch(tmp_path):
    menu = tmp_path / "menu.json"
    menu.write_bytes(b'{"store": "estacion90_pe"}')

    stale_response = _ok_response(b'{"store": "stale"}')
    with patch.object(sync_mod.httpx, "get", return_value=stale_response) as get, \
         patch.object(sync_mod.time, "sleep") as sleep:
        result = sync_mod.verify(menu, "https://estacion90.pe/api/menu.json", retries=3, delay=0.01)

    assert result is False
    assert get.call_count == 3
    assert sleep.call_count == 2  # no sleep after the last attempt


def test_verify_recovers_after_transient_http_error(tmp_path):
    menu = tmp_path / "menu.json"
    content = b'{"store": "estacion90_pe"}'
    menu.write_bytes(content)

    responses = [httpx.ConnectTimeout("timed out"), _ok_response(content)]

    def fake_get(url, timeout):
        result = responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    with patch.object(sync_mod.httpx, "get", side_effect=fake_get), \
         patch.object(sync_mod.time, "sleep"):
        assert sync_mod.verify(menu, "https://estacion90.pe/api/menu.json", retries=2, delay=0.01) is True
