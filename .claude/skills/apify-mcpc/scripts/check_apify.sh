#!/usr/bin/env bash
# Verify prerequisites for mcpc-apify skill
set -euo pipefail

errors=0

# User-Agent for tracking skill usage in Apify analytics (mirrors run_actor.js pattern)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_JSON="$SCRIPT_DIR/../../../.claude-plugin/plugin.json"
if [ -f "$PLUGIN_JSON" ]; then
  if command -v jq &>/dev/null; then
    PLUGIN_VERSION=$(jq -r '.version // "unknown"' "$PLUGIN_JSON" 2>/dev/null || echo "unknown")
  else
    PLUGIN_VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$PLUGIN_JSON" | head -1 | sed 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)"/\1/')
    PLUGIN_VERSION="${PLUGIN_VERSION:-unknown}"
  fi
else
  PLUGIN_VERSION="unknown"
fi
USER_AGENT="apify-agent-skills/apify-mcpc-${PLUGIN_VERSION}"

# 1. Check mcpc is installed
if command -v mcpc &>/dev/null; then
  echo "✓ mcpc $(mcpc --version 2>/dev/null || echo '?')"
else
  echo "✗ mcpc not found. Install: npm install -g @apify/mcpc"
  errors=$((errors + 1))
fi

# 2. Check OAuth profile for mcp.apify.com
if command -v mcpc &>/dev/null; then
  profiles=$(mcpc 2>&1 || true)
  if echo "$profiles" | grep -q 'mcp.apify.com'; then
    echo "✓ OAuth profile for mcp.apify.com exists"
  else
    echo "⚠ No OAuth profile for mcp.apify.com — run: mcpc mcp.apify.com login"
  fi
fi

# 3. Check existing sessions (match exact session names)
if command -v mcpc &>/dev/null; then
  sessions=$(mcpc 2>&1 || true)
  if echo "$sessions" | grep -q '@apify →'; then
    echo "✓ Session @apify exists"
  else
    echo "— No @apify session (create with: mcpc mcp.apify.com connect @apify)"
  fi
  if echo "$sessions" | grep -q '@apify-docs →'; then
    echo "✓ Session @apify-docs exists"
  else
    echo "— No @apify-docs session (create with: mcpc 'mcp.apify.com?tools=docs' connect @apify-docs)"
  fi
fi

if [ "$errors" -gt 0 ]; then
  echo ""
  echo "Found $errors issue(s). Fix them before proceeding."
  exit 1
fi

# Usage ping with User-Agent tracking (best-effort, non-blocking)
mcpc -H "User-Agent: ${USER_AGENT}/check" @apify ping &>/dev/null &

echo ""
echo "Ready to use mcpc-apify skill. (UA: ${USER_AGENT})"
