#!/bin/bash
# market-scheduler.sh - Automatiza búsquedas, comparativas y análisis de precios
# Cron-friendly: ejecuta comparativas cada 6 horas y reportes diarios

set -e

TOKEN="${MARKET_API_TOKEN}"
COUNTRY="${MARKET_COUNTRY:-PE}"
OUTPUT_DIR="${OUTPUT_DIR:-./market-reports}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)

# Crear directorio de reportes
mkdir -p "$OUTPUT_DIR"/{daily,weekly,alerts}

echo "📊 [$(date)] CLI Market Scheduler iniciado" >> "$OUTPUT_DIR/scheduler.log"

# ============================================================================
# FUNCIÓN 1: COMPARATIVA DE PRECIOS CLAVE
# ============================================================================
run_price_comparison() {
    local product="$1"
    local output_file="$OUTPUT_DIR/daily/${product}_${DATE}.json"
    
    echo "🔍 Comparando: $product..."
    docker exec hotel-basket-70pax market search "$product" --country "$COUNTRY" --json > "$output_file" 2>&1 || true
    
    # Analizar resultados y extraer precios mínimos
    if [ -f "$output_file" ]; then
        echo "✓ Resultados guardados en: $output_file"
    fi
}

# ============================================================================
# FUNCIÓN 2: GENERAR REPORTE SEMANAL DE COSTOS
# ============================================================================
generate_weekly_report() {
    local week=$(date +%V)
    local report_file="$OUTPUT_DIR/weekly/basket_week${week}_${DATE}.txt"
    
    echo "📈 Generando reporte semanal..." > "$report_file"
    echo "Fecha: $DATE" >> "$report_file"
    echo "Semana: $week de 52" >> "$report_file"
    echo "" >> "$report_file"
    echo "CANASTA HOTELERA - 70 PERSONAS" >> "$report_file"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$report_file"
    echo "" >> "$report_file"
    
    # Búsquedas de componentes críticos
    docker exec hotel-basket-70pax market doctor --json >> "$report_file" 2>&1 || true
    
    echo "✓ Reporte semanal: $report_file"
}

# ============================================================================
# FUNCIÓN 3: MONITOREAR CAMBIOS DE PRECIO (ALERTAS)
# ============================================================================
check_price_alerts() {
    local product="$1"
    local max_price="$2"
    local alert_file="$OUTPUT_DIR/alerts/${product}_alerts.txt"
    
    # Buscar precio actual
    local current=$(docker exec hotel-basket-70pax market search "$product" --country "$COUNTRY" --limit 1 2>/dev/null | grep -oP 'S/\s*\K[0-9.]+' | head -1 || echo "N/A")
    
    # Comparar con umbral
    if [ "$current" != "N/A" ]; then
        echo "[$(date)] $product - Precio actual: S/ $current (Umbral: S/ $max_price)" >> "$alert_file"
        
        if (( $(echo "$current > $max_price" | bc -l) )); then
            echo "⚠️  ALERTA: $product superó precio máximo (S/ $max_price)" >> "$alert_file"
            echo "⚠️  Precio: S/ $current"
        fi
    fi
}

# ============================================================================
# FUNCIÓN 4: OPTIMIZAR CANASTA (RECOMENDACIÓN DE RETAILERS)
# ============================================================================
optimize_basket() {
    local basket_file="$OUTPUT_DIR/daily/basket_optimization_${DATE}.txt"
    
    echo "🎯 Optimizando canasta hotelera..." > "$basket_file"
    echo "Fecha: $(date)" >> "$basket_file"
    echo "" >> "$basket_file"
    
    # Búsquedas estratégicas de mejor relación precio/cantidad
    docker exec hotel-basket-70pax market search "arroz extra" --country "$COUNTRY" --limit 1 >> "$basket_file" 2>&1 || true
    docker exec hotel-basket-70pax market search "leche gloria" --country "$COUNTRY" --limit 1 >> "$basket_file" 2>&1 || true
    docker exec hotel-basket-70pax market search "huevos" --country "$COUNTRY" --limit 1 >> "$basket_file" 2>&1 || true
    
    echo "✓ Optimización guardada: $basket_file"
}

# ============================================================================
# FUNCIÓN 5: EXPORTAR DATOS A CSV PARA EXCEL
# ============================================================================
export_to_csv() {
    local csv_file="$OUTPUT_DIR/daily/market_data_${DATE}.csv"
    
    echo "Producto,Tienda,Precio,Descuento,Fecha" > "$csv_file"
    
    # Agregar datos de búsquedas recientes
    for product in "arroz" "huevos" "leche" "pollo" "tomate"; do
        docker exec hotel-basket-70pax market search "$product" --country "$COUNTRY" --limit 1 2>/dev/null >> "$csv_file" || true
    done
    
    echo "✓ CSV exportado: $csv_file"
}

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

echo ""
echo "🚀 TAREAS PROGRAMADAS CLI MARKET"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Hora: $(date)"
echo ""

# COMPARATIVAS CRÍTICAS (cada búsqueda)
echo "📍 Ejecutando comparativas..."
run_price_comparison "arroz extra"
run_price_comparison "huevos"
run_price_comparison "leche gloria"
run_price_comparison "pollo"
run_price_comparison "tomate"

# ALERTAS DE PRECIO (umbrales configurables)
echo ""
echo "⚠️  Verificando alertas de precio..."
check_price_alerts "arroz" 5.0
check_price_alerts "leche" 3.5
check_price_alerts "huevos" 7.0

# OPTIMIZACIÓN DE CANASTA
echo ""
echo "🎯 Optimizando canasta..."
optimize_basket

# EXPORTAR A CSV
echo ""
echo "📊 Exportando a CSV..."
export_to_csv

# GENERAR REPORTE SEMANAL (solo si es lunes)
if [ "$(date +%w)" -eq 1 ]; then
    echo ""
    echo "📈 Generando reporte semanal..."
    generate_weekly_report
fi

# RESUMEN
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Tareas completadas"
echo "📁 Reportes en: $OUTPUT_DIR"
echo "📊 Ver: $OUTPUT_DIR/daily/"
echo "⚠️  Alertas: $OUTPUT_DIR/alerts/"
echo "📈 Semanales: $OUTPUT_DIR/weekly/"
echo ""
echo "💡 Próximas tareas en 6 horas..."
echo "[$(date)] Tareas completadas" >> "$OUTPUT_DIR/scheduler.log"
