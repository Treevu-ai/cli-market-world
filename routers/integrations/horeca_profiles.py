"""Gestión de perfiles HORECA y lógica de negocio."""

import os
import re
from datetime import datetime, timedelta
from typing import Dict
from market_core import get_db

# Configuración HORECA desde variables de entorno
HORECA_COOLDOWN_HOURS = int(os.getenv("HORECA_COOLDOWN_HOURS", "4"))
HORECA_FREE_SEARCHES_DAILY = int(os.getenv("HORECA_FREE_SEARCHES_DAILY", "5"))
ESTACION90_BUSINESS_NAME = os.getenv("HORECA_ESTACION90_BUSINESS_NAME", "Estación 90")
ESTACION90_PROCUREMENT_STORES = [
    s.strip() for s in os.getenv("HORECA_ESTACION90_STORES", "wong,metro,plazavea").split(",") if s.strip()
]


def get_or_create_profile(whatsapp_number: str, business_name: str = "Desconocido", business_type: str = "pending") -> Dict:
    """Obtiene o crea un perfil HORECA."""
    db = get_db()
    
    try:
        # Intentar obtener perfil existente
        row = db.execute(
            "SELECT * FROM horeca_profiles WHERE whatsapp_number = ?",
            (whatsapp_number,)
        ).fetchone()
        
        if row:
            return dict(row)
        
        # Crear nuevo perfil
        db.execute(
            """INSERT INTO horeca_profiles 
               (whatsapp_number, business_name, business_type, created_at) 
               VALUES (?, ?, ?, ?)""",
            (whatsapp_number, business_name, business_type, datetime.now())
        )
        db.commit()
        
        # Retornar el perfil creado
        row = db.execute(
            "SELECT * FROM horeca_profiles WHERE whatsapp_number = ?",
            (whatsapp_number,)
        ).fetchone()
        
        return dict(row)
        
    finally:
        db.close()


def seed_estacion90_profile(whatsapp_number: str) -> Dict:
    """Crea o actualiza el perfil HORECA piloto para Estación 90 (Surco)."""
    profile = get_or_create_profile(whatsapp_number, ESTACION90_BUSINESS_NAME, "estacion90")
    update_profile_field(whatsapp_number, "business_name", ESTACION90_BUSINESS_NAME)
    update_profile_field(whatsapp_number, "business_type", "estacion90")
    update_profile_field(whatsapp_number, "currency", "PEN")
    update_profile_field(whatsapp_number, "last_search_category", "insumos")
    return get_or_create_profile(whatsapp_number)


def is_estacion90_profile(profile: Dict) -> bool:
    """True si el perfil corresponde al piloto Estación 90."""
    name = (profile.get("business_name") or "").strip().lower()
    btype = (profile.get("business_type") or "").strip().lower()
    return "estación 90" in name or "estacion 90" in name or btype == "estacion90"


def update_profile_field(whatsapp_number: str, field: str, value: str) -> bool:
    """Actualiza un campo específico del perfil."""
    db = get_db()
    try:
        # Validar campo permitido
        allowed_fields = ['business_name', 'business_type', 'last_search_category', 'currency']
        if field not in allowed_fields:
            print(f"Error: Field '{field}' not allowed for update")
            return False
        
        db.execute(
            f"UPDATE horeca_profiles SET {field} = ? WHERE whatsapp_number = ?",
            (value, whatsapp_number)
        )
        db.commit()
        return True
    except Exception as e:
        print(f"Error updating profile field: {e}")
        return False
    finally:
        db.close()


def update_profile_search(whatsapp_number: str, search_query: str, savings: float) -> bool:
    """Actualiza el perfil después de una búsqueda."""
    db = get_db()
    try:
        # Incrementar contador de búsquedas
        db.execute(
            """UPDATE horeca_profiles 
               SET search_count = search_count + 1,
                   total_savings = total_savings + ?,
                   last_search_category = ?
               WHERE whatsapp_number = ?""",
            (savings, _extract_category(search_query), whatsapp_number)
        )
        db.commit()
        return True
    except Exception as e:
        print(f"Error updating profile search: {e}")
        return False
    finally:
        db.close()


def check_search_cooldown(whatsapp_number: str, search_query: str) -> bool:
    """Verifica si el usuario puede hacer esta búsqueda (cooldown)."""
    db = get_db()
    try:
        # Buscar búsquedas recientes del mismo producto
        cooldown_threshold = datetime.now() - timedelta(hours=HORECA_COOLDOWN_HOURS)
        
        row = db.execute(
            """SELECT COUNT(*) as count FROM horeca_search_history 
               WHERE whatsapp_number = ? 
               AND search_query = ? 
               AND timestamp > ?""",
            (whatsapp_number, search_query, cooldown_threshold)
        ).fetchone()
        
        return row['count'] == 0  # True si no hay búsquedas recientes
        
    except Exception as e:
        print(f"Error checking cooldown: {e}")
        return True  # En caso de error, permitir la búsqueda
    finally:
        db.close()


