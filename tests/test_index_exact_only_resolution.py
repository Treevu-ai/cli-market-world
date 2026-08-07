"""Tests for index_gate's exact-only resolution bypass.

ops/reresolve_stale_brands.py --exact-only routes through this path; it was
built to fix ~212 price_snapshots rows stuck on a stale genrico/noinformado
canonical_product_id caused by a cli-market-index bug: Resolver.index_product()
also indexed every product under canonicalize_brand("", product.name) as an
alias bucket, so an old mis-branded-but-correctly-named product was
rediscovered by fresh resolution attempts for the same real product via
_fuzzy_search/_name_match_search, inheriting the stale id instead of getting
a fresh correct one. Confirmed live 2026-08-07 against the production
registry.

cli-market-index fixed this at the source (PR #14, merged into the pin this
repo now uses) by excluding genrico/noinformado from that alias bucket, so
normal Resolver.resolve() no longer reproduces the bug either — see
test_normal_resolve_no_longer_reproduces_the_alias_pollution_bug below. This
exact-only bypass is kept as defense-in-depth for ops/reresolve_stale_brands.py
and as a documented fallback if a similar defunct-brand-slug situation ever
recurs before an upstream fix ships."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _seed_service():
    from api.resources import Measurement, Product
    from services.index_service import IndexService

    raw_name = "Papa Amarilla Cocktail Comcen 1kg"
    old_product = Product(
        id="prod_genrico_general_1kg",
        name=raw_name,
        brand="brnd_genrico",
        category="cat_general",
        measurement=Measurement(value=1.0, unit="kg", display="1kg"),
        created=1,
    )
    svc = IndexService(registry={"prod_genrico_general_1kg": old_product})
    return svc, raw_name, old_product


def test_normal_resolve_no_longer_reproduces_the_alias_pollution_bug():
    """cli-market-index PR #14 fixed the root cause (declared_brand in
    {genrico, noinformado} is now excluded from the name-derived alias
    bucket), so as of that pin, normal Resolver.resolve() — not just the
    _exact_only bypass below — avoids the stale match too. This asserts the
    upstream fix is actually live in whatever cli-market-index version this
    repo has installed; a pin downgrade or regression would fail this test
    instead of silently losing the fix."""
    svc, raw_name, old_product = _seed_service()

    result = svc.resolver.resolve(raw_name=raw_name, raw_brand="Genérico")

    assert result.product is not None
    assert result.product.id != old_product.id, (
        "normal resolve() inherited the stale genrico id — cli-market-index's "
        "PR #14 fix (excluding genrico/noinformado from alias-indexing) is "
        "missing from the installed pin"
    )


def test_exact_only_resolution_avoids_the_stale_alias_match():
    from index_gate import _exact_only_resolution

    svc, raw_name, old_product = _seed_service()

    with _exact_only_resolution(svc):
        result = svc.resolver.resolve(raw_name=raw_name, raw_brand="Genérico")

    assert result.product is not None
    assert result.product.id != old_product.id
    assert result.product.id.startswith("prod_papa_general_1kg")
    assert result.match_type == "none"


def test_exact_only_resolution_still_returns_a_true_exact_match():
    """A canonical_product_id that's genuinely already correct must resolve
    to itself, not get bypassed into creating a duplicate."""
    from api.resources import Measurement, Product
    from index_gate import _exact_only_resolution
    from services.index_service import IndexService

    raw_name = "Leche Gloria Entera 1L"
    good_product = Product(
        id="prod_gloria_lacteos_1l",
        name=raw_name,
        brand="brnd_gloria",
        category="cat_lacteos",
        measurement=Measurement(value=1.0, unit="l", display="1l"),
        created=1,
    )
    svc = IndexService(registry={good_product.id: good_product})

    with _exact_only_resolution(svc):
        result = svc.resolver.resolve(raw_name=raw_name, raw_brand="Gloria")

    assert result.product is not None
    assert result.product.id == good_product.id
    assert result.match_type == "exact"


def test_exact_only_resolution_restores_resolve_after_use():
    """The monkeypatch must not leak past the `with` block, including when
    the wrapped call raises."""
    from index_gate import _exact_only_resolution

    svc, raw_name, _old_product = _seed_service()
    original_resolve = svc.resolver.resolve

    # Bound methods aren't cached — each attribute access on an unpatched
    # instance yields a distinct-but-equal bound method object, so equality
    # (not `is`) is the right check for "still the original unpatched
    # method" outside the `with` block.
    with _exact_only_resolution(svc):
        assert svc.resolver.resolve != original_resolve

    assert svc.resolver.resolve == original_resolve

    with pytest.raises(RuntimeError):
        with _exact_only_resolution(svc):
            assert svc.resolver.resolve != original_resolve
            raise RuntimeError("boom")

    assert svc.resolver.resolve == original_resolve


def test_resolve_exact_only_never_calls_fuzzy_or_name_match_search():
    """Direct assertion that the bypass never reaches the buggy search
    paths at all, not just that it happens to return a different id."""
    from index_gate import _resolve_exact_only

    svc, raw_name, _old_product = _seed_service()

    def _boom(*args, **kwargs):
        raise AssertionError("exact-only path must not call fuzzy/name-match search")

    svc.resolver._fuzzy_search = _boom
    svc.resolver._name_match_search = _boom

    result = _resolve_exact_only(svc.resolver, raw_name, "Genérico")

    assert result.match_type == "none"
