"""Tests for GH_PAT backend probe helper."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ops"))

from probe_gh_pat_backend import gh_pat_can_read_backend  # noqa: E402


def test_gh_pat_can_read_backend_no_token():
    assert gh_pat_can_read_backend("") is False
    assert gh_pat_can_read_backend(None) is False


def test_gh_pat_can_read_backend_http_200():
    resp = MagicMock()
    resp.status = 200
    resp.__enter__ = lambda self: self
    resp.__exit__ = lambda *args: None
    with patch("probe_gh_pat_backend.urllib.request.urlopen", return_value=resp):
        assert gh_pat_can_read_backend("ghp_test") is True


def test_gh_pat_can_read_backend_http_404():
    import urllib.error

    with patch(
        "probe_gh_pat_backend.urllib.request.urlopen",
        side_effect=urllib.error.HTTPError("url", 404, "nope", hdrs=None, fp=None),
    ):
        assert gh_pat_can_read_backend("ghp_test") is False
