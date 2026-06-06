#!/usr/bin/env bash
# Bundle cli-market-core into the cli-market sdist/wheel (PyPI ships one installable package).
set -euo pipefail
CORE="${1:-cli-market-core}"
test -d "$CORE/market_core"
test -d "$CORE/market_connectors"

rm -rf market_core market_connectors
cp -r "$CORE/market_core" .
cp -r "$CORE/market_connectors" .

for mod in store_credentials market_stats retailer_onboarding market_security market_alerts \
  market_basket market_spread market_units market_db market_indicators market_enrich_subcategory \
  market_billing market_mcp market_intel_agent market_health_alert market_enrich_sources \
  data_v1_service dashboard_glossary dashboard_quality dashboard_renderer dashboard_view_model \
  source_health price_confidence; do
  if [ -f "$CORE/${mod}.py" ]; then
    cp "$CORE/${mod}.py" .
  fi
done

echo "Vendored cli-market-core into $(pwd)"