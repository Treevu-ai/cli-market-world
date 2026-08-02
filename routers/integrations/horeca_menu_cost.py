"""Estimación de costo de insumos del menú Estación 90 vía supermercados PE."""

from __future__ import annotations

import os
from typing import Any

import httpx

from .horeca_profiles import ESTACION90_PROCUREMENT_STORES

DEFAULT_MENU_URL = os.getenv(
    "HORECA_ESTACION90_MENU_URL",
    "https://estacion90.pe/api/menu.json",
)


def _dish_lookup(menu: dict) -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    for cat in menu.get("categories") or []:
        for item in cat.get("items") or []:
            if isinstance(item, dict) and item.get("id"):
                lookup[str(item["id"])] = item
    return lookup


def collect_menu_dishes(menu: dict, *, category_id: str | None = None) -> list[dict]:
    """Platos disponibles del menú (opcionalmente filtrados por categoría)."""
    dishes: list[dict] = []
    for cat in menu.get("categories") or []:
        if category_id and cat.get("id") != category_id:
            continue
        for item in cat.get("items") or []:
            if isinstance(item, dict) and item.get("available", True):
                dishes.append({**item, "category_id": cat.get("id"), "category_name": cat.get("name")})
    return dishes


def collect_ingredients_for_dishes(menu: dict, dish_ids: list[str] | None = None) -> list[str]:
    """Ingredientes únicos para platos del menú (mapeo dish_ingredients)."""
    dish_map = {str(d.get("dish_id")): d for d in menu.get("dish_ingredients") or []}
    if dish_ids is None:
        dish_ids = [str(d["id"]) for d in collect_menu_dishes(menu, category_id="menu_dia")]
    seen: set[str] = set()
    ingredients: list[str] = []
    for dish_id in dish_ids:
        entry = dish_map.get(dish_id)
        if not entry:
            continue
        for ing in entry.get("ingredients") or []:
            key = str(ing).strip().lower()
            if key and key not in seen:
                seen.add(key)
                ingredients.append(str(ing).strip())
    return ingredients


def build_menu_cost_question(ingredients: list[str], stores: list[str] | None = None) -> str:
    """Pregunta para market_optimize / intel ask con retailers Surco."""
    stores = stores or ESTACION90_PROCUREMENT_STORES
    store_list = ", ".join(stores)
    items = ", ".join(ingredients)
    return (
        f"Optimiza la compra de insumos para cocina de restaurante en Lima (Surco): {items}. "
        f"Compara precios en {store_list}. País PE, moneda PEN. "
        "Indica total estimado por tienda y ahorro vs comprar todo en un solo retailer."
    )


async def fetch_menu(menu_url: str | None = None) -> dict:
    url = menu_url or DEFAULT_MENU_URL
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        payload = resp.json()
        return payload if isinstance(payload, dict) else {}


async def estimate_menu_ingredient_cost(
    *,
    menu_url: str | None = None,
    category_id: str = "menu_dia",
    stores: list[str] | None = None,
    market_api_url: str,
    token: str,
) -> dict[str, Any]:
    """Estima costo de insumos del menú del día consultando la API CLI Market."""
    menu = await fetch_menu(menu_url)
    dishes = collect_menu_dishes(menu, category_id=category_id)
    dish_ids = [str(d["id"]) for d in dishes]
    ingredients = collect_ingredients_for_dishes(menu, dish_ids)
    if not ingredients:
        return {
            "ok": False,
            "error": "No hay ingredientes mapeados para el menú solicitado.",
            "dishes": dishes,
        }
    question = build_menu_cost_question(ingredients, stores)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{market_api_url.rstrip('/')}/v1/intel/ask",
            json={"question": question},
            headers=headers,
        )
        if resp.status_code != 200:
            return {
                "ok": False,
                "error": f"API error {resp.status_code}",
                "ingredients": ingredients,
                "dishes": dishes,
            }
        answer = resp.json().get("answer", "")
    dish_lines = "\n".join(
        f"• {d.get('name')}: S/ {float(d.get('price') or 0):.2f}" for d in dishes if d.get("price")
    )
    return {
        "ok": True,
        "dishes": dishes,
        "ingredients": ingredients,
        "stores": stores or ESTACION90_PROCUREMENT_STORES,
        "question": question,
        "answer": answer,
        "summary_header": (
            f"🍽️ *Menú del día — Estación 90*\n"
            f"{dish_lines}\n\n"
            f"🛒 *Insumos estimados ({len(ingredients)} ítems)* en "
            f"{', '.join(stores or ESTACION90_PROCUREMENT_STORES)}:\n"
        ),
    }


def format_menu_cost_response(result: dict[str, Any]) -> str:
    """Formatea respuesta para WhatsApp HORECA."""
    if not result.get("ok"):
        return f"❌ No pude estimar el costo del menú: {result.get('error', 'error desconocido')}"
    return f"{result['summary_header']}{result.get('answer', '')}"
