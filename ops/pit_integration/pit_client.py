"""Thin HTTP client for PIT Research API (phase 3 glue).

Does not reimplement literature search or reports — only health, research-run
create/get, and optional ficha post when the agents module is available.
"""

from __future__ import annotations

import os
from typing import Any

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore[assignment]

DEFAULT_PIT_URL = "https://cli-market-pit-backend.fly.dev"


class PitClient:
    """Minimal PIT API client for thin integration demos and CI mocks."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        *,
        timeout: float = 30.0,
        client: Any | None = None,
    ) -> None:
        if httpx is None and client is None:
            raise RuntimeError("httpx is required for PitClient (pip install httpx)")
        self.base_url = (
            base_url
            or os.getenv("PIT_API_URL")
            or DEFAULT_PIT_URL
        ).rstrip("/")
        self.token = token if token is not None else os.getenv("PIT_API_TOKEN", "")
        self.timeout = timeout
        self._client = client

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json"}
        if self.token:
            # Cookie sessions are primary on PIT; Bearer supported if configured.
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        if self._client is not None:
            r = self._client.request(
                method,
                url if url.startswith("http") else path,
                json=json_body,
                params=params,
                headers=self._headers(),
                timeout=self.timeout,
            )
        else:
            assert httpx is not None
            with httpx.Client(
                base_url=self.base_url,
                headers=self._headers(),
                timeout=self.timeout,
            ) as client:
                r = client.request(method, path, json=json_body, params=params)

        status = r.status_code
        try:
            body: Any = r.json()
        except Exception:  # noqa: BLE001
            body = {"raw": (r.text or "")[:500]}

        return {
            "ok": 200 <= status < 300,
            "status_code": status,
            "body": body,
        }

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/v1/health")

    def agents_status(self) -> dict[str, Any]:
        return self._request("GET", "/v1/agents/status")

    def create_research_run(
        self,
        query: str,
        *,
        target_market: str = "US",
        application: str = "functional foods and beverages",
        from_publication_date: str = "2021-01-01",
        limit: int = 25,
        hs_code: str | None = None,
        full: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "query": query,
            "target_market": target_market.upper(),
            "application": application,
            "from_publication_date": from_publication_date,
            "limit": limit,
        }
        path = "/v1/research-runs/full" if full or hs_code else "/v1/research-runs"
        if hs_code:
            payload["hs_code"] = hs_code
        return self._request("POST", path, json_body=payload)

    def get_research_run(self, run_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/research-runs/{run_id}")

    def get_report(self, run_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/research-runs/{run_id}/report")

    def post_ficha(
        self,
        run_id: str,
        *,
        segment: str = "exportadores y retail premium",
        stage: str = "concepto",
        market_label: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"segment": segment, "stage": stage}
        if market_label is not None:
            payload["market_label"] = market_label
        return self._request("POST", f"/v1/research-runs/{run_id}/ficha", json_body=payload)

    @staticmethod
    def extract_run_id(create_response: dict[str, Any]) -> str | None:
        """Best-effort extract of run id from create research-run response."""
        body = create_response.get("body")
        if not isinstance(body, dict):
            return None
        for key in ("run_id", "id", "research_run_id"):
            val = body.get(key)
            if isinstance(val, str) and val:
                return val
        data = body.get("data")
        if isinstance(data, dict):
            for key in ("run_id", "id"):
                val = data.get(key)
                if isinstance(val, str) and val:
                    return val
        return None
