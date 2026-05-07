"""Tests for ThreatWinds Vision MCP vision client."""

from __future__ import annotations

import base64
import json
import urllib.error
from pathlib import Path
from types import TracebackType
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from skills.mcp_builder.examples.threatwinds_vision_mcp.vision_client import (
    API_BASE,
    build_chat_payload,
    build_headers,
    image_file_to_data_url,
    request_vision_analysis,
)


class _MockResponse:
    """Mock HTTP response that works as a context manager."""

    def __init__(self, body: str) -> None:
        self._body = body.encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_MockResponse":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass


class TestBuildChatPayload:
    """Tests for build_chat_payload function."""

    def test_build_chat_payload_embeds_prompt_and_image(self) -> None:
        """Payload should embed the prompt as text and image as data URL."""
        payload = build_chat_payload(
            model="qwen-3.6",
            prompt="extract invoice number",
            data_url="data:image/png;base64,abc",
            max_tokens=2048,
        )
        assert payload["model"] == "qwen-3.6"
        assert payload["messages"][0]["content"][0]["text"] == "extract invoice number"
        assert payload["messages"][0]["content"][1]["image_url"]["url"] == "data:image/png;base64,abc"

    def test_build_chat_payload_sets_role_to_user(self) -> None:
        """Message role should be 'user'."""
        payload = build_chat_payload(
            model="qwen-3.6",
            prompt="test",
            data_url="data:image/png;base64,xyz",
            max_tokens=1024,
        )
        assert payload["messages"][0]["role"] == "user"

    def test_build_chat_payload_sets_max_completion_tokens(self) -> None:
        """max_tokens should map to max_completion_tokens."""
        payload = build_chat_payload(
            model="qwen-3.6",
            prompt="test",
            data_url="data:image/png;base64,xyz",
            max_tokens=4096,
        )
        assert payload["max_completion_tokens"] == 4096

    def test_build_chat_payload_sets_image_detail_high(self) -> None:
        """Image detail should be set to 'high'."""
        payload = build_chat_payload(
            model="qwen-3.6",
            prompt="test",
            data_url="data:image/png;base64,xyz",
            max_tokens=1024,
        )
        assert payload["messages"][0]["content"][1]["image_url"]["detail"] == "high"

    def test_build_chat_payload_content_types(self) -> None:
        """Content array should have text and image_url types."""
        payload = build_chat_payload(
            model="qwen-3.6",
            prompt="test",
            data_url="data:image/png;base64,xyz",
            max_tokens=1024,
        )
        content = payload["messages"][0]["content"]
        assert content[0]["type"] == "text"
        assert content[1]["type"] == "image_url"


class TestBuildHeaders:
    """Tests for build_headers function."""

    def test_build_headers_with_secret_uses_api_key_headers(self) -> None:
        """When api_secret is provided, use api-key and api-secret headers."""
        headers = build_headers(api_key="my-key", api_secret="my-secret")
        assert headers["api-key"] == "my-key"
        assert headers["api-secret"] == "my-secret"
        assert "Authorization" not in headers

    def test_build_headers_without_secret_uses_bearer(self) -> None:
        """When api_secret is None, use Bearer authorization."""
        headers = build_headers(api_key="my-key", api_secret=None)
        assert headers["Authorization"] == "Bearer my-key"
        assert "api-key" not in headers
        assert "api-secret" not in headers

    def test_build_headers_with_empty_string_key_uses_bearer(self) -> None:
        """Empty-string api_key should still produce a Bearer header."""
        headers = build_headers(api_key="", api_secret=None)
        assert headers["Authorization"] == "Bearer "
        assert "api-key" not in headers

    def test_build_headers_always_sets_content_type(self) -> None:
        """Content-Type and accept headers should always be present."""
        headers_with = build_headers(api_key="k", api_secret="s")
        headers_without = build_headers(api_key="k", api_secret=None)
        assert headers_with["Content-Type"] == "application/json"
        assert headers_with["accept"] == "application/json"
        assert headers_without["Content-Type"] == "application/json"
        assert headers_without["accept"] == "application/json"


class TestImageFileToDataUrl:
    """Tests for image_file_to_data_url function."""

    def test_image_file_to_data_url_png(self, tmp_path: Path) -> None:
        """PNG file should produce a data URL with image/png MIME type."""
        img = tmp_path / "test.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\nfake")
        result = image_file_to_data_url(img)
        assert result.startswith("data:image/png;base64,")

    def test_image_file_to_data_url_jpg(self, tmp_path: Path) -> None:
        """JPG file should produce a data URL with image/jpeg MIME type."""
        img = tmp_path / "test.jpg"
        img.write_bytes(b"\xff\xd8\xff\xe0fake")
        result = image_file_to_data_url(img)
        assert result.startswith("data:image/jpeg;base64,")

    def test_image_file_to_data_url_unknown_ext_defaults_to_png(self, tmp_path: Path) -> None:
        """Unknown file extension should default to image/png."""
        img = tmp_path / "test.unknown"
        img.write_bytes(b"fake")
        result = image_file_to_data_url(img)
        assert result.startswith("data:image/png;base64,")

    def test_image_file_to_data_url_encodes_content(self, tmp_path: Path) -> None:
        """File content should be base64 encoded in the data URL."""
        img = tmp_path / "test.png"
        content = b"\x00\x01\x02\xff"
        img.write_bytes(content)
        result = image_file_to_data_url(img)
        # Verify the base64 portion decodes back to original content
        encoded_part = result.split(",", 1)[1]
        assert base64.b64decode(encoded_part) == content


