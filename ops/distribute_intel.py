import sys
from pathlib import Path

# Asegurar que el root esté en el path para importar routers
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "ops") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "ops"))

from routers.integrations.whatsapp import send_whatsapp_proactive

REPORTS_DIR = PROJECT_ROOT / "ops" / "generated" / "reports" / "intelligence"
SENT_DIR = REPORTS_DIR / "sent"

WHATSAPP_TEST_NUMBER = "whatsapp:+51902126765" # Tu número de prueba

def distribute_reports():
    print("🚀 Iniciando distribución de reportes de Inteligencia...")

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

        # 1. Enviar a Slack (#publicaciones — vía el transporte compartido con
        # token de bot, no un webhook dedicado a "newsletter"; SLACK_CHANNEL_NEWSLETTER
        # aquí trataba el valor como una URL de webhook completa, pero en el
        # resto del código ese nombre de variable es un channel ID — colisión
        # de nombres real detectada en la auditoría 2026-07-19, no solo duplicación.)
        print(f"  📤 Enviando {report_name} a Slack...")
        try:
            from slack_notify import deliver_to_publicaciones

            deliver_to_publicaciones(
                f"📢 *Nuevo Reporte de Inteligencia: {report_name.upper()}*\n\n{clean_content[:2000]}..."
            )
        except Exception as e:
            print(f"    ⚠️ Error en Slack: {e}")

        # 2. Enviar a WhatsApp (Proactivo)
        print(f"  📱 Enviando {report_name} a WhatsApp...")
        ws_body = f"🚀 *CLI Market Intelligence*\n\nReporte: *{report_name.upper()}*\n\n{clean_content[:800]}...\n\n_Para ver el reporte completo, usa el comando /intel en el bot._"
        send_whatsapp_proactive(WHATSAPP_TEST_NUMBER, ws_body)

    print("✅ Distribución completada.")

if __name__ == "__main__":
    distribute_reports()
