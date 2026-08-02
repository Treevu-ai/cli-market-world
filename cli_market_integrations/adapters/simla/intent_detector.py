"""Intent detector — verbatim from simla-cli-market-prototype (no shared dep needed)."""
import re
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PriceIntentType(Enum):
    SEARCH   = "search"
    COMPARE  = "compare"
    OPTIMIZE = "optimize"
    HISTORY  = "history"
    ALERT    = "alert"
    NONE     = "none"


@dataclass
class PriceIntent:
    product: str
    intent_type: PriceIntentType
    confidence: float
    context: str = "general"
    products_list: List[str] = field(default_factory=list)
    threshold: Optional[float] = None


class IntentDetector:
    PRICE_KEYWORDS    = ["precio","cuánto cuesta","cuanto cuesta","cuesta","costo","vale","tarifa","cuanto vale","cuánto vale","cuanto esta","cuánto está","costa","valor"]
    COMPARE_KEYWORDS  = ["comparar","dónde está más barato","mejor precio","dónde conviene","qué tienda","dónde comprar","donde esta mas barato","mejor opción"]
    OPTIMIZE_KEYWORDS = ["optimizar","canasta","lista de compras","compras","qué comprar","lista","necesito","quiero comprar"]
    HISTORY_KEYWORDS  = ["historial","antes costaba","antes valía","subió","bajó","cambio de precio","evolución"]
    ALERT_KEYWORDS    = ["avísame","alerta","notifícame","cuando baje","cuando suba","quiero saber cuando","aviso"]

    def __init__(self):
        def _pat(kws): return re.compile(r'\b(' + '|'.join(re.escape(k) for k in kws) + r')\b', re.IGNORECASE)
        self.price_pat    = _pat(self.PRICE_KEYWORDS)
        self.compare_pat  = _pat(self.COMPARE_KEYWORDS)
        self.optimize_pat = _pat(self.OPTIMIZE_KEYWORDS)
        self.history_pat  = _pat(self.HISTORY_KEYWORDS)
        self.alert_pat    = _pat(self.ALERT_KEYWORDS)

    def detect_intent(self, message: str) -> Optional[PriceIntent]:
        msg = message.lower().strip()
        itype = self._type(msg)
        if itype == PriceIntentType.NONE:
            return None
        if itype == PriceIntentType.OPTIMIZE:
            prods = self._products_list(msg)
            return PriceIntent(product=", ".join(prods) if prods else "varios", intent_type=itype, confidence=0.8 if prods else 0.5, products_list=prods)
        return PriceIntent(product=self._product_name(msg), intent_type=itype, confidence=self._confidence(msg, itype), threshold=self._threshold(msg) if itype == PriceIntentType.ALERT else None)

    def _type(self, msg: str) -> PriceIntentType:
        if self.optimize_pat.search(msg): return PriceIntentType.OPTIMIZE
        if self.compare_pat.search(msg):  return PriceIntentType.COMPARE
        if self.alert_pat.search(msg):    return PriceIntentType.ALERT
        if self.history_pat.search(msg):  return PriceIntentType.HISTORY
        if self.price_pat.search(msg):    return PriceIntentType.SEARCH
        return PriceIntentType.NONE

    def _product_name(self, msg: str) -> str:
        clean = msg
        for kw in self.PRICE_KEYWORDS + self.COMPARE_KEYWORDS + self.HISTORY_KEYWORDS + self.ALERT_KEYWORDS:
            clean = re.sub(re.escape(kw), '', clean, flags=re.IGNORECASE)
        for w in ["el","la","los","las","un","una","de","en","por","para","con","sin","y","o","pero","que","cual","cuanto","cuál","donde","dónde","cuando","cuándo","como","cómo","está","esta","son","es","están"]:
            clean = re.sub(r'\b' + re.escape(w) + r'\b', '', clean, flags=re.IGNORECASE)
        words = re.findall(r'\b[a-záéíóúñ]{3,}\b', clean)
        return " ".join(words[:3]).strip() if words else "producto"

    def _products_list(self, msg: str) -> List[str]:
        text = msg
        for pat in [r"^(necesito|quiero|quisiera|busco|dame|arme|arma)\s+(comprar\s+)?", r"^(lista\s+de\s+compras?|canasta|optimizar|compras?)\s*[:\-]?\s*", r"\bpara\s+la\s+canasta\b", r"\bpara\s+optimizar\b"]:
            text = re.sub(pat, " ", text, flags=re.IGNORECASE)
        parts = re.split(r"\s*,\s*|\s+y\s+|\s+e\s+", text)
        stop = {"el","la","los","las","un","una","de","en","por","para","con","sin","que","del","al","mi","tu","su","me","te","necesito","quiero","comprar","lista","canasta","optimizar","productos","varios","items","item"}
        products: List[str] = []
        for part in parts:
            part = part.strip(" .;:¡!¿?")
            tokens = [t for t in re.findall(r"[a-záéíóúñ0-9]{2,}", part, flags=re.IGNORECASE) if t.lower() not in stop]
            if not tokens: continue
            name = " ".join(tokens[:4]).strip()
            if len(name) >= 3 and name not in products: products.append(name)
        if len(products) < 2:
            tokens = [t for t in re.findall(r"[a-záéíóúñ0-9]{3,}", text, flags=re.IGNORECASE) if t.lower() not in stop]
            products = list(dict.fromkeys(tokens))[:10]
        return products[:10]

    def _threshold(self, msg: str) -> Optional[float]:
        m = re.search(r'[Ss]/?\s*[\d.]+|\d+[\s.]*soles?', msg)
        if m:
            n = re.search(r'[\d.]+', m.group())
            if n:
                try: return float(n.group())
                except ValueError: pass
        return None

    def _confidence(self, msg: str, itype: PriceIntentType) -> float:
        pat_map = {PriceIntentType.SEARCH: self.price_pat, PriceIntentType.COMPARE: self.compare_pat, PriceIntentType.HISTORY: self.history_pat, PriceIntentType.ALERT: self.alert_pat}
        base = 0.7 + len((pat_map.get(itype) or self.price_pat).findall(msg)) * 0.1
        if 10 <= len(msg) <= 100: base += 0.1
        return min(base, 1.0)


intent_detector = IntentDetector()
