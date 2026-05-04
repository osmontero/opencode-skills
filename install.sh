#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="$HOME/.config/opencode"

# Ensure target directories exist
mkdir -p "$CONFIG_DIR/skills" "$CONFIG_DIR/agents"

# Clean and install skills — remove any skill not in the repo
echo "Installing skills to $CONFIG_DIR/skills/..."
for d in "$CONFIG_DIR/skills"/*/; do
  name="$(basename "$d")"
  if [ ! -d "$SCRIPT_DIR/skills/$name" ]; then
    echo "  Removing $name (no longer in repo)"
    rm -rf "$d"
  fi
done
for d in "$SCRIPT_DIR/skills"/*/; do
  name="$(basename "$d")"
  cp -r "$d" "$CONFIG_DIR/skills/$name"
done

# Clean and install agents — remove any agent not in the repo
echo "Installing agents to $CONFIG_DIR/agents/..."
for f in "$CONFIG_DIR/agents/"*.md; do
  [ -f "$f" ] || continue
  name="$(basename "$f")"
  if [ ! -f "$SCRIPT_DIR/agents/$name" ]; then
    echo "  Removing $name (no longer in repo)"
    rm "$f"
  fi
done
cp "$SCRIPT_DIR/agents/"* "$CONFIG_DIR/agents/"

# Install common scripts (shared office utilities)
# Placed at $CONFIG_DIR/common/ so ../../common/ resolves from skills/*/
if [ -d "$SCRIPT_DIR/common" ]; then
  echo "Installing common scripts..."
  cp -r "$SCRIPT_DIR/common" "$CONFIG_DIR/common"
fi

# Install opencode.json config (replaces global config)
GLOBAL_CONFIG="$CONFIG_DIR/opencode.json"
REPO_CONFIG="$SCRIPT_DIR/.opencode/opencode.json"
if [ -f "$REPO_CONFIG" ]; then
  echo "Installing opencode.json config..."
  cp "$REPO_CONFIG" "$GLOBAL_CONFIG"
fi

echo "Done. $(ls -d "$CONFIG_DIR/skills/"*/ 2>/dev/null | wc -l) skills and $(ls "$CONFIG_DIR/agents/" | wc -l) agents installed."
