#!/usr/bin/env bash
#
# Pack agent settings and MCP server
#
# Includes:
#   - .cursor/ (agents, commands, hooks, implants, plans, rules, skills, state)
#   - src/ (MCP server)
#   - scripts/init_repo.sh (repository initialization)
#   - requirements.txt, mcp.json, env.example
#
# Excludes private data and cache.
#
# Supported archivers: 7z, zip, tar
#

set -euo pipefail

# Repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Date for archive name
DATE=$(date +%Y-%m-%d)
BASE_NAME="Agents_${DATE}"

echo "=================================================="
echo "  Packing Agents (settings + MCP server)"
echo "=================================================="
echo

# List of included files/folders
INCLUDES=(
    ".cursor"
    "src"
    "scripts/init_repo.sh"
    "requirements.txt"
    "mcp.json"
    "env.example"
)

# Logging functions
log_info() {
    echo "ℹ️  $1"
}

log_error() {
    echo "❌ $1"
}

log_success() {
    echo "✅ $1"
}

cd "$REPO_ROOT"

# Detect available archiver
if command -v 7z &> /dev/null; then
    ARCHIVER="7z"
    EXT=".7z"
elif command -v zip &> /dev/null; then
    ARCHIVER="zip"
    EXT=".zip"
elif command -v tar &> /dev/null; then
    ARCHIVER="tar"
    EXT=".tar.gz"
else
    log_error "No suitable archiver found (7z, zip, tar)!"
    exit 1
fi

ARCHIVE_NAME="${BASE_NAME}${EXT}"
ARCHIVE_PATH="${REPO_ROOT}/${ARCHIVE_NAME}"

# Remove old archive if exists
if [[ -f "$ARCHIVE_PATH" ]]; then
    rm -f "$ARCHIVE_PATH"
    echo "🗑️  Removed old archive: ${ARCHIVE_NAME}"
fi

log_info "Using archiver: ${ARCHIVER}"
echo "📦 Creating archive: ${ARCHIVE_NAME}"
echo "   Included paths: ${INCLUDES[*]}"
echo

# Execute packing based on archiver
case "$ARCHIVER" in
    "7z")
        7z a -t7z -mx=9 -mmt=on "$ARCHIVE_PATH" \
            "${INCLUDES[@]}" \
            -xr!__pycache__ \
            -xr!*.pyc \
            -xr!*.pyo \
            -xr!.DS_Store \
            -xr!*.log \
            -xr!.cursor/plans \
            -xr!src/ReplicatedStorage \
            -xr!src/ServerScriptService \
            -xr!src/StarterPlayer
        ;;
    "zip")
        # zip requires -x "pattern" for each exclusion.
        # Use array to build command.
        EXCLUDES=(
            "*/__pycache__/*"
            "*.pyc"
            "*.pyo"
            "*/.DS_Store"
            "*.log"
            ".cursor/plans/*"
            "src/ReplicatedStorage/*"
            "src/ServerScriptService/*"
            "src/StarterPlayer/*"
        )
        # Build exclusion arguments
        ZIP_EXCLUDES=()
        for excl in "${EXCLUDES[@]}"; do
            ZIP_EXCLUDES+=("-x" "$excl")
        done

        zip -r -9 "$ARCHIVE_PATH" "${INCLUDES[@]}" "${ZIP_EXCLUDES[@]}"
        ;;
    "tar")
        # tar uses --exclude='pattern'
        # In BSD tar (macOS) and GNU tar the --exclude syntax works, but argument order matters.
        # Use argument array.

        EXCLUDES=(
            "__pycache__"
            "*.pyc"
            "*.pyo"
            ".DS_Store"
            "*.log"
            ".cursor/plans"
            "src/ReplicatedStorage"
            "src/ServerScriptService"
            "src/StarterPlayer"
        )

        TAR_EXCLUDES=()
        for excl in "${EXCLUDES[@]}"; do
            TAR_EXCLUDES+=("--exclude=$excl")
        done

        tar -czf "$ARCHIVE_PATH" "${TAR_EXCLUDES[@]}" "${INCLUDES[@]}"
        ;;
esac

echo
# Check result
if [[ -f "$ARCHIVE_PATH" ]]; then
    SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
    log_success "Archive created: ${ARCHIVE_PATH}"
    echo "   Size: ${SIZE}"
    echo "   Archiver: ${ARCHIVER}"

    echo "🎉 Done!"
else
    log_error "Failed to create archive."
    exit 1
fi
