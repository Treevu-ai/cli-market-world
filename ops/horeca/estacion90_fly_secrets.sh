#!/usr/bin/env bash
# Estación 90 — secrets Fly.io para piloto HORECA (Surco, PE)
# Uso: bash ops/horeca/estacion90_fly_secrets.sh

set -euo pipefail

fly secrets set HORECA_ENABLED=true
fly secrets set HORECA_FREE_SEARCHES_DAILY=5
fly secrets set HORECA_COOLDOWN_HOURS=4
fly secrets set HORECA_MAX_CONCURRENT_SEARCHES=3
fly secrets set HORECA_PRIORITY_CATEGORIES=aceites,limpieza,papel,bebidas,electrodomesticos
fly secrets set HORECA_SAVINGS_NOTIFICATION_THRESHOLD=50.0

# Reemplazar con el WhatsApp del encargado de cocina/compras en Estación 90
fly secrets set HORECA_ESTACION90_WHATSAPP=whatsapp:+51XXXXXXXXX
fly secrets set HORECA_ESTACION90_AUTO_SEED=true
fly secrets set HORECA_ESTACION90_BUSINESS_NAME="Estación 90"
fly secrets set HORECA_ESTACION90_STORES=wong,metro,plazavea
fly secrets set HORECA_ESTACION90_MENU_URL=https://estacion90.pe/api/menu.json

# Puente WhatsApp → Procure Copilot (mismo PROCURE_E2E_SECRET que Workers)
fly secrets set PROCURE_COPILOT_URL=https://procure-copilot.contacto-8e4.workers.dev
fly secrets set PROCURE_E2E_SECRET=your_procure_e2e_secret
fly secrets set PROCURE_ESTACION90_ORG=estacion90
fly secrets set PROCURE_ESTACION90_PLAN=pro

echo "✓ Secrets HORECA Estación 90 configurados. Ejecutá: fly deploy"
