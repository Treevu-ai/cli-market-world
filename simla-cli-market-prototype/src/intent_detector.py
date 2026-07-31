"""
Intent Detector para WhatsApp
Detecta intención de consulta de precios en mensajes de WhatsApp
"""
import re
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PriceIntentType(Enum):
    """Tipos de intención de precios"""
    SEARCH = "search"           # Búsqueda simple de precio
    COMPARE = "compare"        # Comparación entre tiendas
    OPTIMIZE = "optimize"      # Optimización de canasta
    HISTORY = "history"        # Historial de precios
    ALERT = "alert"            # Configurar alerta de precio
    NONE = "none"              # Sin intención de precios

@dataclass
class PriceIntent:
    """Intención de consulta de precios detectada"""
    product: str
    intent_type: PriceIntentType
    confidence: float  # 0.0 a 1.0
    context: str = "general"
    products_list: List[str] | None = None  # Para optimización de canasta
    threshold: float | None = None  # Para alertas

    def __post_init__(self):
        if self.products_list is None:
            self.products_list = []

class IntentDetector:
    """Detector de intención de precios en mensajes de WhatsApp"""
    
    # Patrones de búsqueda de precios
    PRICE_KEYWORDS = [
        "precio", "cuánto cuesta", "cuanto cuesta", "cuesta", "costo",
        "vale", "tarifa", "cuanto vale", "cuánto vale", "cuanto esta",
        "cuánto está", "costa", "valor",
    ]
    
    # Patrones de comparación
    COMPARE_KEYWORDS = [
        "comparar", "dónde está más barato", "mejor precio",
        "dónde conviene", "qué tienda", "dónde comprar",
        "donde esta mas barato", "mejor opción"
    ]
    
    # Patrones de optimización
    OPTIMIZE_KEYWORDS = [
        "optimizar", "canasta", "lista de compras", "compras",
        "qué comprar", "lista", "necesito", "quiero comprar"
    ]
    
    # Patrones de historial
    HISTORY_KEYWORDS = [
        "historial", "antes costaba", "antes valía", "subió",
        "bajó", "cambio de precio", "evolución"
    ]
    
    # Patrones de alertas
    ALERT_KEYWORDS = [
        "avísame", "alerta", "notifícame", "cuando baje",
        "cuando suba", "quiero saber cuando", "aviso"
    ]
    
    def __init__(self):
        """Inicializar detector de intención"""
        # Compilar regex patterns para mejor performance
        self.price_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in self.PRICE_KEYWORDS) + r')\b',
            re.IGNORECASE
        )
        self.compare_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in self.COMPARE_KEYWORDS) + r')\b',
            re.IGNORECASE
        )
        self.optimize_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in self.OPTIMIZE_KEYWORDS) + r')\b',
            re.IGNORECASE
        )
        self.history_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in self.HISTORY_KEYWORDS) + r')\b',
            re.IGNORECASE
        )
        self.alert_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in self.ALERT_KEYWORDS) + r')\b',
            re.IGNORECASE
        )
    
    def detect_intent(self, message: str) -> Optional[PriceIntent]:
        """
        Detectar intención de consulta de precios en un mensaje
        
        Args:
            message: Mensaje de WhatsApp
            
        Returns:
            PriceIntent si se detecta intención, None en caso contrario
        """
        message_lower = message.lower().strip()
        
        # Detectar tipo de intención
        intent_type = self._detect_intent_type(message_lower)
        
        if intent_type == PriceIntentType.NONE:
            return None
        
        # Extraer producto(s) del mensaje
        if intent_type == PriceIntentType.OPTIMIZE:
            products = self._extract_products_list(message_lower)
            confidence = 0.8 if products else 0.5
            
            return PriceIntent(
                product=", ".join(products) if products else "varios",
                intent_type=intent_type,
                confidence=confidence,
                products_list=products
            )
        else:
            product = self._extract_product_name(message_lower)
            confidence = self._calculate_confidence(message_lower, intent_type)
            
            # Para alertas, extraer threshold si existe
            threshold = None
            if intent_type == PriceIntentType.ALERT:
                threshold = self._extract_threshold(message_lower)
            
            return PriceIntent(
                product=product,
                intent_type=intent_type,
                confidence=confidence,
                threshold=threshold
            )
    
    def _detect_intent_type(self, message: str) -> PriceIntentType:
        """Detectar el tipo de intención basado en keywords"""
        
        # Prioridad: OPTIMIZE > COMPARE > ALERT > HISTORY > SEARCH
        
        if self.optimize_pattern.search(message):
            return PriceIntentType.OPTIMIZE
        
        if self.compare_pattern.search(message):
            return PriceIntentType.COMPARE
        
        if self.alert_pattern.search(message):
            return PriceIntentType.ALERT
        
        if self.history_pattern.search(message):
            return PriceIntentType.HISTORY
        
        if self.price_pattern.search(message):
            return PriceIntentType.SEARCH
        
        return PriceIntentType.NONE
    
    def _extract_product_name(self, message: str) -> str:
        """
        Extraer nombre del producto del mensaje
        Versión simplificada - en producción usar NLP más sofisticado
        """
        # Eliminar keywords de intención
        message_clean = message
        
        for kw in self.PRICE_KEYWORDS + self.COMPARE_KEYWORDS + \
                     self.HISTORY_KEYWORDS + self.ALERT_KEYWORDS:
            message_clean = re.sub(re.escape(kw), '', message_clean, flags=re.IGNORECASE)
        
        # Eliminar palabras comunes que no son productos
        stop_words = [
            "el", "la", "los", "las", "un", "una", "de", "en", "por",
            "para", "con", "sin", "y", "o", "pero", "que", "cual",
            "cuanto", "cuál", "donde", "dónde", "cuando", "cuándo",
            "como", "cómo", "está", "esta", "son", "es", "están"
        ]
        
        for word in stop_words:
            message_clean = re.sub(r'\b' + re.escape(word) + r'\b', '', message_clean, flags=re.IGNORECASE)
        
        # Limpiar y extraer palabras restantes
        words = re.findall(r'\b[a-záéíóúñ]{3,}\b', message_clean)
        
        if words:
            # Tomar las primeras 2-3 palabras como nombre de producto
            product_name = " ".join(words[:3])
            return product_name.strip()
        
        return "producto"
    
    def _extract_products_list(self, message: str) -> List[str]:
        """
        Extraer lista de productos del mensaje
        Para optimización de canasta
        """
        # Buscar patrones como: "necesito X, Y, Z" o "quiero comprar X, Y y Z"
        products = []
        
        # Separar por comas, "y", "e"
        separators = r'[,yYeE]+'
        items = re.split(separators, message)
        
        for item in items:
            item = item.strip()
            # Eliminar palabras comunes
            item = re.sub(r'\b(necesito|quiero|comprar|lista|canasta)\b', '', item, flags=re.IGNORECASE)
            item = item.strip()
            
            if len(item) > 2:  # Mínimo 3 caracteres
                products.append(item)
        
        return products[:10]  # Máximo 10 productos
    
    def _extract_threshold(self, message: str) -> Optional[float]:
        """Extraer umbral de precio para alertas"""
        # Buscar patrones como: "cuando baje de S/ 5.00" o "avísame si baja a 4 soles"
        
        # Buscar números con S/ o soles
        price_pattern = re.search(r'[Ss]/?\s*[\d.]+|\d+[\s.]*soles?', message)
        if price_pattern:
            # Extraer número
            number_match = re.search(r'[\d.]+', price_pattern.group())
            if number_match:
                try:
                    return float(number_match.group())
                except ValueError:
                    pass
        
        return None
    
    def _calculate_confidence(self, message: str, intent_type: PriceIntentType) -> float:
        """Calcular confianza de la detección (0.0 a 1.0)"""
        
        base_confidence = 0.7
        
        # Aumentar confianza si hay más keywords específicos
        keyword_count = 0
        
        if intent_type == PriceIntentType.SEARCH:
            keyword_count = len(self.price_pattern.findall(message))
        elif intent_type == PriceIntentType.COMPARE:
            keyword_count = len(self.compare_pattern.findall(message))
        elif intent_type == PriceIntentType.HISTORY:
            keyword_count = len(self.history_pattern.findall(message))
        elif intent_type == PriceIntentType.ALERT:
            keyword_count = len(self.alert_pattern.findall(message))
        
        confidence = base_confidence + (keyword_count * 0.1)
        
        # Aumentar confianza si el mensaje tiene longitud razonable
        if 10 <= len(message) <= 100:
            confidence += 0.1
        
        return min(confidence, 1.0)

# Singleton para usar en toda la aplicación
intent_detector = IntentDetector()