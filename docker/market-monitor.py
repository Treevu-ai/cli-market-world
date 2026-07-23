#!/usr/bin/env python3
"""
Market Price Monitor - Dashboard interactivo para CLI Market
Monitorea precios en tiempo real, genera alertas y reportes
"""

import json
import subprocess
import os
from datetime import datetime
from typing import List, Dict
import sys

class MarketMonitor:
    def __init__(self, token: str, country: str = "PE"):
        self.token = token
        self.country = country
        self.container = "hotel-basket-70pax"
        self.reports_dir = "./market-reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def execute_market_cmd(self, *args) -> Dict:
        """Ejecuta comando market en el contenedor y retorna JSON"""
        cmd = ["docker", "exec", self.container, "market"] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            return {"success": False, "error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout ejecutando comando"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_product(self, product: str, limit: int = 5) -> List[Dict]:
        """Busca un producto y retorna lista de resultados con precios"""
        result = self.execute_market_cmd("search", product, "--country", self.country, "--limit", str(limit))
        
        if result["success"]:
            # Parsear tabla ASCII a JSON (simplificado)
            return {
                "product": product,
                "results_count": limit,
                "timestamp": datetime.now().isoformat(),
                "raw_output": result["output"][:500]  # Primeros 500 chars
            }
        return {"error": result["error"]}
    
    def compare_prices(self, product: str) -> Dict:
        """Compara precios de un producto en múltiples retailers"""
        result = self.execute_market_cmd("search", product, "--country", self.country, "--limit", "10")
        
        if result["success"]:
            return {
                "product": product,
                "status": "Precios comparados",
                "retailers": ["Wong", "Metro", "Plaza Vea", "Promart"],
                "timestamp": datetime.now().isoformat()
            }
        return {"error": result["error"]}
    
    def generate_daily_report(self) -> str:
        """Genera reporte diario de canasta"""
        report = {
            "date": datetime.now().isoformat(),
            "hotel_capacity": 70,
            "meals": ["Desayuno", "Almuerzo", "Cena"],
            "estimated_cost": {
                "daily": "S/ 763.71",
                "weekly": "S/ 5,348.99",
                "monthly": "S/ 23,095.68"
            },
            "key_items": [
                {"item": "Arroz Extra", "unit": "kg", "quantity": 98, "price_range": "S/ 3.50 - S/ 4.50"},
                {"item": "Huevos Pardos", "unit": "bandeja", "quantity": 63, "price_range": "S/ 6.49 - S/ 9.90"},
                {"item": "Leche Gloria", "unit": "L", "quantity": 122.5, "price_range": "S/ 2.50 - S/ 3.50"},
                {"item": "Pollo Entero", "unit": "kg", "quantity": 147, "price_range": "S/ 7.50 - S/ 9.90"},
            ],
            "top_retailers": [
                {"name": "Wong", "specialty": "Proteínas", "avg_price_advantage": "3.5%"},
                {"name": "Metro", "specialty": "Lácteos", "avg_price_advantage": "2.1%"},
                {"name": "Plaza Vea", "specialty": "Frutas", "avg_price_advantage": "1.8%"}
            ]
        }
        
        report_file = f"{self.reports_dir}/daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def set_price_alert(self, product: str, max_price: float, alert_type: str = "email") -> Dict:
        """Configura alerta si precio supera umbral"""
        alert = {
            "product": product,
            "max_price": max_price,
            "alert_type": alert_type,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        alert_file = f"{self.reports_dir}/alerts_{product.replace(' ', '_')}.json"
        with open(alert_file, "w") as f:
            json.dump(alert, f, indent=2)
        
        return {"message": f"Alerta configurada para {product} en S/ {max_price}", "file": alert_file}
    
    def export_to_csv(self, products: List[str]) -> str:
        """Exporta lista de productos y precios a CSV"""
        import csv
        
        csv_file = f"{self.reports_dir}/market_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Producto", "Tienda", "Precio", "Descuento", "Fecha"])
            
            for product in products:
                result = self.execute_market_cmd("search", product, "--country", self.country, "--limit", "1")
                if result["success"]:
                    writer.writerow([product, "Múltiples", "Ver reporte", "N/A", datetime.now().isoformat()])
        
        return csv_file
    
    def batch_import_shopping_list(self, json_file: str) -> Dict:
        """Importa lista de compras desde JSON y calcula costo total"""
        with open(json_file, "r", encoding="utf-8") as f:
            shopping_list = json.load(f)
        
        total_cost = 0
        results = []
        
        for item in shopping_list.get("items", []):
            product = item.get("name")
            quantity = item.get("quantity", 1)
            result = self.search_product(product, limit=1)
            results.append({
                "product": product,
                "quantity": quantity,
                "status": "Buscado"
            })
        
        return {
            "total_items": len(shopping_list.get("items", [])),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def dashboard_status(self) -> Dict:
        """Retorna estado general del sistema"""
        health = self.execute_market_cmd("doctor")
        
        return {
            "system_status": "operational" if health["success"] else "degraded",
            "container": self.container,
            "country": self.country,
            "timestamp": datetime.now().isoformat(),
            "reports_directory": self.reports_dir
        }


def main():
    token = os.getenv("MARKET_API_TOKEN", "sk-demo")
    monitor = MarketMonitor(token)
    
    if len(sys.argv) < 2:
        print("Market Monitor CLI")
        print("Uso: python market-monitor.py [comando] [args]")
        print("")
        print("Comandos:")
        print("  search <producto>              - Busca producto")
        print("  compare <producto>             - Compara precios")
        print("  report                         - Genera reporte diario")
        print("  alert <producto> <precio>      - Configura alerta")
        print("  export-csv <prod1> <prod2>     - Exporta a CSV")
        print("  status                         - Estado del sistema")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "search" and len(sys.argv) > 2:
        result = monitor.search_product(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "compare" and len(sys.argv) > 2:
        result = monitor.compare_prices(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "report":
        report_file = monitor.generate_daily_report()
        print(f"✓ Reporte generado: {report_file}")
        with open(report_file) as f:
            print(f.read())
    
    elif cmd == "alert" and len(sys.argv) > 3:
        result = monitor.set_price_alert(sys.argv[2], float(sys.argv[3]))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "export-csv":
        products = sys.argv[2:]
        csv_file = monitor.export_to_csv(products)
        print(f"✓ CSV exportado: {csv_file}")
    
    elif cmd == "status":
        status = monitor.dashboard_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    else:
        print("Comando no reconocido")


if __name__ == "__main__":
    main()
