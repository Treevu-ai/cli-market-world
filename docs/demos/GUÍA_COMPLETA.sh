#!/bin/bash
# GUÍA COMPLETA: CLI Market - Máxima eficiencia y automatización

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════╗
║           CLI MARKET - GUÍA COMPLETA DE OPTIMIZACIÓN Y AUTOMATIZACIÓN    ║
║                    Para hoteles, restaurantes y negocios                 ║
╚════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
1. CONFIGURACIÓN INICIAL (Una sola vez)
═══════════════════════════════════════════════════════════════════════════════

✓ Paso 1: Configurar variables de entorno
   cp .env.example .env
   # Editar .env con tu token y configuración
   export MARKET_API_TOKEN="sk-tu-token-aqui"
   export MARKET_COUNTRY="PE"

✓ Paso 2: Inicializar contenedor principal
   docker-compose up -d market-cli

✓ Paso 3: Verificar credenciales
   docker exec market-cli market doctor

═══════════════════════════════════════════════════════════════════════════════
2. BÚSQUEDAS BÁSICAS (Diarias)
═══════════════════════════════════════════════════════════════════════════════

# Buscar un producto
docker exec market-cli market search "arroz extra" --country PE --limit 10

# Comparar precios entre retailers
docker exec market-cli market search "leche gloria" --country PE --limit 5

# Buscar con descuentos
docker exec market-cli market search "huevos" --country PE | grep -i "desc"

═══════════════════════════════════════════════════════════════════════════════
3. AUTOMATIZACIÓN CON SCHEDULER (Recomendado)
═══════════════════════════════════════════════════════════════════════════════

# Ejecutar scheduler manual (una vez)
./market-scheduler.sh

# O configurar cron job para automatización (Linux/Mac)
crontab -e

# Añadir estas líneas:
0 6 * * * /path/to/market-scheduler.sh     # 6 AM diarios
0 */6 * * * /path/to/market-scheduler.sh   # Cada 6 horas
0 9 * * 1 /path/to/market-scheduler.sh     # Lunes 9 AM (reporte semanal)

═══════════════════════════════════════════════════════════════════════════════
4. MONITOREO EN TIEMPO REAL CON PYTHON
═══════════════════════════════════════════════════════════════════════════════

# Generar reporte diario
python3 market-monitor.py report

# Buscar producto
python3 market-monitor.py search "arroz"

# Configurar alerta de precio (si arroz > S/ 5.00)
python3 market-monitor.py alert "arroz" 5.0

# Ver estado del sistema
python3 market-monitor.py status

═══════════════════════════════════════════════════════════════════════════════
5. WRAPPER API - ACCESO SIMPLIFICADO
═══════════════════════════════════════════════════════════════════════════════

# Buscar sin Docker manualmente
./market-api-wrapper.sh search "pollo" 5

# Comparar precios
./market-api-wrapper.sh compare "leche"

# Optimizar canasta
./market-api-wrapper.sh basket "arroz:98 pollo:147 leche:122.5"

# Verificar salud
./market-api-wrapper.sh health

═══════════════════════════════════════════════════════════════════════════════
6. STACK COMPLETO CON BASES DE DATOS Y CACHEO
═══════════════════════════════════════════════════════════════════════════════

# Levantar solución completa (CLI + Scheduler + Monitor + DB + Redis + MCP)
docker-compose -f docker-compose.complete.yml up -d

# Verificar todos los servicios
docker-compose -f docker-compose.complete.yml ps

# Ver logs
docker-compose -f docker-compose.complete.yml logs -f market-cli
docker-compose -f docker-compose.complete.yml logs -f market-scheduler
docker-compose -f docker-compose.complete.yml logs -f market-monitor

═══════════════════════════════════════════════════════════════════════════════
7. CONFIGURACIÓN AVANZADA - ALERTAS Y UMBRALES
═══════════════════════════════════════════════════════════════════════════════

# Editar market-config.json para:
- Configurar umbrales de precio máximo por producto
- Definir retailers preferidos y backup
- Establecer horarios de búsqueda automática
- Configurar notificaciones (email/WhatsApp/SMS)

vim market-config.json

Ejemplo de alerta:
{
  "alert_thresholds": {
    "arroz": {
      "max_price": 5.0,
      "alert_type": "email",
      "recipients": ["compras@hotel.com"]
    }
  }
}

═══════════════════════════════════════════════════════════════════════════════
8. EXPORTAR DATOS A EXCEL/CSV
═══════════════════════════════════════════════════════════════════════════════

# Exportar lista de productos a CSV
python3 market-monitor.py export-csv "arroz" "leche" "huevos" "pollo"