def check_daily_limit(whatsapp_number: str) -> tuple[bool, int]:
    """Verifica si el usuario alcanzó el límite diario de búsquedas.
    
    Returns:
        (can_search: bool, current_count: int)
    """
    db = get_db()
    try:
        # Obtener perfil actual
        profile = get_or_create_profile(whatsapp_number)
        current_count = profile.get('search_count', 0)
        
        can_search = current_count < HORECA_FREE_SEARCHES_DAILY
        return can_search, current_count
        
    except Exception as e:
        print(f"Error checking daily limit: {e}")
        return True, 0  # En caso de error, permitir
    finally:
        db.close()


def record_search_history(whatsapp_number: str, search_query: str, category: str, 
                         result_count: int, best_price: float, avg_price: float, 
                         savings: float) -> bool:
    """Registra una búsqueda en el historial."""
    db = get_db()
    try:
        db.execute(
            """INSERT INTO horeca_search_history 
               (whatsapp_number, search_query, category, result_count, best_price, avg_price, savings)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (whatsapp_number, search_query, category, result_count, best_price, avg_price, savings)
        )
        db.commit()
        return True
    except Exception as e:
        print(f"Error recording search history: {e}")
        return False
    finally:
        db.close()


def calculate_savings(search_query: str, answer: str) -> float:
    """Calcula el ahorro basado en la respuesta del LLM.
    
    Busca patrones de precios en la respuesta y calcula la diferencia
    entre el precio promedio y el mejor precio.
    """
    try:
        # Extraer precios de la respuesta (patrón: "S/ X.XX" o "S/ X")
        prices = re.findall(r'S/\s*([\d.]+)', answer)
        
        if len(prices) >= 2:
            prices_float = [float(p) for p in prices]
            best_price = min(prices_float)
            avg_price = sum(prices_float) / len(prices_float)
            savings = avg_price - best_price
            return max(0, savings)  # No ahorros negativos
        
        return 0.0
    except Exception as e:
        print(f"Error calculating savings: {e}")
        return 0.0


def get_user_savings_summary(whatsapp_number: str) -> Dict:
    """Obtiene un resumen de ahorros del usuario."""
    db = get_db()
    try:
        profile = get_or_create_profile(whatsapp_number)
        
        # Obtener historial de búsquedas con ahorros
        history = db.execute(
            """SELECT category, COUNT(*) as searches, SUM(savings) as total_savings
               FROM horeca_search_history 
               WHERE whatsapp_number = ? AND savings > 0
               GROUP BY category
               ORDER BY total_savings DESC""",
            (whatsapp_number,)
        ).fetchall()
        
        return {
            'total_savings': profile.get('total_savings', 0.0),
            'total_searches': profile.get('search_count', 0),
            'by_category': [dict(row) for row in history]
        }
    except Exception as e:
        print(f"Error getting savings summary: {e}")
        return {'total_savings': 0.0, 'total_searches': 0, 'by_category': []}
    finally:
        db.close()


def _extract_category(search_query: str) -> str:
    """Extrae la categoría de una búsqueda (simple heurística)."""
    query_lower = search_query.lower()
    
    category_keywords = {
        'aceites': ['aceite', 'grasa', 'oliva', 'girasol', 'vegetal'],
        'limpieza': ['detergente', 'cloro', 'limpieza', 'desinfectante', 'jabón'],
        'papel': ['papel', 'higiénico', 'servilleta', 'toalla'],
        'bebidas': ['refresco', 'gaseosa', 'cerveza', 'agua', 'jugo'],
        'electrodomesticos': ['electrodoméstico', 'batidora', 'licuadora', 'procesador'],
        'insumos': ['insumo', 'suministro', 'material']
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            return category
    
    return 'general'


def get_profile_by_type(business_type: str) -> list[Dict]:
    """Obtiene todos los perfiles de un tipo de negocio específico."""
    db = get_db()
    try:
        rows = db.execute(
            "SELECT * FROM horeca_profiles WHERE business_type = ? ORDER BY created_at DESC",
            (business_type,)
        ).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting profiles by type: {e}")
        return []
    finally:
        db.close()


def delete_profile(whatsapp_number: str) -> bool:
    """Elimina un perfil HORECA (para testing o cleanup)."""
    db = get_db()
    try:
        # Eliminar registros relacionados primero
        db.execute("DELETE FROM horeca_price_alerts WHERE whatsapp_number = ?", (whatsapp_number,))
        db.execute("DELETE FROM horeca_search_templates WHERE whatsapp_number = ?", (whatsapp_number,))
        db.execute("DELETE FROM horeca_search_history WHERE whatsapp_number = ?", (whatsapp_number,))
        
        # Eliminar perfil
        db.execute("DELETE FROM horeca_profiles WHERE whatsapp_number = ?", (whatsapp_number,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error deleting profile: {e}")
        return False
    finally:
        db.close()