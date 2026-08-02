"""Extensiones HORECA para integración WhatsApp de CLI Market.

Este archivo contiene las extensiones específicas para el piloto HORECA
que se integran con la funcionalidad Twilio existente en whatsapp.py.
"""

import os
from typing import Optional, Dict
import httpx

# Importar módulos HORECA
from .horeca_profiles import (
    get_or_create_profile,
    update_profile_field,
    update_profile_search,
    check_search_cooldown,
    check_daily_limit,
    record_search_history,
    calculate_savings,
    get_user_savings_summary,
    _extract_category,
    seed_estacion90_profile,
    is_estacion90_profile,
    ESTACION90_BUSINESS_NAME,
)
from .horeca_templates import (
    get_template_summary,
    create_sample_templates,
    create_estacion90_templates,
)
from .horeca_menu_cost import estimate_menu_ingredient_cost, format_menu_cost_response
from .horeca_procure_bridge import (
    procure_enabled,
    run_menu_procurement,
    format_procure_whatsapp,
)

# Configuración HORECA
HORECA_ENABLED = os.getenv("HORECA_ENABLED", "false").lower() == "true"
HORECA_FREE_SEARCHES_DAILY = int(os.getenv("HORECA_FREE_SEARCHES_DAILY", "5"))
HORECA_COOLDOWN_HOURS = int(os.getenv("HORECA_COOLDOWN_HOURS", "4"))
HORECA_SAVINGS_NOTIFICATION_THRESHOLD = float(os.getenv("HORECA_SAVINGS_NOTIFICATION_THRESHOLD", "50.0"))
HORECA_ESTACION90_WHATSAPP = os.getenv("HORECA_ESTACION90_WHATSAPP", "").strip()
HORECA_ESTACION90_AUTO_SEED = os.getenv("HORECA_ESTACION90_AUTO_SEED", "true").lower() == "true"

# Funciones helper para mensajes HORECA
def _build_horeca_welcome(profile: Dict) -> str:
    """Mensaje de bienvenida personalizado por tipo de negocio."""
    business_type = profile['business_type']
    business_name = profile['business_name']
    
    type_messages = {
        'restaurant': (
            f"¡Hola {business_name}! 🍽️\n\n"
            "Soy tu asistente de compras CLI Market para restaurantes.\n\n"
            "Puedo ayudarte a:\n"
            "• Encontrar mejores precios en aceites y grasas\n"
            "• Comparar proveedores de limpieza industrial\n"
            "• Optimizar compras recurrentes de papel e insumos\n\n"
            f"Tu primera búsqueda es GRATIS (límite: {HORECA_FREE_SEARCHES_DAILY}/día). "
            "¿Qué insumo necesitas hoy?"
        ),
        'hotel': (
            f"¡Hola {business_name}! 🏨\n\n"
            "Soy tu asistente de compras CLI Market para hoteles.\n\n"
            "Puedo ayudarte a:\n"
            "• Comparar precios de amenidades\n"
            "• Encontrar mejores ofertas en limpieza\n"
            "• Optimizar compras de insumos de restaurant\n\n"
            f"Tu primera búsqueda es GRATIS (límite: {HORECA_FREE_SEARCHES_DAILY}/día). "
            "¿Qué insumo necesitas hoy?"
        ),
        'catering': (
            f"¡Hola {business_name}! 🍱\n\n"
            "Soy tu asistente de compras CLI Market para catering.\n\n"
            "Puedo ayudarte a:\n"
            "• Comparar precios de insumos food service\n"
            "• Encontrar mejores ofertas en descartables\n"
            "• Optimizar compras recurrentes\n\n"
            f"Tu primera búsqueda es GRATIS (límite: {HORECA_FREE_SEARCHES_DAILY}/día). "
            "¿Qué insumo necesitas hoy?"
        ),
        'cafeteria': (
            f"¡Hola {business_name}! ☕\n\n"
            "Soy tu asistente de compras CLI Market para cafeterías.\n\n"
            "Puedo ayudarte a:\n"
            "• Comparar precios de café y granos\n"
            "• Encontrar mejores ofertas en insumos\n"
            "• Optimizar compras recurrentes\n\n"
            f"Tu primera búsqueda es GRATIS (límite: {HORECA_FREE_SEARCHES_DAILY}/día). "
            "¿Qué insumo necesitas hoy?"
        ),
        'estacion90': (
            f"¡Hola {business_name}! 🍽️\n\n"
            "Soy tu asistente CLI Market para *Estación 90* (Surco).\n\n"
            "Puedo ayudarte a:\n"
            "• Optimizar insumos en Wong, Metro y Plazavea\n"
            "• Estimar costo de insumos del *menú del día*\n"
            "• Comparar plantillas de compra semanal\n\n"
            "Comandos: `costo menú`, `cotizar menú`, `cotizar semana`, `mis plantillas`\n\n"
            f"Búsquedas gratis hoy: {HORECA_FREE_SEARCHES_DAILY}"
        )
    }
    
    return type_messages.get(business_type, type_messages['restaurant'])

