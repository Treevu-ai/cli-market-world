#!/usr/bin/env bash
# Deprecate legacy io.github.Treevu-ai/cli-market (PyPI cli-market frozen).
# Run after: mcp-publisher login github
set -euo pipefail
MSG="Use io.github.Treevu-ai/cli-market-world (pip install cli-market-world)."
printf 'y\n' | mcp-publisher status --status deprecated --all-versions --message "$MSG" \
  io.github.Treevu-ai/cli-market
echo "Done. Verify: curl -s 'https://registry.modelcontextprotocol.io/v0.1/servers?search=cli-market'"
