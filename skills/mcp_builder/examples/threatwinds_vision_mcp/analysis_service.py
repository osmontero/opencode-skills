"""Analysis orchestration service for ThreatWinds Vision MCP Server.

Ties together source loading, PDF rendering, and vision analysis
to provide high-level analysis functions for images and PDFs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from skills.mcp_builder.examples.threatwinds_vision_mcp.models import (
    AnalysisError,
    AnalysisWarning,
    ImageAnalysisResult,
    PageResult,
    PdfAnalysisResult,
    SourceType,
)
from skills.mcp_builder.examples.threatwinds_vision_mcp.pdf_renderer import (
    RenderedPage,
    render_pdf_to_images,
)
from skills.mcp_builder.examples.threatwinds_vision_mcp.source_loader import (
    LoadedSource,
    load_path_source,
    materialize_base64_source,
    download_url_source,
)
from skills.mcp_builder.examples.threatwinds_vision_mcp.vision_client import (
    request_vision_analysis,
)


def combine_page_content(
    pages: list[tuple[int, str]],
) -> str:
    """Join page results into a single string with page headers.

    Args:
        pages: List of (page_number, content) tuples.

    Returns:
        Combined string with "=== Page N ===" headers separating each page.
    """
    if not pages:
        return ""
    parts: list[str] = []
    for page_num, content in pages:
        parts.append(f"=== Page {page_num} ===\n{content}")
    return "\n".join(parts)


def _resolve_image_source(
    *,
    image_path: Optional[str] = None,
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> tuple[Path, Literal["path", "url", "base64"]]:
    """Resolve an image source to a local file path and source type.

    Exactly one of image_path, image_url, or image_base64 must be provided.

    Args:
        image_path: Path to a local image file.
        image_url: URL to download an image from.
        image_base64: Base64-encoded image data.

    Returns:
        Tuple of (local_path, source_type).

    Raises:
        ValueError: If no source or multiple sources are provided.
    """
    if image_path is not None:
        if image_url is not None or image_base64 is not None:
            raise ValueError(
                "Exactly one image source must be provided "
                "(image_path, image_url, or image_base64)"
            )
        loaded = load_path_source(image_path, expected_kind="image")
        return loaded.local_path, loaded.source_type
    if image_url is not None:
        if image_base64 is not None:
            raise ValueError(
                "Exactly one image source must be provided "
                "(image_path, image_url, or image_base64)"
            )
        loaded = download_url_source(image_url, expected_kind="image")
        return loaded.local_path, loaded.source_type
    if image_base64 is not None:
        loaded = materialize_base64_source(image_base64, expected_kind="image")
        return loaded.local_path, loaded.source_type
    raise ValueError(
        "No image source provided: exactly one of image_path, "
        "image_url, or image_base64 must be given"
    )


def _resolve_pdf_source(
    *,
    pdf_path: Optional[str] = None,
    pdf_url: Optional[str] = None,
    pdf_base64: Optional[str] = None,
) -> tuple[Path, Literal["path", "url", "base64"]]:
    """Resolve a PDF source to a local file path and source type.

    Exactly one of pdf_path, pdf_url, or pdf_base64 must be provided.

    Args:
        pdf_path: Path to a local PDF file.
        pdf_url: URL to download a PDF from.
        pdf_base64: Base64-encoded PDF data.

    Returns:
        Tuple of (local_path, source_type).

    Raises:
        ValueError: If no source or multiple sources are provided.
    """
    if pdf_path is not None:
        if pdf_url is not None or pdf_base64 is not None:
            raise ValueError(
                "Exactly one PDF source must be provided "
                "(pdf_path, pdf_url, or pdf_base64)"
            )
        loaded = load_path_source(pdf_path, expected_kind="pdf")
        return loaded.local_path, loaded.source_type
    if pdf_url is not None:
        if pdf_base64 is not None:
            raise ValueError(
                "Exactly one PDF source must be provided "
                "(pdf_path, pdf_url, or pdf_base64)"
            )
        loaded = download_url_source(pdf_url, expected_kind="pdf")
        return loaded.local_path, loaded.source_type
    if pdf_base64 is not None:
        loaded = materialize_base64_source(pdf_base64, expected_kind="pdf")
        return loaded.local_path, loaded.source_type
    raise ValueError(
        "No PDF source provided: exactly one of pdf_path, "
        "pdf_url, or pdf_base64 must be given"
    )


def analyze_image_source(
    *,
    prompt: str,
    model: str,
    max_tokens: int,
    image_path: Optional[str] = None,
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> ImageAnalysisResult:
    """Orchestrate image analysis: resolve source, send to vision API, return result.

    Args:
        prompt: Analysis prompt to send with the image.
        model: Model identifier (e.g. "qwen-3.6").
        max_tokens: Maximum completion tokens.
        image_path: Path to a local image file.
        image_url: URL to download an image from.
        image_base64: Base64-encoded image data.

    Returns:
        ImageAnalysisResult with analysis content and metadata.
    """
    local_path, source_type = _resolve_image_source(
        image_path=image_path,
        image_url=image_url,
        image_base64=image_base64,
    )
    content = request_vision_analysis(
        image_path=local_path,
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
    )
    return ImageAnalysisResult(
        input_type="image",
        source_type=SourceType(source_type),
        model=model,
        prompt=prompt,
        content=content,
    )


def analyze_pdf_source(
    *,
    prompt: str,
    model: str,
    max_tokens: int,
    dpi: int = 200,
    pages: Optional[str] = None,
    pdf_path: Optional[str] = None,
    pdf_url: Optional[str] = None,
    pdf_base64: Optional[str] = None,
) -> PdfAnalysisResult:
    """Orchestrate PDF analysis: resolve source, render pages, analyze each page.

    Partial page failures are handled gracefully — failed pages produce
    errors in the result but do not stop analysis of remaining pages.

    Args:
        prompt: Analysis prompt to send with each page.
        model: Model identifier (e.g. "qwen-3.6").
        max_tokens: Maximum completion tokens per page.
        dpi: Resolution for PDF rendering (72-600).
        pages: Optional page selection string (e.g. "1-3", "1,3,5").
        pdf_path: Path to a local PDF file.
        pdf_url: URL to download a PDF from.
        pdf_base64: Base64-encoded PDF data.

    Returns:
        PdfAnalysisResult with per-page results, combined content, and errors.
    """
    local_path, source_type = _resolve_pdf_source(
        pdf_path=pdf_path,
        pdf_url=pdf_url,
        pdf_base64=pdf_base64,
    )
    rendered = render_pdf_to_images(
        pdf_path=local_path,
        dpi=dpi,
        pages=pages,
    )

    results: list[PageResult] = []
    errors: list[AnalysisError] = []

    for page in rendered:
        try:
            content = request_vision_analysis(
                image_path=page.image_path,
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
            )
            results.append(PageResult(page=page.page_num, content=content))
        except Exception as exc:
            errors.append(
                AnalysisError(
                    code="page_analysis_failed",
                    message=str(exc),
                    page=page.page_num,
                )
            )

    combined = combine_page_content([(r.page, r.content) for r in results])

    warnings: list[AnalysisWarning] = []
    if errors:
        warnings.append(
            AnalysisWarning(
                code="partial_pdf_analysis",
                message=f"{len(errors)} of {len(rendered)} page(s) failed to analyze",
            )
        )

    return PdfAnalysisResult(
        input_type="pdf",
        source_type=SourceType(source_type),
        model=model,
        prompt=prompt,
        results=results,
        combined_content=combined,
        warnings=warnings,
        errors=errors,
    )
