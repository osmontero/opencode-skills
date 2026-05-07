"""ThreatWinds vision client for sending images to the ThreatWinds API for analysis."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
from pathlib import Path
import urllib.error
import urllib.request


API_BASE = "https://apis.threatwinds.com/api/ai/v1"


def image_file_to_data_url(image_path: Path) -> str:
    """Encode an image file as a base64 data URL.

    Args:
        image_path: Path to the image file.

    Returns:
        A data URL string suitable for inline embedding in API payloads.
    """
    mime_type, _ = mimetypes.guess_type(image_path.name)
    if not mime_type:
        mime_type = "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def build_headers(api_key: str, api_secret: str | None) -> dict[str, str]:
    """Construct authentication headers for the ThreatWinds API.

    Args:
        api_key: The API key.
        api_secret: Optional API secret. When provided, uses api-key/api-secret
            headers; otherwise uses Bearer token authentication.

    Returns:
        Dictionary of HTTP headers.
    """
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    if api_secret:
        headers["api-key"] = api_key
        headers["api-secret"] = api_secret
    else:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def build_chat_payload(model: str, prompt: str, data_url: str, max_tokens: int) -> dict[str, object]:
    """Build a chat completion payload for a vision analysis request.

    Args:
        model: The model identifier (e.g. "qwen-3.6").
        prompt: The text prompt to send alongside the image.
        data_url: Base64 data URL of the image.
        max_tokens: Maximum completion tokens.

    Returns:
        Dictionary matching the ThreatWinds chat completions API schema.
    """
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                ],
            }
        ],
        "max_completion_tokens": max_tokens,
    }


def request_vision_analysis(
    image_path: Path,
    prompt: str,
    model: str,
    max_tokens: int,
    api_key: str | None = None,
    api_secret: str | None = None,
) -> str:
    """Send an image to the ThreatWinds API for vision analysis.

    Args:
        image_path: Path to the image file to analyze.
        prompt: Analysis prompt to send with the image.
        model: Model identifier.
        max_tokens: Maximum completion tokens.
        api_key: Optional API key (falls back to THREATWINDS_API_KEY env var).
        api_secret: Optional API secret (falls back to THREATWINDS_API_SECRET env var).

    Returns:
        The text content of the model's response.

    Raises:
        ValueError: If no API key is available.
        RuntimeError: If the API request fails or response is malformed.
    """
    resolved_api_key = api_key or os.environ.get("THREATWINDS_API_KEY")
    resolved_api_secret = api_secret if api_secret is not None else os.environ.get("THREATWINDS_API_SECRET")

    if not resolved_api_key:
        raise ValueError("THREATWINDS_API_KEY is required")

    payload = build_chat_payload(
        model=model,
        prompt=prompt,
        data_url=image_file_to_data_url(image_path),
        max_tokens=max_tokens,
    )
    request = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=build_headers(resolved_api_key, resolved_api_secret),
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            decoded = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ThreatWinds API error {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"ThreatWinds request failed: {exc}") from exc

    try:
        return decoded["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("ThreatWinds response did not contain the expected message content") from exc
