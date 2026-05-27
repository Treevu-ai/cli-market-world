#!/bin/bash
# Agent Receipt — CLI Market Demo Script (~60s)
# Record: terminalizer record demo -c ops/terminalizer.yml
# Or just screen-record this running.

clear
echo ""
echo "  🤖 AGENT: \"Busca leche al mejor precio en Peru.\""
sleep 2

echo -n "  \$ "; sleep 0.5; echo "market login"
sleep 1; echo "  ✓ Authenticated — 30 retailers ready."
sleep 2

echo ""; echo -n "  \$ "; sleep 0.3
echo "market search \"leche\" --country PE"
sleep 2
echo ""
echo "  ╭──────────────┬─────────┬────────┬────────╮"
echo "  │ Retailer     │ Product │ Price  │ Stock  │"
echo "  ├──────────────┼─────────┼────────┼────────┤"
echo "  │ Metro        │ Leche   │ S/3.90 │ ✓      │"
echo "  │ Wong         │ Leche   │ S/4.20 │ ✓      │"
echo "  │ Plaza Vea    │ Leche   │ S/4.50 │ ✓      │"
echo "  ╰──────────────┴─────────┴────────┴────────╯"
sleep 3

echo ""; echo -n "  \$ "; sleep 0.3
echo "market compare \"arroz\" --countries PE,CO,BR"
sleep 2
echo ""
echo "  Mejor: Metro PE · S/2.80"
echo "  Ahorro: S/0.70/unidad vs. promedio"
echo "  Comparado: 12 retailers en 3 paises"
sleep 2

echo ""; echo -n "  \$ "; sleep 0.3
echo "market basket leche:2 arroz:1 aceite:1 --country PE"
sleep 2
echo ""
echo "  ╭────────────────┬──────┬───────┬──────────╮"
echo "  │ Retailer       │ Items│ Total │ Ahorro   │"
echo "  ├────────────────┼──────┼───────┼──────────┤"
echo "  │ Metro          │ 4/4  │ S/14.80│ —       │"
echo "  │ Wong           │ 4/4  │ S/15.90│ -S/1.10  │"
echo "  │ Plaza Vea      │ 3/4  │ S/16.50│ -S/1.70  │"
echo "  ╰────────────────┴──────┴───────┴──────────╯"
sleep 3

echo ""; echo -n "  \$ "; sleep 0.3
echo "market add 12345 --qty 2 && market add 67890 --qty 1"
sleep 1
echo "  2x Leche Gloria → carrito"
echo "  1x Arroz Costeno → carrito"
echo "  Subtotal: S/10.60 · Metro"
sleep 2

echo ""; echo -n "  \$ "; sleep 0.3
echo "market checkout --payment yape"
sleep 1
echo ""
echo "  ✓ Orden confirmada #ORD-A7F3B91C"
echo "  📱 QR Yape generado — vigencia: 5 min"
echo "  🔔 Webhook: POST https://miapp.com/order-webhook"
sleep 2

echo ""
echo "  ─────────────────────────────────────────"
echo "  🧾  AGENT RECEIPT"
echo "  ─────────────────"
echo "  Buscado:    leche, arroz, aceite"
echo "  Comparado:  30 retailers · 7 paises"
echo "  Comprado:   Metro · S/10.60"
echo "  Pagado:     Yape · ORD-A7F3B91C"
echo "  Tiempo:     12 segundos"
echo "  ─────────────────"
echo "  cli-market.dev  ·  MIT  ·  pip install cli-market"
echo ""
sleep 5
