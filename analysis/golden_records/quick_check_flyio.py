#!/usr/bin/env python3
import os

import requests
import json

token = os.environ["MARKET_API_TOKEN"]
h = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print("Consultando CLI Market en fly.io...")

try:
    r = requests.post('https://cli-market-api.fly.dev/products/search', 
                      headers=h, 
                      json={'query': 'coca', 'limit': 50, 'country': 'PE'}, 
                      timeout=15)
    
    print(f'Status: {r.status_code}')
    
    if r.status_code == 200:
        d = r.json()
        total = d.get('total', len(d.get('results', [])))
        results = d.get('results', [])
        
        print(f'\nTotal SKUs en búsqueda: {total}')
        print(f'Items retornados: {len(results)}')
        
        if results:
            item = results[0]
            print(f'\nPrimer item:')
            print(json.dumps(item, indent=2)[:500])
            
            print(f'\nCampos disponibles:')
            print(list(item.keys()))
            
            # Buscar campos de golden record
            golden_fields = ['golden_record', 'is_golden', 'canonical', 'verified']
            for field in golden_fields:
                if field in item:
                    print(f'  ✓ Campo "{field}" encontrado')
    
except requests.exceptions.Timeout:
    print("ERROR: Timeout - El API está respondiendo lentamente")
except Exception as e:
    print(f'ERROR: {e}')
