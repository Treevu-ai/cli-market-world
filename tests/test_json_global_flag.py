"""Regression test for cli-market-backend#127 (S9): --json is documented as
a global flag but only worked when placed before the subcommand — argparse
rejected it as "unrecognized arguments: --json" when placed after
subcommand-specific args (e.g. `market search leche --country AR --json`,
the natural place an agent would put it)."""

from __future__ import annotations

import market_cli


def test_strip_json_flag_after_subcommand_args():
    argv = ["market", "search", "leche entera", "--country", "AR", "--limit", "3", "--json"]
    stripped, present = market_cli._strip_json_flag(argv)
    assert present is True
    assert "--json" not in stripped
    assert stripped == ["market", "search", "leche entera", "--country", "AR", "--limit", "3"]


def test_strip_json_flag_before_subcommand():
    argv = ["market", "--json", "search", "leche"]
    stripped, present = market_cli._strip_json_flag(argv)
    assert present is True
    assert stripped == ["market", "search", "leche"]


def test_strip_json_flag_absent():
    argv = ["market", "search", "leche"]
    stripped, present = market_cli._strip_json_flag(argv)
    assert present is False
    assert stripped == argv
