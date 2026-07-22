#!/bin/bash

INPUT=$(cat)
if command -v jq >/dev/null 2>&1; then
  COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')
else
  COMMAND=$(echo "$INPUT" | grep -o '"command"[[:space:]]*:[[:space:]]*"\([^"\\]\|\\.\)*"' | head -n1 | sed -e 's/^"command"[[:space:]]*:[[:space:]]*"//' -e 's/"$//' -e 's/\\"/"/g' -e 's/\\\\/\\/g')
fi

DANGEROUS_PATTERNS=(
  "git reset --hard"
  "git clean -fd"
  "git clean -f"
  "git branch -D"
  "git checkout \."
  "git restore \."
  "push --force"
  "push .*-f( |$)"
  "reset --hard"
)

# Match only against text outside quoted string literals, so a commit message,
# echo string, or heredoc line that happens to contain e.g. "reset --hard" as
# prose doesn't trip the block. Does not handle heredoc bodies (<<EOF ... EOF).
STRIPPED=$(printf '%s' "$COMMAND" | sed -E "s/'[^']*'//g; s/\"[^\"]*\"//g")

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$STRIPPED" | grep -qE "$pattern"; then
    echo "BLOCKED: '$COMMAND' matches dangerous pattern '$pattern'. The user has prevented you from doing this." >&2
    exit 2
  fi
done

exit 0
