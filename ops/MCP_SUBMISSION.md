# CLI Market — Submit to MCP Registry

## Process (via mcp-publisher CLI)

```bash
git clone https://github.com/modelcontextprotocol/registry
cd registry
make publisher
./bin/mcp-publisher publish --repo https://pypi.org/project/cli-market-world/
```

The mcp.json at repo root is auto-parsed. Uses GitHub OAuth for namespace verification.

## After publishing

Searchable at registry.modelcontextprotocol.io by: "commerce", "shopping", "prices", "retail".
One-click install for Claude Desktop, DeepSeek, and any MCP client.
