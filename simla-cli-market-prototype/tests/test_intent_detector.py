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
    # No debe quedar basura tipo "sito l" / "para la"
    joined = " ".join(intent.products_list).lower()
    assert "leche" in joined
    assert "arroz" in joined
    assert "aceite" in joined
    assert "sito" not in joined
    assert "necesito" not in joined


def test_optimize_list_colon_form():
    det = IntentDetector()
    intent = det.detect_intent("canasta: leche evaporada, arroz, aceite vegetal")
    assert intent is not None
    assert intent.intent_type == PriceIntentType.OPTIMIZE
    assert any("leche" in p for p in intent.products_list)
    assert any("arroz" in p for p in intent.products_list)
    assert any("aceite" in p for p in intent.products_list)
