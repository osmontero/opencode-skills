"""Source loading module for ThreatWinds Vision MCP Server.

Normalizes local paths, URLs, and base64 inputs into validated local artifacts.
"""

from __future__ import annotations

import base64
import binascii
import mimetypes
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

# Default timeout for URL requests in seconds
DEFAULT_TIMEOUT = 30


@dataclass
class LoadedSource:
    """Represents a source that has been materialized to a local path."""

    source_type: Literal["path", "url", "base64"]
    local_path: Path
    mime_type: Optional[str]


@dataclass
class DecodedPayload:
    """Represents decoded base64 content with optional MIME type."""

    content: bytes
    mime_type: Optional[str]


def validate_url(url: str) -> str:
    """Validate that URL uses http or https scheme.

    Args:
        url: The URL string to validate.

    Returns:
        The validated URL string.

    Raises:
        ValueError: If URL scheme is not http or https, or if missing network location.
    """
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https URLs are supported")
    if not parsed.netloc:
        raise ValueError("URL must include a network location")
    return url


def parse_base64_payload(value: str) -> DecodedPayload:
    """Parse a base64 payload, supporting both raw base64 and data URLs.

    Args:
        value: Base64 encoded string, optionally as a data URL.

    Returns:
        DecodedPayload with content bytes and optional MIME type.

    Raises:
        ValueError: If base64 is invalid or decodes to empty content.
    """
    mime_type: Optional[str] = None
    encoded = value
    if value.startswith("data:"):
        header, encoded = value.split(",", 1)
        mime_type = header[5:].split(";", 1)[0] or None

    try:
        content = base64.b64decode(encoded, validate=True)
    except binascii.Error as exc:
        raise ValueError("Invalid base64 payload") from exc

    if not content:
        raise ValueError("Base64 payload decoded to empty content")

    return DecodedPayload(content=content, mime_type=mime_type)


def load_path_source(path_str: str, expected_kind: str) -> LoadedSource:
    """Load a source from a local file path.

    Args:
        path_str: Path to the local file.
        expected_kind: Expected file kind ("pdf" or "image").

    Returns:
        LoadedSource with source_type="path" and resolved local path.

    Raises:
        FileNotFoundError: If path does not exist.
        ValueError: If path is not a file or doesn't match expected kind.
    """
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    mime_type, _ = mimetypes.guess_type(path.name)
    if expected_kind == "pdf" and path.suffix.lower() != ".pdf":
        raise ValueError("Expected a PDF file")
    if expected_kind == "image" and not (mime_type or "").startswith("image/"):
        raise ValueError("Expected an image file")

    return LoadedSource(source_type="path", local_path=path, mime_type=mime_type)


def download_url_source(url: str, expected_kind: str, timeout: int = DEFAULT_TIMEOUT) -> LoadedSource:
    """Download a source from a URL and save to a temporary file.

    Args:
        url: HTTP or HTTPS URL to download.
        expected_kind: Expected content kind ("pdf" or "image").
        timeout: Request timeout in seconds.

    Returns:
        LoadedSource with source_type="url" and temp file path.

    Raises:
        ValueError: If URL is invalid, content is empty, or doesn't match expected kind.

    Note:
        The caller is responsible for deleting the temporary file after use.
        The file is created with delete=False to ensure it persists after
        the function returns and the context manager exits.
    """
    validate_url(url)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            content_type = response.headers.get_content_type()
            content = response.read()
    except HTTPError as exc:
        raise ValueError(f"HTTP error downloading URL: {url}") from exc
    except URLError as exc:
        raise ValueError(f"URL error downloading: {url}") from exc
    except TimeoutError as exc:
        raise ValueError(f"Timeout downloading URL: {url}") from exc

    if not content:
        raise ValueError("Downloaded content is empty")

    suffix = ".pdf" if expected_kind == "pdf" else mimetypes.guess_extension(content_type or "") or ".bin"
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        handle.write(content)
        handle.flush()
    finally:
        handle.close()

    path = Path(handle.name)
    if expected_kind == "pdf" and not (content_type or "").startswith("application/pdf"):
        raise ValueError("URL did not resolve to PDF content")
    if expected_kind == "image" and not (content_type or "").startswith("image/"):
        raise ValueError("URL did not resolve to image content")

    return LoadedSource(source_type="url", local_path=path, mime_type=content_type)


def materialize_base64_source(value: str, expected_kind: str) -> LoadedSource:
    """Decode a base64 payload and save to a temporary file.

    Args:
        value: Base64 encoded string, optionally as a data URL.
        expected_kind: Expected content kind ("pdf" or "image").

    Returns:
        LoadedSource with source_type="base64" and temp file path.

    Raises:
        ValueError: If base64 is invalid or doesn't match expected kind.

    Note:
        The caller is responsible for deleting the temporary file after use.
        The file is created with delete=False to ensure it persists after
        the function returns and the context manager exits.
    """
    payload = parse_base64_payload(value)
    if expected_kind == "pdf" and payload.mime_type not in {None, "application/pdf"}:
        raise ValueError("Base64 payload is not a PDF")
    if expected_kind == "image" and payload.mime_type is not None and not payload.mime_type.startswith("image/"):
        raise ValueError("Base64 payload is not an image")

    suffix = ".pdf" if expected_kind == "pdf" else mimetypes.guess_extension(payload.mime_type or "image/png") or ".png"
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        handle.write(payload.content)
        handle.flush()
    finally:
        handle.close()
    return LoadedSource(source_type="base64", local_path=Path(handle.name), mime_type=payload.mime_type)