def _build_cooldown_message(sender: str, search_query: str) -> str:
    """Mensaje cuando el usuario está en cooldown."""
    return (
        f"⏰ Ya buscaste '{search_query}' hace menos de {HORECA_COOLDOWN_HOURS} horas.\n\n"
        f"Para evitar spam, esperá {HORECA_COOLDOWN_HOURS} horas antes de buscar "
        f"el mismo producto nuevamente.\n\n"
        f"Podés buscar otros productos o consultarme por otras categorías."
    )

def _build_limit_message(profile: Dict) -> str:
    """Mensaje cuando el usuario alcanzó el límite diario."""
    return (
        f"📊 Alcanzaste tu límite de {HORECA_FREE_SEARCHES_DAILY} búsquedas gratis hoy.\n\n"
        f"Ahorro acumulado este mes: S/ {profile['total_savings']:.2f}\n\n"
        f"Para continuar usando el servicio:\n"
        f"• Plan Starter: S/99/mes (20 búsquedas)\n"
        f"• Plan Pro: S/499/mes (búsquedas ilimitadas + alertas)\n\n"
        f"¿Te interesa hacer upgrade? Responde 'upgrade' para más info."
    )

def _build_savings_notification(profile: Dict, current_savings: float) -> str:
    """Notificación de ahorro alcanzado."""
    return (
        f"💰 ¡Buenas noticias! alcanzaste un nuevo hito de ahorro.\n\n"
        f"Ahorro total acumulado: S/ {profile['total_savings']:.2f}\n"
        f"Ahorro en esta búsqueda: S/ {current_savings:.2f}\n\n"
        f"Seguí así optimizando tus compras de {profile['business_type']}!"
    )

def _build_progress_message(stage: int, total_stages: int = 3) -> str:
    """Mensaje de progreso durante búsqueda."""
    stages = {
        1: "🔍 Buscando en 60+ retailers...",
        2: "📊 Comparando precios y calculando ahorro...",
        3: "✅ Preparando tu resultado..."
    }
    return stages.get(stage, "⏳ Procesando...")

async def _handle_horeca_onboarding_flow(sender: str, message: str, profile: Dict, send_function) -> None:
    """Maneja el flujo de onboarding interactivo.
    
    Args:
        sender: Número de WhatsApp del usuario
        message: Mensaje recibido
        profile: Perfil actual del usuario
        send_function: Función para enviar mensajes (e.g., _send_twilio_text)
    """
    message_lower = message.lower().strip()
    
    # Paso 1: Pedir nombre del negocio
    if profile['business_name'] == 'Desconocido':
        update_profile_field(sender, 'business_name', message)
        send_function(
            sender,
            f"✓ Nombre registrado: {message}\n\n"
            f"¿Qué tipo de negocio es?\n"
            f"1. Restaurante\n"
            f"2. Hotel\n"
            f"3. Catering\n"
            f"4. Cafetería\n\n"
            f"Respondé con el número (1-4)."
        )
        return
    
    # Paso 2: Registrar tipo de negocio
    if profile['business_type'] == 'pending':
        type_mapping = {
            '1': 'restaurant',
            '2': 'hotel', 
            '3': 'catering',
            '4': 'cafeteria'
        }
        
        if message_lower in type_mapping:
            business_type = type_mapping[message_lower]
            update_profile_field(sender, 'business_type', business_type)
            
            # Completar onboarding
            profile = get_or_create_profile(sender, profile['business_name'], business_type)
            welcome_msg = _build_horeca_welcome(profile)
            
            # Crear templates de ejemplo
            create_sample_templates(sender, business_type)
            
            send_function(sender, welcome_msg)
        else:
            send_function(
                sender,
                "❌ Opción no válida. Por favor respondé con un número del 1 al 4."
            )