class TestRequestVisionAnalysis:
    """Tests for request_vision_analysis function."""

    def test_request_vision_analysis_raises_without_api_key(self, tmp_path: Path) -> None:
        """Should raise ValueError when no API key is provided."""
        img = tmp_path / "test.png"
        img.write_bytes(b"fake")
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="THREATWINDS_API_KEY is required"):
                request_vision_analysis(
                    image_path=img,
                    prompt="test",
                    model="qwen-3.6",
                    max_tokens=1024,
                )

    def test_request_vision_analysis_uses_env_api_key(self, tmp_path: Path) -> None:
        """Should use THREATWINDS_API_KEY from environment."""
        img = tmp_path / "test.png"
        img.write_bytes(b"fake")

        mock_response = _MockResponse(json.dumps({
            "choices": [{"message": {"content": "analysis result"}}]
        }))

        with patch.dict("os.environ", {"THREATWINDS_API_KEY": "env-key"}, clear=True):
            with patch("urllib.request.urlopen", return_value=mock_response):
                result = request_vision_analysis(
                    image_path=img,
                    prompt="test",
                    model="qwen-3.6",
                    max_tokens=1024,
                )
                assert result == "analysis result"

    def test_request_vision_analysis_uses_explicit_api_key(self, tmp_path: Path) -> None:
        """Explicit api_key parameter should override environment."""
        img = tmp_path / "test.png"
        img.write_bytes(b"fake")

        mock_response = _MockResponse(json.dumps({
            "choices": [{"message": {"content": "result"}}]
        }))

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_open:
            request_vision_analysis(
                image_path=img,
                prompt="test",
                model="qwen-3.6",
                max_tokens=1024,
                api_key="explicit-key",
            )
            # Verify the request was made
            mock_open.assert_called_once()
            request = mock_open.call_args[0][0]
            assert request.full_url == f"{API_BASE}/chat/completions"

    def test_request_vision_analysis_http_error(self, tmp_path: Path) -> None:
        """HTTP error should raise RuntimeError with status code and body."""
        img = tmp_path / "test.png"
        img.write_bytes(b"fake")

        http_error = urllib.error.HTTPError(
            url="https://apis.threatwinds.com/api/ai/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=None,  # type: ignore[arg-type]
        )
        http_error.read = MagicMock(return_value=b'{"error":"unauthorized"}')

        with patch.dict("os.environ", {"THREATWINDS_API_KEY": "key"}, clear=True):
            with patch("urllib.request.urlopen", side_effect=http_error):
                with pytest.raises(RuntimeError, match="ThreatWinds API error 401"):
                    request_vision_analysis(
                        image_path=img,
                        prompt="test",
                        model="qwen-3.6",
                        max_tokens=1024,
                    )

    def test_request_vision_analysis_url_error(self, tmp_path: Path) -> None:
        """URL error should raise RuntimeError."""
        img = tmp_path / "test.png"
        img.write_bytes(b"fake")

        url_error = urllib.error.URLError("connection refused")

        with patch.dict("os.environ", {"THREATWINDS_API_KEY": "key"}, clear=True):
            with patch("urllib.request.urlopen", side_effect=url_error):
                with pytest.raises(RuntimeError, match="ThreatWinds request failed"):
                    request_vision_analysis(
                        image_path=img,
                        prompt="test",
                        model="qwen-3.6",
                        max_tokens=1024,
                    )

    def test_request_vision_analysis_bad_response_structure(self, tmp_path: Path) -> None:
        """Malformed response should raise RuntimeError."""
        img = tmp_path / "test.png"
        img.write_bytes(b"fake")

        mock_response = _MockResponse(json.dumps({"error": "bad response"}))

        with patch.dict("os.environ", {"THREATWINDS_API_KEY": "key"}, clear=True):
            with patch("urllib.request.urlopen", return_value=mock_response):
                with pytest.raises(RuntimeError, match="did not contain the expected message content"):
                    request_vision_analysis(
                        image_path=img,
                        prompt="test",
                    model="qwen-3.6",
                    max_tokens=1024,
                )


def test_api_base_constant() -> None:
    """API_BASE should point to the ThreatWinds API."""
    assert API_BASE == "https://apis.threatwinds.com/api/ai/v1"
