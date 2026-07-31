"""Unit tests for WhatsApp error formatting (no network)."""
from src.whatsapp_formatter import WhatsAppFormatter


def test_format_api_error_429():
    fmt = WhatsAppFormatter()
    msg = fmt.format_api_error("search_http_429", action="buscar ese producto")
    assert "Demasiadas consultas" in msg
    assert "minuto" in msg.lower() or "minuto" in msg


def test_format_api_error_403():
    fmt = WhatsAppFormatter()
    msg = fmt.format_api_error("basket_http_403", action="optimizar tu canasta")
    assert "permiso" in msg.lower() or "Pro" in msg


def test_format_search_uses_429_message():
    fmt = WhatsAppFormatter()
    msg = fmt.format_search_result({"error": "search_http_429", "products": []})
    assert "Demasiadas consultas" in msg
