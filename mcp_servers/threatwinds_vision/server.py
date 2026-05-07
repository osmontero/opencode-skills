"""ThreatWinds Vision MCP Server — FastMCP entrypoint.

Exposes two MCP tools:
- analyze_pdf: analyze a PDF document using vision AI
- analyze_image: analyze an image using vision AI

Each tool accepts the document/image via path, URL, or base64-encoded data,
sends it to the ThreatWinds vision API, and returns structured JSON results.
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from mcp_servers.threatwinds_vision.analysis_service import (
    analyze_image_source,
    analyze_pdf_source,
)
from mcp_servers.threatwinds_vision.models import (
    AnalyzeImageInput,
    AnalyzePdfInput,
)

mcp = FastMCP("threatwinds_vision_mcp")


@mcp.tool(
    name="analyze_pdf",
    title="Analyze PDF Document",
    description=(
        "Analyze a PDF document using vision AI. "
        "Accepts a PDF via local path, URL, or base64-encoded data. "
        "Renders each page as an image and sends it to the ThreatWinds "
        "vision API for analysis. Returns per-page results and combined content."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def analyze_pdf(
    prompt: str,
    pdf_path: str | None = None,
    pdf_url: str | None = None,
    pdf_base64: str | None = None,
    pages: str | None = None,
    model: str = "qwen-3.6",
    dpi: int = 200,
    max_tokens: int = 4096,
) -> str:
    """Analyze a PDF document using vision AI.

    Exactly one of pdf_path, pdf_url, or pdf_base64 must be provided.

    Args:
        prompt: Analysis prompt to send with each page.
        pdf_path: Path to a local PDF file.
        pdf_url: URL to download a PDF from.
        pdf_base64: Base64-encoded PDF data.
        pages: Optional page selection string (e.g. "1-3", "1,3,5").
        model: Model identifier (default: "qwen-3.6").
        dpi: Resolution for PDF rendering, 72-600 (default: 200).
        max_tokens: Maximum completion tokens per page (default: 4096).

    Returns:
        JSON string with per-page analysis results, combined content,
        and any warnings or errors.
    """
    try:
        # Validate inputs using Pydantic model
        AnalyzePdfInput(
            prompt=prompt,
            pdf_path=pdf_path,
            pdf_url=pdf_url,
            pdf_base64=pdf_base64,
            pages=pages,
            model=model,
            dpi=dpi,
            max_tokens=max_tokens,
        )

        result = analyze_pdf_source(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            dpi=dpi,
            pages=pages,
            pdf_path=pdf_path,
            pdf_url=pdf_url,
            pdf_base64=pdf_base64,
        )
        return json.dumps(result.model_dump(), indent=2)
    except Exception as exc:
        return json.dumps(
            {
                "input_type": "pdf",
                "source_type": "path" if pdf_path else "url" if pdf_url else "base64",
                "model": model,
                "prompt": prompt,
                "results": [],
                "combined_content": "",
                "warnings": [],
                "errors": [{"code": "server_error", "message": str(exc)}],
            },
            indent=2,
        )


@mcp.tool(
    name="analyze_image",
    title="Analyze Image",
    description=(
        "Analyze an image using vision AI. "
        "Accepts an image via local path, URL, or base64-encoded data. "
        "Sends the image to the ThreatWinds vision API for analysis "
        "and returns structured JSON results."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def analyze_image(
    prompt: str,
    image_path: str | None = None,
    image_url: str | None = None,
    image_base64: str | None = None,
    model: str = "qwen-3.6",
    max_tokens: int = 4096,
) -> str:
    """Analyze an image using vision AI.

    Exactly one of image_path, image_url, or image_base64 must be provided.

    Args:
        prompt: Analysis prompt to send with the image.
        image_path: Path to a local image file.
        image_url: URL to download an image from.
        image_base64: Base64-encoded image data.
        model: Model identifier (default: "qwen-3.6").
        max_tokens: Maximum completion tokens (default: 4096).

    Returns:
        JSON string with analysis content and metadata.
    """
    try:
        # Validate inputs using Pydantic model
        AnalyzeImageInput(
            prompt=prompt,
            image_path=image_path,
            image_url=image_url,
            image_base64=image_base64,
            model=model,
            max_tokens=max_tokens,
        )

        result = analyze_image_source(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            image_path=image_path,
            image_url=image_url,
            image_base64=image_base64,
        )
        return json.dumps(result.model_dump(), indent=2)
    except Exception as exc:
        return json.dumps(
            {
                "input_type": "image",
                "source_type": (
                    "path" if image_path else "url" if image_url else "base64"
                ),
                "model": model,
                "prompt": prompt,
                "content": "",
                "warnings": [],
                "errors": [{"code": "server_error", "message": str(exc)}],
            },
            indent=2,
        )


if __name__ == "__main__":
    mcp.run()
