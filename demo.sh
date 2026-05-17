#!/usr/bin/env bash
# demo.sh — CLI Agentic Market demo script
# Grabar con: asciinema rec demo.cast --command "bash demo.sh"

P="sleep 1.5"
PS="sleep 0.6"
PF="sleep 2.5"

clear
$P

echo "██████╗██╗     ██╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗██╗ ██████╗"
echo "██╔════╝██║     ██║    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██║██╔════╝"
echo "██║     ██║     ██║    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██║██║"
echo "██║     ██║     ██║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██║██║"
echo "╚██████╗███████╗██║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ██║╚██████╗"
echo " ╚═════╝╚══════╝╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝ ╚═════╝"
echo " ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗███████╗████████╗"
echo " ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝╚══██╔══╝"
echo " ██╔████╔██║███████║██████╔╝█████╔╝ █████╗     ██║"
echo " ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝     ██║"
echo " ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗███████╗   ██║"
echo " ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝"
echo ""
echo "CLI AGENTIC MARKET · v1.0"
echo "Supermarkets as programmable commerce"
echo ""
echo "Stripe transformo pagos en APIs."
echo "Nosotros transformamos supermercados en APIs para agentes IA."
$PF

echo ""
echo "$ market login"
$PS
echo "Autenticado como admin"
$P

echo ""
echo "$ market search 'leche' --limit 5"
$PF
echo "  #  Producto            Marca     Tienda    Precio   Desc."
echo "  1  Leche Gloria        Gloria    P.Vea     S/5.90    3%"
echo "  2  Leche de Tigre      Tiger     Metro     S/8.90    --"
echo "  3  Leche Condensada    Nestle    Wong      S/3.90    20%"
echo "  4  Tollo Leche Entero  Generico  Metro     S/45.50   --"
echo "  5  Choc. con Leche     Triangulo Wong      S/1.70    --"
echo "  5 resultados en Wong, Metro y Plaza Vea"
$P

echo ""
echo "$ market compare 'aceite'"
$PF
echo "  #  Producto           Wong      Metro     P.Vea     Mejor   Ahorro"
echo "  1  Aceite Carbonell   S/25.90   S/17.90   --        Metro   S/8.00"
echo "  2  Aceite Primor      S/11.90   S/10.90   S/9.90    P.Vea   S/2.00"
echo "  3  Aceite SAO         S/5.90    --        S/5.50    P.Vea   S/0.40"
$P

echo ""
echo "$ market ask 'compra lo mas barato'"
$PF
echo "Agregue 'Aceite BELLS 900ml' de Plaza Vea a S/5.50"
echo "Carrito: 1 item, S/5.50"
$P

echo ""
echo "$ market --json"
$PF
echo '{'
echo '  "company": "CLI AGENTIC MARKET",'
echo '  "pitch": "Stripe transformed payments into APIs.'
echo '           CLI AGENTIC MARKET transforms supermarkets'
echo '           into APIs for AI agents."'
echo '}'
$P

echo ""
echo "  pip install agentic-market"
echo "  github.com/tuuser/agentic-market"
echo ""
echo "  Human-friendly > Terminal CLI"
echo "  Agent-friendly  > REST API - MCP Tools - JSON"
$PF

echo ""
echo "[Fin de la demo]"