async def process_horeca_message(
    incoming_msg: str, 
    sender: str, 
    audio_url: Optional[str],
    send_function,
    market_api_url: str,
    token_function
) -> None:
    """Procesa un mensaje WhatsApp con lógica HORECA.
    
    Esta función extiende la funcionalidad existente de whatsapp.py
    con características específicas para el piloto HORECA.
    
    Args:
        incoming_msg: Mensaje de texto recibido
        sender: Número de WhatsApp del remitente
        audio_url: URL de audio (si existe)
        send_function: Función para enviar mensajes de vuelta
        market_api_url: URL de la API de CLI Market
        token_function: Función para obtener el token de autenticación
    """
    # Si HORECA no está habilitado, usar lógica estándar
    if not HORECA_ENABLED:
        return None  # Indica que use la lógica estándar
    
    # Obtener o crear perfil HORECA
    profile = get_or_create_profile(sender)

    # Auto-seed piloto Estación 90 (número configurado en Fly.io)
    if HORECA_ESTACION90_AUTO_SEED and HORECA_ESTACION90_WHATSAPP and sender == HORECA_ESTACION90_WHATSAPP:
        if not is_estacion90_profile(profile):
            profile = seed_estacion90_profile(sender)
            create_estacion90_templates(sender)
            send_function(sender, _build_horeca_welcome(profile))
            return True
    
    # Flujo de onboarding si el perfil está pendiente
    if profile['business_type'] == 'pending':
        await _handle_horeca_onboarding_flow(sender, incoming_msg, profile, send_function)
        return True  # Indica que se procesó con lógica HORECA
    
    # Comandos específicos HORECA
    message_lower = incoming_msg.lower().strip()
    
    if message_lower in ['mis ahorros', 'ahorros', 'savings']:
        summary = get_user_savings_summary(sender)
        savings_msg = (
            f"📊 *Tu resumen de ahorros:*\n\n"
            f"Ahorro total: S/ {summary['total_savings']:.2f}\n"
            f"Búsquedas realizadas: {summary['total_searches']}\n\n"
        )
        
        if summary['by_category']:
            savings_msg += "*Por categoría:*\n"
            for cat in summary['by_category']:
                savings_msg += f"• {cat['category']}: {cat['searches']} búsquedas, S/ {cat['total_savings']:.2f}\n"
        
        send_function(sender, savings_msg)
        return True
    
    if message_lower in ['mis plantillas', 'plantillas', 'templates']:
        templates_msg = get_template_summary(sender)
        send_function(sender, templates_msg)
        return True

    if message_lower in ('costo menu', 'costo menú', 'menu del dia', 'menú del día', 'costo menú del día',
                         'cotizar menu', 'cotizar menú', 'cotizar menú del día'):
        if is_estacion90_profile(profile) and procure_enabled():
            send_function(sender, "📋 Cotizando insumos del menú del día (Procure + aprobación)...")
            try:
                result = await run_menu_procurement(sender, menu_category_id="menu_dia")
                send_function(sender, format_procure_whatsapp(result))
            except Exception as e:
                print(f"Error procure menu run: {e}")
                send_function(sender, "❌ Error en Procure Copilot. Probá de nuevo.")
            return True

        token = token_function(sender)
        if not token:
            send_function(sender, "❌ Error de configuración. Contactá al administrador.")
            return True
        send_function(sender, "📊 Calculando costo de insumos del menú del día en Wong, Metro y Plazavea...")
        try:
            result = await estimate_menu_ingredient_cost(
                market_api_url=market_api_url,
                token=token,
                category_id="menu_dia",
            )
            send_function(sender, format_menu_cost_response(result))
        except Exception as e:
            print(f"Error estimating menu cost: {e}")
            send_function(sender, "❌ No pude estimar el costo del menú. Probá de nuevo en un ratito.")
        return True

    if message_lower in ('cotizar semana', 'pedido semana', 'insumos semana'):
        if not is_estacion90_profile(profile):
            send_function(sender, "Este comando es del piloto Estación 90.")
            return True
        if not procure_enabled():
            send_function(sender, "❌ Procure Copilot no está configurado en el servidor.")
            return True
        send_function(sender, "📋 Cotizando insumos semanales (Procure)...")
        try:
            result = await run_menu_procurement(sender, preset_id="semana_cocina")
            send_function(sender, format_procure_whatsapp(result))
        except Exception as e:
            print(f"Error procure semana: {e}")
            send_function(sender, "❌ Error en Procure Copilot.")
        return True
    
    if message_lower == 'upgrade':
        upgrade_msg = (
            "💳 *Planes CLI Market HORECA:*\n\n"
            "• *Starter*: S/99/mes\n"
            "  - 20 búsquedas/mes\n"
            "  - Export CSV\n"
            "  - Soporte email\n\n"
            "• *Pro*: S/499/mes\n"
            "  - Búsquedas ilimitadas\n"
            "  - Alertas de precio\n"
            "  - Templates avanzados\n"
            "  - Soporte prioritario\n\n"
            "Para hacer upgrade, contactá a: horeca@cli-market.dev"
        )
        send_function(sender, upgrade_msg)
        return True
    
    # Chequear cooldowns para búsquedas de productos
    if not check_search_cooldown(sender, incoming_msg):
        send_function(sender, _build_cooldown_message(sender, incoming_msg))
        return True
    
    # Chequear límite diario de búsquedas gratis
    can_search, current_count = check_daily_limit(sender)
    if not can_search:
        send_function(sender, _build_limit_message(profile))
        return True
    
    # Enviar mensaje de progreso
    send_function(sender, _build_progress_message(1))
    
    # Procesar búsqueda con lógica estándar (llamar a la API existente)
    token = token_function(sender)
    if not token:
        send_function(sender, "❌ Error de configuración. Contactá al administrador.")
        return True
    
    try:
        send_function(sender, _build_progress_message(2))
        
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                f"{market_api_url}/v1/intel/ask",
                json={"question": incoming_msg},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                answer = response.json().get("answer", "")
                
                # Calcular ahorro
                savings = calculate_savings(incoming_msg, answer)
                
                # Actualizar perfil
                update_profile_search(sender, incoming_msg, savings)
                
                # Registrar en historial
                category = _extract_category(incoming_msg)
                record_search_history(
                    sender, incoming_msg, category, 
                    result_count=0,  # Se completaría con datos reales
                    best_price=0.0,  # Se completaría con datos reales
                    avg_price=0.0,   # Se completaría con datos reales
                    savings=savings
                )
                
                # Construir respuesta con ahorro
                final_answer = answer
                if savings > 0:
                    final_answer += f"\n\n💰 *Ahorro estimado: S/ {savings:.2f}*"
                    # Notificar si alcanzó un hito significativo
                    if savings > HORECA_SAVINGS_NOTIFICATION_THRESHOLD:
                        final_answer += f"\n\n{_build_savings_notification(profile, savings)}"
                
                send_function(sender, _build_progress_message(3))
                send_function(sender, final_answer)
                
                # CTA para crear template si el ahorro es significativo
                if savings > 20:  # S/ 20
                    send_function(
                        sender,
                        "💡 ¿Querés guardar esta búsqueda como recurrente? "
                        "Escribí 'guardar [nombre]' para crear un template."
                    )
                
            else:
                send_function(sender, "❌ Error consultando precios. Probá de nuevo en un ratito.")
                
    except Exception as e:
        print(f"Error en process_horeca_message: {e}")
        send_function(sender, "❌ Error procesando tu solicitud. Probá de nuevo.")
    
    return True  # Indica que se procesó con lógica HORECA