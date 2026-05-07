# ThreatWinds Vision MCP Server

FastMCP server that analyzes scanned PDFs and images through the [ThreatWinds AI API](https://threatwinds.com) using vision models. Supports arbitrary extraction prompts and three input modes: local file paths, remote URLs, and base64 payloads.

## Requirements

- Python 3.12+
- `THREATWINDS_API_KEY` environment variable
- Optional: `THREATWINDS_API_SECRET` (for API key/secret auth mode)

## Running the server

Dependencies are managed via `pyproject.toml` and installed by `install.sh` into `~/.local/opencode-venv/`. The server is copied to `~/.config/opencode/mcp_servers/` by `install.sh`.

```bash
# After install.sh:
~/.local/opencode-venv/bin/python3 ~/.config/opencode/mcp_servers/threatwinds_vision/server.py

# Or from the repo (without install.sh):
~/.local/opencode-venv/bin/python3 mcp_servers/threatwinds_vision/server.py
```

## Tools

### `analyze_pdf`

Analyzes a scanned PDF by converting pages to images and sending them to the ThreatWinds vision API.

**Parameters:**
- `prompt` (required) — Arbitrary extraction instructions for the vision model
- `pdf_path` / `pdf_url` / `pdf_base64` (exactly one required) — PDF source
- `pages` (optional) — Page range, e.g., `"1-3"` or `"1,3,5"`
- `model` (optional, default: `"qwen-3.6"`) — ThreatWinds model ID
- `dpi` (optional, default: `200`) — Image resolution (72–600)
- `max_tokens` (optional, default: `4096`) — Max output tokens per page

**Example:**
```json
{
  "prompt": "Extract the invoice number, date, line items, and total. Output as JSON.",
  "pdf_path": "/path/to/invoice.pdf",
  "pages": "1-2"
}
```

### `analyze_image`

Analyzes an image by sending it to the ThreatWinds vision API.

**Parameters:**
- `prompt` (required) — Arbitrary extraction instructions for the vision model
- `image_path` / `image_url` / `image_base64` (exactly one required) — Image source
- `model` (optional, default: `"qwen-3.6"`) — ThreatWinds model ID
- `max_tokens` (optional, default: `4096`) — Max output tokens

**Example:**
```json
{
  "prompt": "Describe the chart and extract all data labels as a table.",
  "image_url": "https://example.com/chart.png"
}
```

## OpenCode MCP Configuration

Add this to your `.opencode/opencode.json` under the `mcp` section:

```json
{
  "threatwinds-vision": {
    "type": "local",
    "command": [
      "~/.local/opencode-venv/bin/python3",
      "~/.config/opencode/mcp_servers/threatwinds_vision/server.py"
    ],
    "environment": {
      "THREATWINDS_API_KEY": "{env:THREATWINDS_API_KEY}",
      "THREATWINDS_API_SECRET": "{env:THREATWINDS_API_SECRET}"
    }
  }
}
```

Or just run `./install.sh` — it copies the server and config automatically.

## Architecture

The server is built from shared modules:

| Module | Responsibility |
|--------|---------------|
| `source_loader.py` | Normalize local path, URL, and base64 inputs |
| `pdf_renderer.py` | Convert PDF pages to images |
| `vision_client.py` | Call ThreatWinds `/chat/completions` endpoint |
| `analysis_service.py` | Orchestrate PDF/image analysis |
| `server.py` | FastMCP tool definitions |
| `models.py` | Pydantic request/response models |

The existing PDF skill CLI (`skills/pdf/scripts/ocr_vision.py`) has been refactored to use these shared modules.
