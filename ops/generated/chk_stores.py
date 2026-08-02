from market_core import STORES
for k, v in STORES.items():
    if any(x in k.lower() for x in ['sodimac', 'promart', 'carsa', 'ferrincorp']):
        print(f"{k}: name={v.get('name')}, country={v.get('country')}, base={v.get('base')}")
print(f"\nTotal STORES: {len(STORES)}")
