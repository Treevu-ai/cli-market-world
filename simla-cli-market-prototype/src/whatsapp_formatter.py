"""
WhatsApp Response Formatter
Formatea respuestas de CLI Market para mensajes de WhatsApp
"""
from typing import Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppFormatter:
    """Formateador de respuestas para WhatsApp"""
    
    def __init__(self):
        """Inicializar formateador"""
        self.emojis = {
            "search": "🔍",
            "compare": "📊",
            "optimize": "🛒",
            "history": "📈",
            "alert": "🔔",
            "error": "❌",
            "success": "✅",
            "info": "ℹ️",
            "price": "💰",
            "store": "🏪",
            "savings": "💵",
            "warning": "⚠️"
        }
    
    def format_search_result(self, result: Dict) -> str:
        """
        Formatear resultado de búsqueda para WhatsApp
        
        Args:
            result: Resultado de búsqueda de CLI Market
            
        Returns:
            String formateado para WhatsApp
        """
        if result.get("error"):
            return self.format_api_error(result["error"], action="buscar ese producto")

        products = result.get("products", [])
        if not products:
            return f"{self.emojis['error']} No encontré ese producto en los retailers peruanos."
        
        # Tomar el mejor resultado
        top_product = products[0]
        
        response = f"{self.emojis['search']} *{self._format_bold(top_product.get('name', 'Producto'))}*\n\n"
        response += f"{self.emojis['price']} Mejor precio: S/ {self._format_price(top_product.get('price', 0))}\n"
        response += f"{self.emojis['store']} En: {self._format_bold(top_product.get('store', 'Tienda'))}\n"
        
        if top_product.get('last_updated'):
            response += f"📅 Actualizado: {self._format_date(top_product['last_updated'])}\n"
        
        # Agregar opciones adicionales si hay más resultados
        if len(products) > 1:
            response += f"\n_{len(products) - 1} opciones más disponibles_\n"
            response += "¿Quieres que compare con otras tiendas?"
        
        return response
    
    def format_compare_result(self, result: Dict) -> str:
        """
        Formatear resultado de comparación para WhatsApp
        
        Args:
            result: Resultado de comparación de CLI Market
            
        Returns:
            String formateado para WhatsApp
        """
        if result.get("error"):
            return self.format_api_error(result["error"], action="comparar precios")

        comparisons = result.get("comparisons", [])
        if not comparisons:
            return f"{self.emojis['error']} No encontré precios para comparar."
        
        response = f"{self.emojis['compare']} *Comparación de precios:*\n\n"
        
        # Mostrar top 5 retailers
        for i, comp in enumerate(comparisons[:5], 1):
            response += f"{i}. {self.emojis['store']} {comp.get('store', 'Tienda')}: "
            response += f"S/ {self._format_price(comp.get('price', 0))}\n"
        
        # Mejor opción
        if result.get("best_price"):
            best = result["best_price"]
            response += f"\n{self.emojis['success']} *Mejor opción:* {best.get('store', 'Tienda')}\n"
            response += f"{self.emojis['price']} S/ {self._format_price(best.get('price', 0))}\n"
            
            # Calcular ahorro vs. el más caro
            if len(comparisons) > 1:
                most_expensive = max(comparisons, key=lambda x: x.get('price', 0))
                savings = most_expensive.get('price', 0) - best.get('price', 0)
                if savings > 0:
                    response += f"{self.emojis['savings']} Ahorro: S/ {self._format_price(savings)}\n"
        
        return response
    
    def format_optimize_result(self, result: Dict) -> str:
        """
        Formatear resultado de optimización para WhatsApp
        
        Args:
            result: Resultado de optimización de CLI Market
            
        Returns:
            String formateado para WhatsApp
        """
        if result.get("error"):
            return self.format_api_error(result["error"], action="optimizar tu canasta")

        recommendations = result.get("recommendations", [])
        if not recommendations:
            return f"{self.emojis['error']} No pude optimizar tu canasta."
        
        response = f"{self.emojis['optimize']} *Optimización de canasta:*\n\n"
        
        total_savings = 0
        
        for rec in recommendations:
            product_name = rec.get('product', 'Producto')
            optimized_price = rec.get('optimized_price', 0)
            rec.get('original_price', 0)
            savings = rec.get('savings', 0)
            store = rec.get('store', 'Tienda')
            
            response += f"• {self._format_bold(product_name)}\n"
            response += f"  {self.emojis['price']} S/ {self._format_price(optimized_price)} en {store}\n"
            
            if savings > 0:
                response += f"  {self.emojis['savings']} Ahorro: S/ {self._format_price(savings)}\n"
                total_savings += savings
        
        # Resumen de ahorro total
        if result.get("total_savings"):
            total_savings = result["total_savings"]
            response += f"\n{self.emojis['savings']} *Ahorro total: S/ {self._format_price(total_savings)}*\n"
        
        # Recomendación de tienda
        if result.get("recommended_store"):
            response += f"\n{self.emojis['store']} *Mejor opción: {result['recommended_store']}*\n"
        
        return response
    
    def format_history_result(self, result: Dict) -> str:
        """
        Formatear resultado de historial para WhatsApp
        
        Args:
            result: Resultado de historial de CLI Market
            
        Returns:
            String formateado para WhatsApp
        """
        if result.get("error"):
            return self.format_api_error(result["error"], action="obtener el historial de precios")

        history = result.get("history", [])
        if not history:
            return f"{self.emojis['error']} No hay historial disponible para este producto."
        
        response = f"{self.emojis['history']} *Historial de precios:*\n\n"
        
        # Mostrar últimos 5 registros
        for i, entry in enumerate(history[:5], 1):
            date = entry.get('date', 'Fecha desconocida')
            price = entry.get('price', 0)
            store = entry.get('store', 'Tienda')
            
            response += f"{i}. {self._format_date(date)}: S/ {self._format_price(price)} ({store})\n"
        
        # Tendencia
        if len(history) >= 2:
            first_price = history[-1].get('price', 0)
            last_price = history[0].get('price', 0)
            
            if last_price > first_price:
                trend = "📈 Subió"
                change = last_price - first_price
            elif last_price < first_price:
                trend = "📉 Bajó"
                change = first_price - last_price
            else:
                trend = "➡️ Estable"
                change = 0
            
            response += f"\n{trend}: S/ {self._format_price(change)} en el período"
        
        return response
    
    def format_alert_confirmation(self, product: str, threshold: float) -> str:
        """
        Formatear confirmación de alerta configurada
        
        Args:
            product: Nombre del producto
            threshold: Umbral de precio
            
        Returns:
            String formateado para WhatsApp
        """
        response = f"{self.emojis['alert']} *Alerta configurada:*\n\n"
        response += f"Producto: {self._format_bold(product)}\n"
        response += f"Te avisaré cuando el precio baje de S/ {self._format_price(threshold)}\n\n"
        response += f"{self.emojis['info']} Te notificaré por este chat cuando haya cambios."
        
        return response
    
    def format_error(self, message: str) -> str:
        """Formatear mensaje de error genérico para WhatsApp."""
        return f"{self.emojis['error']} {message}"

    def format_api_error(self, error_code: str, action: str = "completar la consulta") -> str:
        """Mensajes claros según código de error de CLI Market (429, 403, etc.)."""
        code = (error_code or "").lower()
        if "429" in code or "too many" in code or "rate" in code:
            return (
                f"{self.emojis['warning']} Demasiadas consultas en poco tiempo. "
                "Esperá un minuto e intentá de nuevo."
            )
        if "403" in code or "401" in code:
            return (
                f"{self.emojis['error']} No tengo permiso para {action} con la cuenta configurada. "
                "Revisá el plan/API key (canasta exige Pro+)."
            )
        if "timeout" in code:
            return (
                f"{self.emojis['warning']} La consulta tardó demasiado. "
                "Intentá de nuevo en unos segundos."
            )
        return self.format_error(f"No pude {action}. Intentá con otro nombre o más tarde.")
    
    def _format_bold(self, text: str) -> str:
        """Formatear texto en negrita para WhatsApp"""
        # WhatsApp usa * para negrita
        return f"*{text}*"
    
    def _format_price(self, price: float) -> str:
        """Formatear precio para mostrar"""
        try:
            return f"{price:,.2f}"
        except (ValueError, TypeError):
            return str(price)
    
    def _format_date(self, date_str: str) -> str:
        """Formatear fecha para mostrar"""
        try:
            # Intentar parsear diferentes formatos de fecha
            for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%d/%m/%Y")
                except ValueError:
                    continue
            return date_str  # Si no se puede parsear, devolver original
        except (ValueError, TypeError):
            return date_str

# Singleton para usar en toda la aplicación
whatsapp_formatter = WhatsAppFormatter()