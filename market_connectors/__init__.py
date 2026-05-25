"""market_connectors — Multi-platform e-commerce connectors."""
from .vtex import VtexConnector
from .shopify import ShopifyConnector

# Registry: platform name → connector instance (singletons)
_CONNECTORS: dict[str, VtexConnector | ShopifyConnector] = {
    "vtex": VtexConnector(),
    "shopify": ShopifyConnector(),
}

def get_connector(platform: str):
    """Return the connector instance for a given platform."""
    conn = _CONNECTORS.get(platform)
    if not conn:
        raise ValueError(f"Unknown platform: {platform}. Known: {list(_CONNECTORS)}")
    return conn
