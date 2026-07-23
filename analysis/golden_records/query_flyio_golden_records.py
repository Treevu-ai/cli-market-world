#!/usr/bin/env python3
"""
Consulta golden records directamente desde fly.io API
"""

import os

import requests
import json

token = os.environ["MARKET_API_TOKEN"]
api_url = "https://cli-market-api.fly.dev"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("="*70)
print("Consultando CLI Market en fly.io")
print("="*70)

# Test 1: Stats endpoint
try:
    print("\n1. Intentando endpoint /products/stats...")
    resp = requests.get(f"{api_url}/products/stats", headers=headers, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"   Error: {e}")

# Test 2: SKU count
try:
    print("\n2. Intentando endpoint /products/count...")
    resp = requests.get(f"{api_url}/products/count", headers=headers, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Search con limit alto
try:
    print("\n3. Buscando todos los productos...")
    resp = requests.post(
        f"{api_url}/products/search",
        headers=headers,
        json={"query": "*", "limit": 1000, "country": "PE"},
        timeout=15
    )
    print(f"   Status: {resp.status_code}")
    data = resp.json()
    
    total = data.get('total', data.get('count', len(data.get('results', []))))
    results = data.get('results', [])
    
    print(f"   Total SKUs: {total}")
    print(f"   Items retornados: {len(results)}")
    
    if results:
        print(f"\n   Sample result:")
        print(json.dumps(results[0], indent=2))
        
        # Contar golden records
        golden_count = sum(1 for r in results if r.get('golden_record') or r.get('is_golden'))
        print(f"\n   Golden records en muestra: {golden_count}/{len(results)}")

except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Probar endpoint raíz
try:
    print("\n4. Consultando raíz de API...")
    resp = requests.get(f"{api_url}/", headers=headers, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=2))
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*70)
