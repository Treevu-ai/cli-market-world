#!/usr/bin/env python3
"""
Example: Using VTEX connector with Playwright fallback.

This example demonstrates how to use the self-healing fallback mechanism
to search for products in stores that are protected by Cloudflare.

Run this example with:
    python3 example_vtex_fallback.py
"""

import asyncio
import logging
from market_connectors.vtex import VtexConnector

# Setup logging to see the fallback in action
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)

# Example store configurations (from market_stores.py or your store config)
STORE_CONFIGS = {
    "globo_br": {
        "name": "Globo",
        "base": "https://www.globo.com.br",
        "currency": "BRL",
        "_store_key": "globo_br",
    },
    "carrefour_ar": {
        "name": "Carrefour Argentina",
        "base": "https://www.carrefour.com.ar",
        "currency": "ARS",
        "_store_key": "carrefour_ar",
    },
    "falabella_pe": {
        "name": "Falabella Perú",
        "base": "https://www.falabella.com.pe",
        "currency": "PEN",
        "_store_key": "falabella_pe",
    },
}


async def example_1_simple_search():
    """Example 1: Simple product search with fallback."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Product Search")
    print("=" * 70)
    
    connector = VtexConnector()
    
    # Search for "aspirina" (aspirin) in Globo
    store_key = "globo_br"
    store_config = STORE_CONFIGS[store_key]
    
    print(f"\nSearching for 'aspirina' in {store_config['name']}...")
    print("(This will activate Playwright fallback on first attempt)\n")
    
    try:
        products = await connector.search(
            store_config=store_config,
            term="aspirina",
            page=1,
            limit=5
        )
        
        print(f"\n✅ Found {len(products)} products!")
        if products:
            print("\nFirst product:")
            product = products[0]
            print(f"  ID: {product.get('id', 'N/A')}")
            print(f"  Name: {product.get('productName', 'N/A')}")
            print(f"  Price: {product.get('price', 'N/A')}")
            print(f"  Brand: {product.get('brand', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Search failed: {e}")


async def example_2_cache_reuse():
    """Example 2: Demonstrate cookie cache reuse."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Cookie Cache Reuse")
    print("=" * 70)
    
    connector = VtexConnector()
    store_config = STORE_CONFIGS["globo_br"]
    
    print("\n--- FIRST SEARCH (will populate cache) ---")
    products1 = await connector.search(store_config, "leche", page=1, limit=3)
    print(f"First search: {len(products1)} products found")
    
    print("\n--- SECOND SEARCH (will use cached cookies) ---")
    print("(Should be much faster - using cf_clearance from cache)\n")
    products2 = await connector.search(store_config, "pan", page=1, limit=3)
    print(f"Second search: {len(products2)} products found")
    print("✅ Cache reuse successful!")


async def example_3_multiple_stores():
    """Example 3: Search across multiple stores (sequential)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Multiple Store Search (Sequential)")
    print("=" * 70)
    
    connector = VtexConnector()
    search_term = "cafe"
    
    results = {}
    
    for store_key, store_config in STORE_CONFIGS.items():
        print(f"\nSearching '{search_term}' in {store_config['name']}...")
        try:
            products = await connector.search(
                store_config=store_config,
                term=search_term,
                page=1,
                limit=3
            )
            results[store_key] = len(products)
            print(f"  ✅ {len(products)} products found")
        except Exception as e:
            results[store_key] = 0
            print(f"  ❌ Error: {e}")
    
    print("\n" + "-" * 70)
    print("SUMMARY:")
    for store_key, count in results.items():
        store_name = STORE_CONFIGS[store_key]['name']
        print(f"  {store_name}: {count} products")


async def example_4_fetch_all_products():
    """Example 4: Fetch all products from a store."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Fetch All Products")
    print("=" * 70)
    
    connector = VtexConnector()
    store_config = STORE_CONFIGS["carrefour_ar"]
    
    print(f"\nFetching products from {store_config['name']} (max 3 pages)...")
    print("(Will use fallback if direct HTTP fails)\n")
    
    try:
        products = await connector.fetch_all_products(
            store_config=store_config,
            max_pages=3
        )
        
        print(f"\n✅ Fetched {len(products)} products total")
        
        if products:
            print("\nSample products:")
            for i, product in enumerate(products[:3], 1):
                print(f"\n  {i}. {product.get('productName', 'N/A')}")
                print(f"     Price: {product.get('price', 'N/A')} {store_config['currency']}")
                
    except Exception as e:
        print(f"❌ Fetch failed: {e}")


async def example_5_normalize_products():
    """Example 5: Normalize raw products to unified schema."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Product Normalization")
    print("=" * 70)
    
    connector = VtexConnector()
    store_config = STORE_CONFIGS["globo_br"]
    
    print(f"\nSearching for products in {store_config['name']}...")
    raw_products = await connector.search(store_config, "chocolates", page=1, limit=2)
    
    if raw_products:
        print(f"\n--- RAW PRODUCT (from API) ---")
        raw = raw_products[0]
        print(f"Keys in raw: {list(raw.keys())[:5]}...")
        
        print(f"\n--- NORMALIZED PRODUCT ---")
        normalized = connector.normalize(raw, "globo_br", store_config)
        print(f"Normalized product:")
        for key, value in normalized.items():
            if key != 'url':  # Skip URL for brevity
                print(f"  {key}: {value}")
        print(f"  url: {normalized.get('url', 'N/A')[:50]}...")


async def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + " CLI Market: VTEX Connector with Playwright Fallback Examples ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    print("\n⚠️  NOTE: These examples expect stores to have Playwright fallback enabled.")
    print("Install Playwright first:")
    print("  pip install 'cli-market[playwright]'")
    print("  playwright install chromium")
    
    examples = [
        ("Simple Search", example_1_simple_search),
        ("Cache Reuse", example_2_cache_reuse),
        ("Multiple Stores", example_3_multiple_stores),
        ("Fetch All Products", example_4_fetch_all_products),
        ("Product Normalization", example_5_normalize_products),
    ]
    
    for example_name, example_func in examples:
        try:
            await example_func()
        except KeyboardInterrupt:
            print("\n\n✋ Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
