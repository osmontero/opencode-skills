$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$CONFIG_DIR = "$env:USERPROFILE\.config\opencode"
$OPENVEN = "$env:USERPROFILE\.local\opencode-venv"

# Ensure target directories exist
New-Item -ItemType Directory -Path "$CONFIG_DIR\skills", "$CONFIG_DIR\agents" -Force | Out-Null

# Clean and install skills — remove any skill not in the repo
Write-Host "Installing skills to $CONFIG_DIR\skills\..."
$repoSkills = Get-ChildItem -Directory -LiteralPath "$SCRIPT_DIR\skills"
$configSkills = Get-ChildItem -Directory -LiteralPath "$CONFIG_DIR\skills" -ErrorAction SilentlyContinue

foreach ($d in $configSkills) {
    $name = $d.Name
    if (-not ($repoSkills.Name -contains $name)) {
        Write-Host "  Removing $name (no longer in repo)"
        Remove-Item -LiteralPath $d.FullName -Recurse -Force
    }
}

foreach ($d in $repoSkills) {
    $name = $d.Name
    $dest = "$CONFIG_DIR\skills\$name"
    if (Test-Path -LiteralPath $dest) {
        Remove-Item -LiteralPath $dest -Recurse -Force
    }
    Copy-Item -LiteralPath $d.FullName -Destination $dest -Recurse -Force
}

# Clean and install agents — remove any agent not in the repo
Write-Host "Installing agents to $CONFIG_DIR\agents\..."
$repoAgents = Get-ChildItem -File -LiteralPath "$SCRIPT_DIR\agents"
$configAgents = Get-ChildItem -File -LiteralPath "$CONFIG_DIR\agents" -ErrorAction SilentlyContinue

foreach ($f in $configAgents) {
    $name = $f.Name
    if (-not ($repoAgents.Name -contains $name)) {
        Write-Host "  Removing $name (no longer in repo)"
        Remove-Item -LiteralPath $f.FullName -Force
    }
}

foreach ($f in $repoAgents) {
    Copy-Item -LiteralPath $f.FullName -Destination "$CONFIG_DIR\agents\$($f.Name)" -Force
}

# Install MCP servers
Write-Host "Installing MCP servers to $CONFIG_DIR\mcp_servers\..."
if (Test-Path -LiteralPath "$SCRIPT_DIR\mcp_servers") {
    New-Item -ItemType Directory -Path "$CONFIG_DIR\mcp_servers" -Force | Out-Null
    $repoMCPs = Get-ChildItem -Directory -LiteralPath "$SCRIPT_DIR\mcp_servers"
    $configMCPs = Get-ChildItem -Directory -LiteralPath "$CONFIG_DIR\mcp_servers" -ErrorAction SilentlyContinue

    foreach ($d in $configMCPs) {
        $name = $d.Name
        if (-not ($repoMCPs.Name -contains $name)) {
            Write-Host "  Removing $name (no longer in repo)"
            Remove-Item -LiteralPath $d.FullName -Recurse -Force
        }
    }

    foreach ($d in $repoMCPs) {
        $name = $d.Name
        $dest = "$CONFIG_DIR\mcp_servers\$name"
        if (Test-Path -LiteralPath $dest) {
            Remove-Item -LiteralPath $dest -Recurse -Force
        }
        Copy-Item -LiteralPath $d.FullName -Destination $dest -Recurse -Force
    }
}

# Install opencode.json config (replaces global config)
$GLOBAL_CONFIG = "$CONFIG_DIR\opencode.json"
$REPO_CONFIG = "$SCRIPT_DIR\.opencode\opencode.json"
if (Test-Path -LiteralPath $REPO_CONFIG) {
    Write-Host "Installing opencode.json config..."
    Copy-Item -LiteralPath $REPO_CONFIG -Destination $GLOBAL_CONFIG -Force
}

# Install prompt files referenced by opencode.json
if (Test-Path -LiteralPath "$SCRIPT_DIR\.opencode\prompts") {
    Write-Host "Installing prompt files..."
    New-Item -ItemType Directory -Path "$CONFIG_DIR\prompts" -Force | Out-Null
    Get-ChildItem -File -LiteralPath "$SCRIPT_DIR\.opencode\prompts" | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination "$CONFIG_DIR\prompts\$($_.Name)" -Force
    }
}

# Remove legacy common folder from older installs
if (Test-Path -LiteralPath "$CONFIG_DIR\common") {
    Write-Host "Removing legacy common folder from $CONFIG_DIR..."
    Remove-Item -LiteralPath "$CONFIG_DIR\common" -Recurse -Force
}

# Install Python dependencies via uv
Write-Host "Setting up Python environment..."
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "  Installing uv..."
    powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
}

if (Test-Path -LiteralPath $OPENVEN) {
    Write-Host "  Updating existing venv..."
    uv pip install --python "$OPENVEN\Scripts\python.exe" -e "$SCRIPT_DIR"
} else {
    Write-Host "  Creating virtual environment..."
    try {
        uv venv $OPENVEN --python 3.12 --allow-incomplete-chapters 2>$null
    } catch {
        uv venv $OPENVEN --python 3.12
    }
    uv pip install --python "$OPENVEN\Scripts\python.exe" -e "$SCRIPT_DIR"
}

Write-Host "  Python environment ready at $OPENVEN"

# Install LSP dependencies in opencode's node_modules
# These are required by built-in LSP servers that resolve from opencode's internal directory
$OPENCODE_DIR = "$env:USERPROFILE\.opencode"
if (Test-Path -LiteralPath "$OPENCODE_DIR\node_modules") {
    Write-Host "Setting up LSP dependencies..."
    $OPENCODE_NPM_DEPS = @("typescript", "typescript-language-server", "pyright")
    foreach ($dep in $OPENCODE_NPM_DEPS) {
        if (-not (Test-Path -LiteralPath "$OPENCODE_DIR\node_modules\$dep")) {
            Write-Host "  Installing $dep..."
            Push-Location $OPENCODE_DIR
            try {
                npm install --no-save $dep 2>$null
            } finally {
                Pop-Location
            }
        }
    }
}

# Install LSP dependencies in project's .opencode/node_modules
# The typescript LSP server requires 'typescript' as a project dependency
if (Test-Path -LiteralPath "$SCRIPT_DIR\.opencode\package.json") {
    Write-Host "Setting up project LSP dependencies..."
    Push-Location "$SCRIPT_DIR\.opencode"
    try {
        npm install --ignore-scripts 2>$null
    } finally {
        Pop-Location
    }
}

# Count installed skills and agents
$skillCount = (Get-ChildItem -Directory -LiteralPath "$CONFIG_DIR\skills" -ErrorAction SilentlyContinue).Count
$agentCount = (Get-ChildItem -File -Filter "*.md" -LiteralPath "$CONFIG_DIR\agents" -ErrorAction SilentlyContinue).Count
Write-Host "Done. $skillCount skills and $agentCount agents installed."
