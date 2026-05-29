#!/usr/bin/env python3
"""CLI Market — LinkedIn Outreach Scripts Generator."""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from market_stores import STORES

DM_ES = """Hola:

CLI Market indexa precios de 30 retailers en 7 países de LATAM para agentes de IA. Ya tenemos Wong, Metro, Carrefour, Chedraui, HEB y otros.

{store_name} está en nuestra lista de prioridades.

Solo necesitamos un token de API de solo lectura (catálogo). Son 30 segundos de configuración. Sin costo, sin integración, sin acceso a datos de clientes.

A cambio, sus productos aparecen en búsquedas y comparaciones de agentes autónomos, junto a 30 retailers.

¿Le interesa conversarlo?

Antonio Cuba
CLI Market · cli-market.dev"""

DM_EN = """Hi! 👋

CLI Market indexes prices from 30 retailers across 7 countries for AI agents. We already have major LATAM retailers onboard.

{store_name} is on our priority list.

All we need is a read-only API token (catalog access). 30 second setup. No cost, no technical integration, no customer data access.

In exchange, your products appear in searches and comparisons by autonomous AI agents, alongside 30 retailers.

Interested in a quick chat?

Antonio Cuba
CLI Market · cli-market.dev"""

DM_BR = """Ola! 👋

A CLI Market indexa precos de 30 varejistas em 7 paises para agentes de IA. Ja temos os principais varejistas LATAM a bordo.

{store_name} esta na nossa lista de prioridades.

So precisamos de um token de API somente leitura. 30 segundos. Sem custo, sem integracao, sem acesso a dados de clientes.

Em troca, seus produtos aparecem em buscas e comparacoes de agentes autonomos, ao lado de 30 varejistas.

Vamos conversar?

Antonio Cuba
CLI Market · cli-market.dev"""

LOCALE = {
    "AR": "es", "PE": "es", "MX": "es", "CO": "es", "CL": "es", "ES": "es",
    "US": "en", "UK": "en", "CH": "en", "IT": "en", "FR": "en", "BR": "br",
}


def dm_for(store_id, info):
    name = info.get("name", store_id)
    country = info.get("country", "??")
    loc = LOCALE.get(country, "en")
    if loc == "br": return DM_BR.format(store_name=name)
    if loc == "es": return DM_ES.format(store_name=name)
    return DM_EN.format(store_name=name)


def main():
    shopify = {k: v for k, v in STORES.items() if v.get("platform") == "shopify"}
    magento = {k: v for k, v in STORES.items() if v.get("platform") == "magento"}
    dead = {k: v for k, v in STORES.items() if v.get("platform") in ("need_token",) 
            or (v.get("platform") == "vtex" and k in ("cruzverde_cl", "cruzverde_co", "farmatodo_co"))}

    print("# CLI Market — LinkedIn Outreach Scripts")
    print(f"**Date:** {datetime.now().isoformat()[:19]}")
    print(f"**Total:** {len(shopify) + len(magento) + len(dead)} stores")
    print()

    for title, stores in [
        ("## Shopify — 15 stores (Storefront API token)", shopify),
        ("## Magento — 7 stores (REST API catalog read)", magento),
        ("## VTEX dead / need_token — 8 stores", dead),
    ]:
        print(title)
        print()
        for sid, info in sorted(stores.items(), key=lambda x: x[1].get("country", "")):
            name = info.get("name", sid)
            country = info.get("country", "??")
            line = info.get("line", "?")
            site = info.get("base", "")
            plat = info.get("platform", "vtex")
            print(f"### {name} ({country}) — {line} — {plat}")
            print(f"Site: {site}")
            print()
            print("```")
            print(dm_for(sid, info))
            print("```")
            print()
        print("---")
        print()


if __name__ == "__main__":
    main()
