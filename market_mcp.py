"""Console entry and thin re-export layer for MCP server (`market-mcp` after pip install)."""

from market_core.market_mcp import api, get_token, handle_tool, main

__all__ = ["api", "get_token", "handle_tool", "main"]

if __name__ == "__main__":
    main()