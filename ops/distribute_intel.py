import os
import sys
import httpx
from pathlib import Path

# Asegurar que el root esté en el path para importar routers
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from routers.integrations.whatsapp import send_whatsapp_proactive

REPORTS_DIR = PROJECT_ROOT / "ops" / "generated" / "reports" / "intelligence"
SENT_DIR = REPORTS_DIR / "sent"

# Configuración
SLACK_WEBHOOK_INTEL = os.getenv("SLACK_CHANNEL_NEWSLETTER")
WHATSAPP_TEST_NUMBER = "whatsapp:+51902126765" # Tu número de prueba

def distribute_reports():
    print("🚀 Iniciando distribución de reportes de Inteligencia...")
    
    if not SLACK_WEBHOOK_INTEL:
        print("  ⚠️ SLACK_CHANNEL_NEWSLETTER no configurado. Saltando Slack.")
    
    # Listar reportes generados
    reports = list(REPORTS_DIR.glob("*.md"))
    
    if not reports:
        print("  ❌ No se encontraron reportes para distribuir.")
        return

    for report_path in reports:
        report_name = report_path.stem
        if "informal" in report_name.lower(): continue # Saltar el reporte de estrategia conceptual

        content = report_path.read_text(encoding="utf-8")
        # Limpiar un poco el markdown para WhatsApp/Slack
        clean_content = content.replace("# ", "*").replace("## ", "*").replace("### ", "*")
        
        # 1. Enviar a Slack
        if SLACK_WEBHOOK_INTEL:
            print(f"  📤 Enviando {report_name} a Slack...")
            payload = {
                "text": f"📢 *Nuevo Reporte de Inteligencia: {report_name.upper()}*\n\n{clean_content[:2000]}..."
            }
            try:
                httpx.post(SLACK_WEBHOOK_INTEL, json=payload, timeout=10)
            except Exception as e:
                print(f"    ⚠️ Error en Slack: {e}")

        # 2. Enviar a WhatsApp (Proactivo)
        print(f"  📱 Enviando {report_name} a WhatsApp...")
        ws_body = f"🚀 *CLI Market Intelligence*\n\nReporte: *{report_name.upper()}*\n\n{clean_content[:800]}...\n\n_Para ver el reporte completo, usa el comando /intel en el bot._"
        send_whatsapp_proactive(WHATSAPP_TEST_NUMBER, ws_body)

    print("✅ Distribución completada.")

if __name__ == "__main__":
    distribute_reports()
