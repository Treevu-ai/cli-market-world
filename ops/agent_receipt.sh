#!/bin/bash
# Agent Receipt — CLI Market Demo Script (~45s)
# Record: terminalizer record demo -c ops/terminalizer.yml
# Landing now uses landing/components/HeroDemo.tsx (live terminal animation).

clear
echo ""
echo "  🤖 AGENT: \"Compara arroz en Perú y arma una canasta.\""
sleep 2

echo -n "  \$ "; sleep 0.5; echo "pip install cli-market-world"
sleep 1; echo "  ✓ cli-market-world 1.9.6"
sleep 1

echo ""; echo -n "  \$ "; sleep 0.3; echo "market init"
sleep 1; echo "  ✓ 38 retailers verificados · 22 MCP · 8 países"
sleep 2

echo ""; echo -n "  \$ "; sleep 0.3
echo 'market compare "arroz" --country PE'
sleep 2
echo ""
echo "  Metro S/2.90 · Wong S/3.10 · Plaza Vea S/2.95 · /kg"
sleep 2

echo ""; echo -n "  \$ "; sleep 0.3
echo 'market basket "arroz:1 leche:1" --country PE'
sleep 2
echo ""
echo "  Mejor: Metro S/12.40 · ahorro S/1.20 vs promedio"
sleep 2

echo ""; echo -n "  \$ "; sleep 0.3; echo "market tools"
sleep 1
echo "  Shop (11) · Intel (6) · Account (5) · default profile"
sleep 2

echo ""
echo "  ─────────────────────────────────────────"
echo "  🧾  AGENT RECEIPT"
echo "  ─────────────────"
echo "  Comparado:  38 retailers · PE"
echo "  Canasta:    Metro · S/12.40"
echo "  MCP:        22 curated (46 legacy)"
echo "  Tiempo:     <15 segundos"
echo "  ─────────────────"
echo "  cli-market.dev  ·  MIT  ·  pip install cli-market-world"
echo ""
sleep 5