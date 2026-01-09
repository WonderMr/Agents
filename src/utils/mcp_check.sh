#!/bin/sh

# Resolve REPO_ROOT relative to the script location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_PATH="$REPO_ROOT/.cursor/config/mcp-status.json"
STATE_FILE="$REPO_ROOT/.cursor/state/runtime_status.md"

MCP_ENABLED=false

if [ -f "$CONFIG_PATH" ]; then
    # Simple grep check for "mcp_enabled": true
    if grep -qE '"mcp_enabled"\s*:\s*true' "$CONFIG_PATH"; then
        MCP_ENABLED=true
    fi
fi

# Generate Timestamp
DATE_STR=$(date "+%Y-%m-%d %H:%M:%S")

# Update State File
cat <<EOF > "$STATE_FILE"
# Runtime Status
Last Checked: $DATE_STR

## MCP Status
Enabled: $MCP_ENABLED
Strategy: $([ "$MCP_ENABLED" = true ] && echo "Call \`get_agent_context(agent_name, query)\`" || echo "Use Static Mode (Load system_prompt.mdc manually)")
EOF

# Output for the Agent (Standard Output)
if [ "$MCP_ENABLED" = true ]; then
    echo "✅ MCP ENABLED (State cached to .cursor/state/runtime_status.md)"
    echo "Strategy: Call \`get_agent_context(agent_name, query)\`"
else
    echo "🚫 MCP DISABLED (State cached to .cursor/state/runtime_status.md)"
    echo "Strategy: Use Static Mode (Load system_prompt.mdc manually)"
fi
