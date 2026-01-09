#!/bin/bash

# Configuration
MCP_CONFIG_PATH="$HOME/.cursor/mcp.json"

# Colors
BLUE='\033[1;34m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔌 GitLab MCP Setup${NC}"

# 1. Check Pre-requisites (npx)
if ! command -v npx &> /dev/null; then
    echo -e "${RED}❌ Error: 'npx' is not installed or not in your PATH.${NC}"
    echo "This MCP server requires Node.js and npx to run."
    echo "Please install Node.js before proceeding."
    exit 1
fi
echo -e "${GREEN}✓ npx found${NC}"

# 2. Ask for GitLab URL
echo ""
read -p "Enter your GitLab Base URL (default: https://gitlab.com): " USER_URL
USER_URL=${USER_URL:-https://gitlab.com}

# Remove trailing slash if present
GITLAB_BASE_URL=${USER_URL%/}

if [ -z "$GITLAB_BASE_URL" ]; then
    echo -e "${RED}❌ URL cannot be empty.${NC}"
    exit 1
fi

GITLAB_API_URL="${GITLAB_BASE_URL}/api/v4"

# 3. Instruction
echo ""
echo "To connect to GitLab, you need to create a Personal Access Token."
echo "Please follow these steps:"
echo -e "1. Open URL: ${BLUE}${GITLAB_BASE_URL}/-/user_settings/personal_access_tokens${NC}"
echo "2. Click 'Add new token'"
echo "3. Fill in the fields:"
echo -e "   - Name: ${BLUE}Cursor MCP${NC}"
echo "   - Expiration date: (leave empty or select a date)"
echo -e "   - Scopes: select ${BLUE}api${NC} and ${BLUE}read_repository${NC}"
echo "4. Click 'Create personal access token'"
echo "5. Copy the generated token (it starts with 'glpat-')"
echo ""
echo "--------------------------------------------------"

# 4. Request Token
while true; do
    echo ""
    read -p "Paste your token (glpat-...): " TOKEN
    if [[ "$TOKEN" == glpat-* ]] && [[ ${#TOKEN} -gt 10 ]]; then
        break
    else
        echo -e "${YELLOW}! Token must start with 'glpat-'. Please try again.${NC}"
    fi
done

# 5. Update mcp.json using Python
echo ""
echo "Updating configuration..."

python3 -c "
import json
import os
import sys

config_path = '$MCP_CONFIG_PATH'
token = '$TOKEN'
api_url = '$GITLAB_API_URL'

try:
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {'mcpServers': {}}

    if 'mcpServers' not in config:
        config['mcpServers'] = {}

    config['mcpServers']['gitlab'] = {
        'command': 'npx',
        'args': ['-y', '@modelcontextprotocol/server-gitlab'],
        'env': {
            'GITLAB_PERSONAL_ACCESS_TOKEN': token,
            'GITLAB_API_URL': api_url
        }
    }

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Configuration successfully written to mcp.json${NC}"
    echo -e "${BLUE}🎉 Done!${NC}"
else
    echo -e "${RED}❌ Error updating configuration file.${NC}"
    exit 1
fi
