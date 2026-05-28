---
name: Agent integration feedback
description: Report issues connecting CLI Market MCP to your AI agent or IDE
title: "[Agent]: "
labels: ["agent-integration", "dx"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Help us improve time-to-first-success for agent developers.
        See [DX audit](https://github.com/Treevu-ai/cli-market-world/blob/main/docs/dx-audit.md).
  - type: dropdown
    id: environment
    attributes:
      label: Environment
      options:
        - Cursor
        - Claude Desktop
        - Windsurf
        - Other IDE
        - Custom agent
  - type: input
    id: cli_version
    attributes:
      label: cli-market version
      placeholder: pip show cli-market
  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      description: From pip install to the failure
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
  - type: textarea
    id: actual
    attributes:
      label: Actual behavior
  - type: textarea
    id: logs
    attributes:
      label: MCP / API logs (redact tokens)
