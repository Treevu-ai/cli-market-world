# -*- coding: utf-8 -*-
import os
import subprocess
import time
from datetime import datetime

import httpx

# --- CONFIGURACION ---
API_URL = "https://cli-market-api.fly.dev"
APP_NAME = "cli-market-collector"
STALE_THRESHOLD_SECONDS = 86400  # 24 horas
CHECK_INTERVAL = 3600  # Verificar cada hora
API_TOKEN = os.environ["MARKET_API_TOKEN"]


def check_freshness():
    print(f"[{datetime.now().isoformat()}] Verificando salud del datamoat...")
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = httpx.get(f"{API_URL}/v1/quality/scores", headers=headers, timeout=20.0)
        response.raise_for_status()
        data = response.json()

        # El envelope de CLI Market pone la frescura en meta o en el cuerpo
        freshness = data.get("meta", {}).get("freshness_seconds") or data.get("freshness_seconds")

        if freshness is None:
            print("  ⚠ No se pudo encontrar la metrica de frescura en la respuesta.")
            return "unknown"

        print(f"  ✓ Frescura actual: {freshness} segundos ({(freshness / 3600):.1f} horas)")

        if freshness > STALE_THRESHOLD_SECONDS:
            print("  ⚠ ESTADO: STALE. Los datos tienen mas de 24h.")
            return "stale"

        print("  ✓ ESTADO: HEALTHY.")
        return "healthy"

    except Exception as e:
        print(f"  ✗ Error al consultar la API: {e}")
        return "error"


def heal_system():
    print(f"  ⚙ Iniciando proceso de auto-curacion para {APP_NAME}...")
    try:
        result = subprocess.run(
            ["fly", "apps", "restart", APP_NAME],
            capture_output=True,
            text=True,
            shell=True,
        )
        if result.returncode == 0:
            print("  ✓ Collector reiniciado exitosamente.")
        else:
            print(f"  ✗ Fallo al reiniciar: {result.stderr}")
    except Exception as e:
        print(f"  ✗ Error critico en la curacion: {e}")


def main():
    print("🛡 CLI Market Health Watchdog iniciado.")
    print(f"Umbral de alerta: {STALE_THRESHOLD_SECONDS}s | Intervalo: {CHECK_INTERVAL}s\n")

    while True:
        status = check_freshness()
        if status == "stale":
            heal_system()
        elif status == "error":
            print("  ⚠ El sistema de monitoreo tiene un problema, reintentando en el proximo ciclo...")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
