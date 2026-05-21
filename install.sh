#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="$HOME/.config/opencode"
OPENVEN="$HOME/.local/opencode-venv"

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
  rm -rf "$CONFIG_DIR/skills/$name"
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

# Install MCP servers
echo "Installing MCP servers to $CONFIG_DIR/mcp_servers/..."
if [ -d "$SCRIPT_DIR/mcp_servers" ]; then
  mkdir -p "$CONFIG_DIR/mcp_servers"
  for d in "$CONFIG_DIR/mcp_servers"/*/; do
    name="$(basename "$d")"
    if [ ! -d "$SCRIPT_DIR/mcp_servers/$name" ]; then
      echo "  Removing $name (no longer in repo)"
      rm -rf "$d"
    fi
  done
  for d in "$SCRIPT_DIR/mcp_servers"/*/; do
    name="$(basename "$d")"
    rm -rf "$CONFIG_DIR/mcp_servers/$name"
    cp -r "$d" "$CONFIG_DIR/mcp_servers/$name"
  done
fi

# Install opencode.json config (replaces global config)
GLOBAL_CONFIG="$CONFIG_DIR/opencode.json"
REPO_CONFIG="$SCRIPT_DIR/.opencode/opencode.json"
if [ -f "$REPO_CONFIG" ]; then
  echo "Installing opencode.json config..."
  cp "$REPO_CONFIG" "$GLOBAL_CONFIG"
fi

# Install prompt files referenced by opencode.json
if [ -d "$SCRIPT_DIR/.opencode/prompts" ]; then
  echo "Installing prompt files..."
  mkdir -p "$CONFIG_DIR/prompts"
  cp "$SCRIPT_DIR/.opencode/prompts/"* "$CONFIG_DIR/prompts/"
fi

# Remove legacy common folder from older installs
if [ -d "$CONFIG_DIR/common" ]; then
  echo "Removing legacy common folder from $CONFIG_DIR..."
  rm -rf "$CONFIG_DIR/common"
fi

# Install Python dependencies via uv
echo "Setting up Python environment..."
if ! command -v uv &>/dev/null; then
  echo "  Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.cargo/bin:$PATH"
fi

if [ -d "$OPENVEN" ]; then
  echo "  Updating existing venv..."
  uv pip install --python "$OPENVEN/bin/python" -e "$SCRIPT_DIR"
else
  echo "  Creating virtual environment..."
  uv venv "$OPENVEN" --python 3.12 --allow-incomplete-chapters 2>/dev/null || \
    uv venv "$OPENVEN" --python 3.12
  uv pip install --python "$OPENVEN/bin/python" -e "$SCRIPT_DIR"
fi

echo "  Python environment ready at $OPENVEN"
echo "  Activate with: source $OPENVEN/bin/activate"

# Install LSP dependencies in opencode's node_modules
# These are required by built-in LSP servers that resolve from opencode's internal directory
OPENCODE_DIR="$HOME/.opencode"
if [ -d "$OPENCODE_DIR/node_modules" ]; then
  echo "Setting up LSP dependencies..."
  OPENCODE_NPM_DEPS="typescript typescript-language-server pyright"
  for dep in $OPENCODE_NPM_DEPS; do
    if [ ! -d "$OPENCODE_DIR/node_modules/$dep" ]; then
      echo "  Installing $dep..."
      (cd "$OPENCODE_DIR" && npm install --no-save "$dep" 2>/dev/null)
    fi
  done
fi

echo "Done. $(ls -d "$CONFIG_DIR/skills/"*/ 2>/dev/null | wc -l) skills and $(ls "$CONFIG_DIR/agents/"*.md 2>/dev/null | wc -l) agents installed."
