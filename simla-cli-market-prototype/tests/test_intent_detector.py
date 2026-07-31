"""Unit tests for WhatsApp price intent detection (no network)."""
from src.intent_detector import IntentDetector, PriceIntentType


def test_search_intent():
    det = IntentDetector()
    intent = det.detect_intent("¿Cuánto cuesta la leche evaporada Gloria?")
    assert intent is not None
    assert intent.intent_type == PriceIntentType.SEARCH
    assert intent.confidence > 0.5
    assert "leche" in intent.product or "gloria" in intent.product


def test_compare_intent():
    det = IntentDetector()
    intent = det.detect_intent("dónde está más barato el arroz")
    assert intent is not None
    assert intent.intent_type == PriceIntentType.COMPARE


def test_no_intent():
    det = IntentDetector()
    intent = det.detect_intent("hola buenos días")
    assert intent is None


def test_optimize_list():
    det = IntentDetector()
    intent = det.detect_intent("necesito leche, arroz y aceite para la canasta")
    assert intent is not None
    assert intent.intent_type == PriceIntentType.OPTIMIZE
    assert len(intent.products_list) >= 2