# Archivo generado: market-reports/market_prices_YYYYMMDD_HHMMSS.csv

# Ver reportes generados
ls -lah market-reports/daily/

═══════════════════════════════════════════════════════════════════════════════
9. ANÁLISIS DE BASES DE DATOS - HISTÓRICO DE PRECIOS
═══════════════════════════════════════════════════════════════════════════════

# Conectar a PostgreSQL
docker exec -it market-db psql -U market -d market_prices

# Queries útiles:
SELECT * FROM latest_prices ORDER BY price ASC;
SELECT * FROM price_trends WHERE date = CURRENT_DATE;
SELECT * FROM alerts WHERE is_active = TRUE;

═══════════════════════════════════════════════════════════════════════════════
10. OPTIMIZACIÓN DE CANASTA - MEJOR COSTO
═══════════════════════════════════════════════════════════════════════════════

# Buscar mejor precio por producto (bulk)
docker exec market-cli market search "arroz extra" --country PE --limit 1 | grep "Wong\|Metro\|Plaza Vea"

# Comparar retailers
docker exec market-cli market search "pollo" --country PE --limit 3

# Estrategia multi-retailer:
1. Comprar arroz en Wong (más barato)
2. Comprar leche en Metro (descuentos frecuentes)
3. Comprar frutas en Plaza Vea (variedad)

═══════════════════════════════════════════════════════════════════════════════
11. INTEGRACIÓN CON CLAUDE/CURSOR (MCP)
═══════════════════════════════════════════════════════════════════════════════

# MCP ya está configurado en docker-compose.complete.yml
# Acceso en Cursor/Claude:
market-mcp en puerto 3000

# Usar en Cursor:
- Abre el comando pallette
- Escribe: "market search arroz"
- El MCP ejecutará búsquedas directamente en Claude

═══════════════════════════════════════════════════════════════════════════════
12. CASOS DE USO ESPECÍFICOS
═══════════════════════════════════════════════════════════════════════════════

### CASO 1: Hotel necesita compra urgente de 70 personas
✓ docker exec market-cli market search "pollo" --country PE --limit 5
✓ Identificar mejor precio
✓ Ejecutar compra multi-retailer

### CASO 2: Monitorear precio del arroz (insumo crítico)
✓ python3 market-monitor.py alert "arroz" 4.50
✓ Scheduler automático notifica si precio > S/ 4.50

### CASO 3: Análisis semanal de gastos
✓ python3 market-monitor.py report
✓ Exportar: python3 market-monitor.py export-csv "arroz" "leche" "huevos"
✓ Ver en Excel

### CASO 4: Comparativa mensual de retailers
✓ Base de datos PostgreSQL almacena 30 días de histórico
✓ Ver trends: SELECT * FROM price_trends;
✓ Identificar patrones de precios

═══════════════════════════════════════════════════════════════════════════════
13. TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

Problema: "No authentication found"
Solución: docker exec market-cli market init

Problema: "Container exits immediately"
Solución: docker logs market-cli

Problema: "Timeout en búsquedas"
Solución: Aumentar timeout en market-config.json

Problema: "No se ejecutan alertas"
Solución: Verificar market-config.json y permisos

═══════════════════════════════════════════════════════════════════════════════
14. COMANDOS RÁPIDOS (COPY-PASTE)
═══════════════════════════════════════════════════════════════════════════════

# Iniciar todo de cero
docker-compose -f docker-compose.complete.yml up -d && sleep 5 && docker exec market-cli market doctor

# Ver últimos 100 logs
docker-compose logs -f --tail=100

# Parar todo sin borrar datos
docker-compose -f docker-compose.complete.yml stop

# Reiniciar servicios
docker-compose -f docker-compose.complete.yml restart

# Limpiar contenedores pero mantener datos
docker-compose -f docker-compose.complete.yml down

# Acceso a base de datos
docker exec -it market-db psql -U market -d market_prices -c "SELECT * FROM latest_prices LIMIT 10;"

═══════════════════════════════════════════════════════════════════════════════
15. CHECKLIST DE PRODUCTIVIDAD MÁXIMA
═══════════════════════════════════════════════════════════════════════════════

□ Token API guardado en .env (seguro)
□ Contenedor main ejecutándose
□ Scheduler automatizado cada 6 horas
□ Alertas configuradas para productos críticos
□ Base de datos con histórico de precios
□ Reportes generados automáticamente
□ MCP integrado en Cursor/Claude
□ Exportación a Excel funcionando
□ Redis cacheo activo
□ Monitoreo 24/7 en ejecución

═══════════════════════════════════════════════════════════════════════════════

¿Preguntas? Consulta cli-market.dev/docs

EOF
