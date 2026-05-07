# ThreatWinds Vision MCP Server Design

## Summary
Add a Python FastMCP server that exposes ThreatWinds-powered vision analysis for:
- image-based PDFs
- images

The server must accept an arbitrary caller-provided prompt describing what to extract.
Each tool will support exactly one input source per request:
- local file path
- remote URL
- base64 payload

The implementation should refactor the existing PDF OCR logic in `skills/pdf/scripts/ocr_vision.py` into shared library code used by both the CLI script and the MCP server.

## Goals
- Provide MCP tools for ThreatWinds-based PDF and image analysis
- Support arbitrary extraction prompts
- Support three source input modes: path, URL, base64
- Reuse current PDF OCR behavior where practical
- Keep responsibilities isolated and independently testable
- Preserve existing CLI functionality for the PDF skill

## Non-goals
- OCR provider abstraction across multiple vendors
- Batch multi-document processing in a single tool call
- Advanced structured-schema extraction enforcement beyond prompt-driven output
- Authentication/session handling beyond env-based API credentials
- Browser/UI integration

## Proposed tool surface

### `analyze_pdf`
Accept one and only one of:
- `pdf_path`
- `pdf_url`
- `pdf_base64`

Other inputs:
- `prompt` (required)
- `pages` (optional)
- `model` (optional, default `qwen-3.6`)
- `dpi` (optional)
- `max_tokens` (optional)

Returns:
- page-by-page extracted content
- combined content
- warnings and errors
- metadata about source/model/options used

### `analyze_image`
Accept one and only one of:
- `image_path`
- `image_url`
- `image_base64`

Other inputs:
- `prompt` (required)
- `model` (optional, default `qwen-3.6`)
- `max_tokens` (optional)

Returns:
- extracted content
- warnings and errors
- metadata about source/model/options used

## Architecture

### 1. Source loading module
Responsibility:
- validate exactly one source input
- read local files
- fetch HTTP/HTTPS URLs
- decode base64 or data URLs
- detect/validate MIME/file type
- create and clean up temp files where needed

This module should not know anything about ThreatWinds or MCP.

### 2. PDF rendering module
Responsibility:
- validate PDF content
- convert PDF pages to images
- handle page selection/range parsing
- return rendered page images for analysis

This module should not know anything about transport, prompts, or MCP.

### 3. ThreatWinds vision client
Responsibility:
- construct ThreatWinds chat completion payloads
- attach image payloads
- set auth headers
- send requests
- parse responses
- normalize API/network errors

This module should not know about PDFs specifically.

### 4. Analysis service
Responsibility:
- orchestrate source loading, PDF rendering, and ThreatWinds calls
- implement PDF page iteration
- aggregate page results
- represent partial failure cleanly

This is the main application logic layer.

### 5. MCP server entrypoint
Responsibility:
- define FastMCP tools
- validate tool arguments
- call analysis service
- shape tool responses for MCP consumers

### 6. CLI compatibility layer
Responsibility:
- update `skills/pdf/scripts/ocr_vision.py` to use shared analysis logic
- preserve current CLI behavior and options as much as possible

## Data flow

### PDF flow
1. MCP tool receives source + prompt
2. source loading module resolves the input into a local PDF artifact
3. PDF rendering module converts selected pages into images
4. analysis service sends each page image to ThreatWinds using the same prompt
5. per-page results are aggregated
6. MCP tool returns structured response

### Image flow
1. MCP tool receives source + prompt
2. source loading module resolves the input into an image artifact
3. analysis service sends the image to ThreatWinds
4. MCP tool returns structured response

## Response format

### PDF result shape
```json
{
  "input_type": "pdf",
  "source_type": "url",
  "model": "qwen-3.6",
  "prompt": "Extract invoice number and total",
  "results": [
    {
      "page": 1,
      "content": "..."
    }
  ],
  "combined_content": "...",
  "warnings": [],
  "errors": []
}
```

### Image result shape
```json
{
  "input_type": "image",
  "source_type": "base64",
  "model": "qwen-3.6",
  "prompt": "Describe the chart and extract all labels",
  "content": "...",
  "warnings": [],
  "errors": []
}
```

## Error handling

### Fail-fast errors
Fail the request immediately when:
- zero sources are provided
- multiple sources are provided
- required prompt is missing
- `THREATWINDS_API_KEY` is missing
- base64 cannot be decoded
- URL scheme is unsupported
- source content is not a valid PDF/image for the selected tool
- local path does not exist / is not a file
- page range is invalid

### Partial failures
For PDFs:
- if one or more pages fail during ThreatWinds analysis, return successful page results where available
- include page-level errors
- include a top-level warning indicating partial extraction

### API/network failures
Normalize:
- ThreatWinds HTTP errors
- request timeouts
- malformed API responses
- download timeouts for URL inputs

Errors must be actionable and identify the stage that failed.

## Security and operational constraints

### URL inputs
- only `http` and `https`
- reject unsupported schemes
- enforce download timeout
- enforce maximum download size
- store downloaded data in temporary files only when needed
- clean up temporary files after processing

### Base64 inputs
- support raw base64 and data URLs
- enforce maximum decoded payload size
- inspect decoded content type rather than trusting caller metadata

### Local file inputs
- validate existence and readability
- reject directories
- return explicit permission/path errors

## Testing strategy

### Unit tests
- source exclusivity validation
- page range parsing
- MIME/file type validation
- base64 normalization
- URL validation
- response aggregation
- partial error handling

### Mocked integration tests
- mock ThreatWinds request/response behavior
- validate `analyze_pdf` for path/url/base64
- validate `analyze_image` for path/url/base64

### Manual verification
- scanned PDF via local path
- image via local path
- image via URL
- PDF via base64
- invalid page range
- invalid mixed-source input
- missing API key

## Implementation impact
Likely changes:
- add new Python MCP server module(s)
- add shared ThreatWinds analysis library
- refactor `skills/pdf/scripts/ocr_vision.py` to use shared library
- document setup and example MCP configuration
- optionally add OpenCode config example for wiring the server

## Open questions deferred
These are intentionally out of v1 unless requested later:
- schema-constrained JSON extraction
- batch multi-file processing
- support for non-image office docs
- OCR caching
- async/queue-based processing for very large PDFs

## Recommendation
Proceed with:
- Python FastMCP
- shared analysis library
- `analyze_pdf` + `analyze_image`
- exactly one source per request
- support for path, URL, and base64
- arbitrary extraction prompt passthrough
