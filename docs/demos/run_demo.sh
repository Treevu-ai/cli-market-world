#!/usr/bin/env bash
# 🚀 QUICK START: Market Optimizer Agent Demo
# Ejecuta esto para ver el agente en acción

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║      🚀 MARKET OPTIMIZER AGENT - QUICK START                 ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que estamos en la carpeta correcta
if [ ! -f "market_optimizer_agent.py" ]; then
    echo "❌ Error: No estás en C:\Users\acuba\cli-market-world\"
    echo "   Cambia a esa carpeta primero:"
    echo "   cd C:\Users\acuba\cli-market-world"
    exit 1
fi

echo "✓ Carpeta correcta"
echo ""

# Verificar Python
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python no está instalado"
        exit 1
    fi
    PYTHON="python3"
else
    PYTHON="python"
fi

echo "✓ Python disponible: $PYTHON"
echo ""

# Verificar que el módulo existe
if [ ! -f "market_optimizer_agent.py" ]; then
    echo "❌ market_optimizer_agent.py no encontrado"
    exit 1
fi

echo "✓ market_optimizer_agent.py encontrado"
echo ""

# Verificar que la demo existe
if [ ! -f "demo_optimizer_corrected.py" ]; then
    echo "❌ demo_optimizer_corrected.py no encontrado"
    exit 1
fi

echo "✓ demo_optimizer_corrected.py encontrado"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎬 Ejecutando demo..."
echo ""
echo "La demo muestra:"
echo "  1. Query Optimization (mejora de búsquedas)"
echo "  2. Response Enrichment (deduplicación + ranking)"
echo "  3. Recommendations (5+ tipos de insights)"
echo "  4. Full Pipeline (flujo completo)"
echo "  5. Caching & Performance (368x speedup)"
echo "  6. Real-World Use Cases (aplicaciones prácticas)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ejecutar la demo
$PYTHON demo_optimizer_corrected.py

EXIT_CODE=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Demo completada exitosamente!"
    echo ""
    echo "Próximos pasos:"
    echo "  1. Lee: DEMO_SCRIPT_SUMMARY.txt"
    echo "  2. Lee: market_optimizer_agent.py (comentado)"
    echo "  3. Integra en: market_cli.py"
    echo "  4. Usa en: pricing-consultant.py"
    echo ""
else
    echo "❌ La demo falló con código: $EXIT_CODE"
    echo ""
    echo "Troubleshooting:"
    echo "  • Verifica que Python 3.7+ está instalado"
    echo "  • Verifica que market_optimizer_agent.py existe"
    echo "  • Intenta: python demo_optimizer_corrected.py"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

exit $EXIT_CODE
