"""Validate backend CI template includes cli-market-index checkout."""

from pathlib import Path


def test_backend_ci_template_checks_out_index():
    ci = Path(__file__).resolve().parent.parent / "ops" / "backend-parity" / "ci.yml"
    text = ci.read_text(encoding="utf-8")
    assert "cli-market-index" in text
    assert 'pip install -e ".deps/cli-market-index[postgres]"' in text


def test_backend_pytest_ini_registers_integration_mark():
    ini = Path(__file__).resolve().parent.parent / "ops" / "backend-parity" / "pytest.ini"
    text = ini.read_text(encoding="utf-8")
    assert "integration:" in text
