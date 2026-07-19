import os
import sys
import json
import httpx
from pathlib import Path
from datetime import datetime, timezone

# Rutas
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "ops" / "generated" / "reports" / "intelligence"
SENT_DIR = REPORTS_DIR / "sent"

# Configuración
SLACK_WEBHOOK_INTEL = os.getenv("SLACK_CHANNEL_NEWSLETTER") # Usamos el canal de newsletter para prensa/export
CLI_MARKET_API_KEY = os.getenv("MARKET_API_TOKEN")

def distribute_reports():
    print(f"🚀 Iniciando distribución de reportes de Inteligencia...")
    
    if not SLACK_WEBHOOK_INTEL:
        print("  ⚠️ SLACK_CHANNEL_NEWSLETTER no configurado. Saltando Slack.")
    
    # Listar reportes generados hoy
    reports = list(REPORTS_DIR.glob("*.md"))
    
    if not reports:
        print("  ❌ No se encontraron reportes para distribuir.")
        return

    for report_path in reports:
        report_name = report_path.stem
        content = report_path.read_text(encoding="utf-8")
        
        # 1. Enviar a Slack (Newsletter/Outbound channel)
        if SLACK_WEBHOOK_INTEL:
            print(f"  📤 Enviando {report_name} a Slack...")
            payload = {
                "text": f"📢 *Nuevo Reporte de Inteligencia Generado: {report_name.upper()}*\n\n{content[:2000]}..."
            }
            try:
                httpx.post(SLACK_WEBHOOK_INTEL, json=payload, timeout=10)
            except Exception as e:
                print(f"    ⚠️ Error en Slack: {e}")

        # 2. Simulación de envío de Email (Log para luego integrar con SendGrid/Mailchimp)
        print(f"  📧 Reporte {report_name} listo para secuencia de Email Marketing.")
        
        # Mover a 'sent' para no duplicar si se desea tracking (opcional)
        # report_path.rename(SENT_DIR / report_path.name)

    print("✅ Distribución completada.")

if __name__ == "__main__":
    distribute_reports()
