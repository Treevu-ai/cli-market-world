#!/bin/bash
# market-api-wrapper.sh - API REST para acceso a CLI Market sin Docker
# Uso: ./market-api-wrapper.sh search "arroz" | jq
# O: curl http://localhost:8001/api/search?q=arroz

set -e

PORT="${MARKET_API_PORT:-8001}"
TOKEN="${MARKET_API_TOKEN}"
COUNTRY="${MARKET_COUNTRY:-PE}"

# ============================================================================
# Función: Search endpoint
# ============================================================================
search_product() {
    local query="$1"
    local limit="${2:-5}"
    
    docker exec hotel-basket-70pax market search "$query" \
        --country "$COUNTRY" \
        --limit "$limit" \
        --json 2>/dev/null | jq . || echo '{"error":"search failed"}'
}

# ============================================================================
# Función: Compare endpoint
# ============================================================================
compare_product() {
    local product="$1"
    
    docker exec hotel-basket-70pax market search "$product" \
        --country "$COUNTRY" \
        --limit 10 \
        --json 2>/dev/null | jq . || echo '{"error":"comparison failed"}'
}

# ============================================================================
# Función: Basket optimization
# ============================================================================
optimize_basket() {
    local items="$1"  # "arroz:98 pollo:147 leche:122.5"
    
    docker exec hotel-basket-70pax market basket "$items" \
        --country "$COUNTRY" \
        2>/dev/null || echo '{"error":"basket optimization failed"}'
}

# ============================================================================
# Función: Health check
# ============================================================================
health_check() {
    docker exec hotel-basket-70pax market doctor --json 2>/dev/null | jq . || echo '{"status":"unhealthy"}'
}

# ============================================================================
# MAIN: CLI Interface
# ============================================================================

case "${1:-help}" in
    search)
        search_product "$2" "${3:-5}"
        ;;
    compare)
        compare_product "$2"
        ;;
    basket)
        optimize_basket "$2"
        ;;
    health)
        health_check
        ;;
    *)
        echo "Market CLI Wrapper v1.0"
        echo ""
        echo "Uso:"
        echo "  ./market-api-wrapper.sh search <producto> [limit]"
        echo "  ./market-api-wrapper.sh compare <producto>"
        echo "  ./market-api-wrapper.sh basket '<items>'"
        echo "  ./market-api-wrapper.sh health"
        echo ""
        echo "Ejemplos:"
        echo "  ./market-api-wrapper.sh search 'arroz' 10"
        echo "  ./market-api-wrapper.sh compare 'leche gloria'"
        echo "  ./market-api-wrapper.sh basket 'arroz:98 pollo:147'"
        echo ""
        ;;
esac
