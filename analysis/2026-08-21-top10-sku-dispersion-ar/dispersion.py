#!/usr/bin/env python3
"""
Análisis Top 10 SKU con mayor dispersión en Alimentos y Bebidas
CLI Market - Argentina Supermercados
"""

import json
import subprocess
from typing import List, Dict
from statistics import stdev, mean

def calculate_dispersion(prices: List[float]) -> Dict:
    """Calcula dispersión de precios"""
    prices = [p for p in prices if p > 0]
    
    if len(prices) < 2:
        return {
            "mean": prices[0] if prices else 0,
            "std_dev": 0,
            "cv": 0,
            "min": prices[0] if prices else 0,
            "max": prices[0] if prices else 0,
            "spread_pct": 0
        }
    
    mean_price = mean(prices)
    std_dev = stdev(prices)
    cv = (std_dev / mean_price * 100) if mean_price > 0 else 0
    min_price = min(prices)
    max_price = max(prices)
    spread_pct = (max_price - min_price) / mean_price * 100 if mean_price > 0 else 0
    
    return {
        "mean": round(mean_price, 2),
        "std_dev": round(std_dev, 2),
        "cv": round(cv, 2),
        "min": round(min_price, 2),
        "max": round(max_price, 2),
        "spread_pct": round(spread_pct, 2)
    }

def manual_sku_analysis():
    """
    Análisis manual de SKUs principales en alimentos y bebidas
    Basado en datos de CLI Market
    """
    skus = {
        "Bebida Vegetal Notmilk (1L)": {
            "prices": [765.93, 765.93],
            "stores": ["Vea AR", "Jumbo AR"],
        },
        "Gatorade Manzana (1.25L)": {
            "prices": [2750.00],
            "stores": ["Carrefour AR"],
        },
        "Nescafé Cappuccino Clásico (270ml)": {
            "prices": [2804.25],
            "stores": ["Carrefour AR"],
        },
        "Speed Zero Sugar (473ml)": {
            "prices": [2925.00],
            "stores": ["Carrefour AR"],
        },
        "Monster Energy (473ml)": {
            "prices": [3299.00, 3300.00],
            "stores": ["Carrefour AR", "Vea AR"],
        },
        "Ades Soja Manzana (1L)": {
            "prices": [3390.00],
            "stores": ["Vea AR"],
        },
        "Terma Pomelo Rosado (1.75L)": {
            "prices": [3399.00],
            "stores": ["Vea AR"],
        },
        "Bebida Quinoa Biba (1L)": {
            "prices": [3400.00],
            "stores": ["New Garden"],
        },
        "Red Bull Sugar Free (250ml)": {
            "prices": [3439.00],
            "stores": ["Carrefour AR"],
        },
        "Suerox Bebida Hidratante (630ml)": {
            "prices": [3500.00],
            "stores": ["El Banquito"],
        },
        "Bebida Gasificada Limón/Jengibre Orgánica (354ml)": {
            "prices": [3900.00],
            "stores": ["Biomarket"],
        },
        "Ades Almendras (1L)": {
            "prices": [3900.00],
            "stores": ["Carrefour AR"],
        },
        "Green Food Makers Almendra (330ml)": {
            "prices": [3970.00],
            "stores": ["Biomarket"],
        },
        "Silk Almendras Sin Azúcar (1L)": {
            "prices": [4623.75, 6650.00],
            "stores": ["Carrefour AR", "Jumbo AR"],
        },
        "La Serenísima Bebida Vegetal Almendra (1L)": {
            "prices": [4950.00],
            "stores": ["Jumbo AR"],
        },
        "Bebida Orgánica Arándano/Hibiscus (500ml)": {
            "prices": [5520.00],
            "stores": ["Biomarket"],
        },
        "Bebida de Coco Sin Gluten Chennai (400ml)": {
            "prices": [6400.00],
            "stores": ["New Garden"],
        },
    }
    
    results = []
    for sku_name, sku_data in skus.items():
        prices = sku_data["prices"]
        dispersion = calculate_dispersion(prices)
        results.append({
            "sku": sku_name,
            "stores": sku_data["stores"],
            "num_stores": len(sku_data["stores"]),
            "prices": prices,
            **dispersion
        })
    
    # Ordenar por coeficiente de variación (dispersión)
    results.sort(key=lambda x: x["cv"], reverse=True)
    
    return results

def print_report(results: List[Dict]):
    """Imprime reporte formateado"""
    print("\n" + "="*130)
    print("TOP 10 SKU CON MAYOR DISPERSIÓN - ALIMENTOS Y BEBIDAS".center(130))
    print("CLI Market | Argentina | Supermercados".center(130))
    print("="*130 + "\n")
    
    print(f"{'Rank':<6} {'SKU':<45} {'CV %':<10} {'Spread %':<12} {'Tiendas':<10} {'Rango Precio ARS':<20}")
    print("-"*130)
    
    for idx, item in enumerate(results[:10], 1):
        sku = item["sku"][:43]
        cv = f"{item['cv']:.2f}"
        spread = f"{item['spread_pct']:.2f}"
        stores = str(item["num_stores"])
        price_range = f"{item['min']:.0f} - {item['max']:.0f}"
        
        print(f"{idx:<6} {sku:<45} {cv:<10} {spread:<12} {stores:<10} {price_range:<20}")
    
    print("\n" + "="*130)
    print("\nDETALLE COMPLETO:\n")
    
    for idx, item in enumerate(results[:10], 1):
        print(f"{idx}. {item['sku']}")
        print(f"   ├─ Dispersión (CV):       {item['cv']:.2f}%")
        print(f"   ├─ Spread de Precios:     {item['spread_pct']:.2f}%")
        print(f"   ├─ Precio Promedio:       ARS {item['mean']:.2f}")
        print(f"   ├─ Desv. Estándar:        ARS {item['std_dev']:.2f}")
        print(f"   ├─ Rango:                 ARS {item['min']:.2f} - ARS {item['max']:.2f}")
        print(f"   ├─ Tiendas:               {', '.join(item['stores'])}")
        print(f"   └─ Precios:               {[f'ARS {p:.0f}' for p in item['prices']]}\n")

def export_json(results: List[Dict], filename: str = "top10_sku_dispersion.json"):
    """Exporta resultados a JSON"""
    export_data = []
    for item in results[:10]:
        export_data.append({
            "rank": results.index(item) + 1,
            "sku": item["sku"],
            "dispersión_cv_pct": item["cv"],
            "spread_pct": item["spread_pct"],
            "precio_promedio": item["mean"],
            "desv_estandar": item["std_dev"],
            "rango_min": item["min"],
            "rango_max": item["max"],
            "num_tiendas": item["num_stores"],
            "tiendas": item["stores"],
            "precios": item["prices"]
        })
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Reporte JSON exportado a: {filename}\n")

if __name__ == "__main__":
    print("\n🔍 Analizando Top 10 SKU con mayor dispersión...\n")
    results = manual_sku_analysis()
    
    print_report(results)
    
    export_json(results)
    
    print("📊 Análisis completado.")
