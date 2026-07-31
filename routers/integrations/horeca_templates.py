"""Gestión de templates de búsqueda recurrente para HORECA."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from market_core import get_db

# Configuración de frecuencias permitidas
ALLOWED_FREQUENCIES = ['daily', 'weekly', 'monthly']


def get_user_templates(whatsapp_number: str) -> List[Dict]:
    """Obtiene todos los templates de un usuario."""
    db = get_db()
    try:
        rows = db.execute(
            """SELECT * FROM horeca_search_templates 
               WHERE whatsapp_number = ? 
               ORDER BY created_at DESC""",
            (whatsapp_number,)
        ).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting user templates: {e}")
        return []
    finally:
        db.close()


def create_template(whatsapp_number: str, template_name: str, search_query: str, 
                   category: str, frequency: str = 'weekly') -> bool:
    """Crea un nuevo template de búsqueda recurrente."""
    # Validar frecuencia
    if frequency not in ALLOWED_FREQUENCIES:
        print(f"Error: Invalid frequency '{frequency}'. Must be one of: {ALLOWED_FREQUENCIES}")
        return False
    
    db = get_db()
    try:
        db.execute(
            """INSERT INTO horeca_search_templates 
               (whatsapp_number, template_name, search_query, category, frequency, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (whatsapp_number, template_name, search_query, category, frequency, datetime.now())
        )
        db.commit()
        return True
    except Exception as e:
        print(f"Error creating template: {e}")
        return False
    finally:
        db.close()


def update_template_savings(template_id: int, additional_savings: float) -> bool:
    """Actualiza el ahorro acumulado de un template."""
    db = get_db()
    try:
        db.execute(
            """UPDATE horeca_search_templates 
               SET savings_accumulated = savings_accumulated + ?,
                   last_used = ?
               WHERE id = ?""",
            (additional_savings, datetime.now(), template_id)
        )
        db.commit()
        return True
    except Exception as e:
        print(f"Error updating template savings: {e}")
        return False
    finally:
        db.close()


def delete_template(template_id: int, whatsapp_number: str) -> bool:
    """Elimina un template (verifica ownership)."""
    db = get_db()
    try:
        # Verificar que el template pertenezca al usuario
        template = db.execute(
            "SELECT * FROM horeca_search_templates WHERE id = ? AND whatsapp_number = ?",
            (template_id, whatsapp_number)
        ).fetchone()
        
        if not template:
            print(f"Error: Template {template_id} not found or doesn't belong to user")
            return False
        
        db.execute("DELETE FROM horeca_search_templates WHERE id = ?", (template_id,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error deleting template: {e}")
        return False
    finally:
        db.close()


def get_template_by_id(template_id: int) -> Optional[Dict]:
    """Obtiene un template específico por ID."""
    db = get_db()
    try:
        row = db.execute(
            "SELECT * FROM horeca_search_templates WHERE id = ?",
            (template_id,)
        ).fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error getting template by id: {e}")
        return None
    finally:
        db.close()


def get_template_summary(whatsapp_number: str) -> str:
    """Genera un resumen de templates para mostrar al usuario."""
    templates = get_user_templates(whatsapp_number)
    
    if not templates:
        return "📋 No tenés búsquedas guardadas aún.\n\nPara crear una, escribí 'guardar [nombre]' después de una búsqueda."
    
    summary = "📋 *Tus búsquedas guardadas:*\n\n"
    for i, template in enumerate(templates, 1):
        summary += f"{i}. *{template['template_name']}*\n"
        summary += f"   📝 {template['search_query']}\n"
        summary += f"   🔄 Frecuencia: {template['frequency']}\n"
        summary += f"   💰 Ahorro acumulado: S/ {template['savings_accumulated']:.2f}\n"
        if template['last_used']:
            summary += f"   📅 Último uso: {template['last_used']}\n"
        summary += "\n"
    
    return summary


def get_templates_due_for_execution() -> List[Dict]:
    """Obtiene templates que deben ejecutarse según su frecuencia.
    
    Para MVP simplificado, retorna todos los templates marcados como 'weekly'
    que no se han ejecutado en los últimos 7 días.
    """
    db = get_db()
    try:
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        rows = db.execute(
            """SELECT * FROM horeca_search_templates 
               WHERE frequency = 'weekly'
               AND (last_used IS NULL OR last_used < ?)
               ORDER BY last_used ASC NULLS FIRST""",
            (seven_days_ago,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting templates due for execution: {e}")
        return []
    finally:
        db.close()


def create_sample_templates(whatsapp_number: str, business_type: str) -> bool:
    """Crea templates de ejemplo basados en el tipo de negocio."""
    
    sample_templates = {
        'restaurant': [
            {
                'name': 'Pedido semanal restaurante',
                'query': 'aceite vegetal 20L, detergente industrial 5L, papel higiénico',
                'category': 'insumos',
                'frequency': 'weekly'
            },
            {
                'name': 'Bebidas restaurante',
                'query': 'refrescos 2L, cervezas, aguas',
                'category': 'bebidas',
                'frequency': 'weekly'
            }
        ],
        'hotel': [
            {
                'name': 'Amenidades hotel',
                'query': 'jabón, shampoo, acondicionador',
                'category': 'limpieza',
                'frequency': 'weekly'
            },
            {
                'name': 'Limpieza hotel',
                'query': 'detergente, cloro, desinfectante',
                'category': 'limpieza',
                'frequency': 'weekly'
            }
        ],
        'catering': [
            {
                'name': 'Insumos food service',
                'query': 'aceite, descartables, servilletas',
                'category': 'insumos',
                'frequency': 'weekly'
            }
        ],
        'cafeteria': [
            {
                'name': 'Insumos cafetería',
                'query': 'café, azúcar, leche, vasos descartables',
                'category': 'insumos',
                'frequency': 'weekly'
            }
        ]
    }
    
    templates = sample_templates.get(business_type, [])
    
    for template in templates:
        create_template(
            whatsapp_number,
            template['name'],
            template['query'],
            template['category'],
            template['frequency']
        )
    
    return len(templates) > 0


def get_template_usage_stats(whatsapp_number: str) -> Dict:
    """Obtiene estadísticas de uso de templates."""
    db = get_db()
    try:
        templates = get_user_templates(whatsapp_number)
        
        if not templates:
            return {
                'total_templates': 0,
                'total_savings': 0.0,
                'most_used_category': None,
                'active_templates': 0
            }
        
        total_savings = sum(t['savings_accumulated'] for t in templates)
        active_templates = len([t for t in templates if t['last_used']])
        
        # Encontrar categoría más usada
        category_counts = {}
        for t in templates:
            cat = t['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        most_used_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        
        return {
            'total_templates': len(templates),
            'total_savings': total_savings,
            'most_used_category': most_used_category,
            'active_templates': active_templates
        }
    except Exception as e:
        print(f"Error getting template usage stats: {e}")
        return {
            'total_templates': 0,
            'total_savings': 0.0,
            'most_used_category': None,
            'active_templates': 0
        }
    finally:
        db.close()


