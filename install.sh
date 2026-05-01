#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="$HOME/.config/opencode"

# Ensure target directories exist
mkdir -p "$CONFIG_DIR/skills" "$CONFIG_DIR/agents"

# Install skills
echo "Installing skills to $CONFIG_DIR/skills/..."
for d in "$SCRIPT_DIR/skills"/*/; do
  cp -r "$d" "$CONFIG_DIR/skills/"
done

# Install agents
echo "Installing agents to $CONFIG_DIR/agents/..."
cp "$SCRIPT_DIR/agents/"* "$CONFIG_DIR/agents/"

# Install common scripts (shared office utilities)
# Placed at $CONFIG_DIR/common/ so ../../common/ resolves from skills/*/
if [ -d "$SCRIPT_DIR/common" ]; then
  echo "Installing common scripts..."
  cp -r "$SCRIPT_DIR/common" "$CONFIG_DIR/common"
fi

echo "Done. $(ls "$CONFIG_DIR/skills/" | grep -c /) skills and $(ls "$CONFIG_DIR/agents/" | wc -l) agents installed."
