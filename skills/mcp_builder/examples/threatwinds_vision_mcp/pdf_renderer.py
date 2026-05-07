"""PDF rendering helpers for ThreatWinds Vision MCP Server.

Provides page range parsing and PDF-to-image rendering using pypdfium2.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pypdfium2  # pytype: disable=import-error


@dataclass
class RenderedPage:
    """A single rendered PDF page as a PNG image on disk."""

    page_num: int
    image_path: Path


def parse_pages(pages: str) -> set[int]:
    """Parse a page selection string into a set of 1-based page numbers.

    Supports comma-separated values and range notation::

        >>> parse_pages("1-3")
        {1, 2, 3}
        >>> parse_pages("1,3,5")
        {1, 3, 5}
        >>> parse_pages("1-3,5,7-8")
        {1, 2, 3, 5, 7, 8}

    Args:
        pages: Page selection string (e.g. "1-3", "1,3,5", "1-3,5,7-8").

    Returns:
        Set of 1-based page numbers.

    Raises:
        ValueError: If the string is empty, contains invalid values,
            non-positive page numbers, or reverse ranges.
    """
    if not pages.strip():
        raise ValueError("Page selection string is empty")

    result: set[int] = set()

    for part in pages.split(","):
        part = part.strip()
        if "-" in part:
            # Range notation: split on first dash only, but handle leading negative
            # A leading dash means negative number, not a range
            if part.startswith("-"):
                try:
                    page = int(part)
                except ValueError:
                    raise ValueError(f"Invalid page number: {part}")
                if page <= 0:
                    raise ValueError("Page numbers must be positive")
                result.add(page)
                continue
            tokens = part.split("-", 1)
            start_str = tokens[0].strip()
            end_str = tokens[1].strip()
            if not start_str or not end_str:
                raise ValueError(f"Invalid page range: {part}")
            try:
                start = int(start_str)
                end = int(end_str)
            except ValueError:
                raise ValueError(f"Invalid page range: {part}")
            if start <= 0 or end <= 0:
                raise ValueError("Page numbers must be positive")
            if start > end:
                raise ValueError(f"invalid range: {part} (start > end)")
            result.update(range(start, end + 1))
        else:
            # Single page number
            try:
                page = int(part)
            except ValueError:
                raise ValueError(f"Invalid page number: {part}")
            if page <= 0:
                raise ValueError("Page numbers must be positive")
            result.add(page)

    return result


def filter_rendered_pages(
    rendered: list[RenderedPage],
    pages: Optional[str] = None,
) -> list[RenderedPage]:
    """Filter a list of rendered pages by page selection string.

    Args:
        rendered: List of rendered pages to filter.
        pages: Optional page selection string. If None, all pages are returned.

    Returns:
        Filtered list of rendered pages, maintaining original order.
    """
    if pages is None:
        return rendered

    selected = parse_pages(pages)
    return [rp for rp in rendered if rp.page_num in selected]


def render_pdf_to_images(
    pdf_path: Path,
    dpi: int = 200,
    pages: Optional[str] = None,
) -> list[RenderedPage]:
    """Render PDF pages to PNG images.

    Args:
        pdf_path: Path to the PDF file.
        dpi: Resolution for rendering (72-600).
        pages: Optional page selection string. If None, all pages are rendered.

    Returns:
        List of RenderedPage objects with page numbers and image paths.

    Raises:
        ValueError: If the PDF file cannot be opened or is invalid.

    Note:
        The caller is responsible for deleting the temporary image files
        after use. Files are created with delete=False.
    """
    if not pdf_path.exists():
        raise ValueError(f"PDF file does not exist: {pdf_path}")

    try:
        doc = pypdfium2.PdfDocument(pdf_path)
    except Exception as exc:
        raise ValueError(f"Invalid PDF file: {pdf_path}") from exc

    total_pages = len(doc)

    # Determine which pages to render
    if pages is not None:
        page_nums = sorted(parse_pages(pages))
        # Filter to only valid page numbers
        page_nums = [p for p in page_nums if 1 <= p <= total_pages]
    else:
        page_nums = list(range(1, total_pages + 1))

    rendered: list[RenderedPage] = []
    for page_num in page_nums:
        # pypdfium2 uses 0-based indexing
        pdf_page = doc[page_num - 1]
        bitmap = pdf_page.render(scale=dpi / 72.0)

        handle = tempfile.NamedTemporaryFile(
            delete=False, suffix=".png", prefix=f"page_{page_num:04d}_"
        )
        try:
            bitmap.save(handle.name)
            handle.flush()
        finally:
            handle.close()

        rendered.append(
            RenderedPage(page_num=page_num, image_path=Path(handle.name))
        )

    return rendered
