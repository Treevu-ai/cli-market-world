import os

import httpx

API_URL = "https://cli-market-api.fly.dev"
API_TOKEN = os.environ["MARKET_API_TOKEN"]

try:
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    print("Consultando API...")
    r = httpx.get(f"{API_URL}/v1/quality/scores", headers=headers, timeout=10.0)
    print(f"Status: {r.status_code}")
    print(f"Data: {r.json().get('meta', {}).get('freshness_seconds')}")
except Exception as e:
    print(f"Error: {e}")
