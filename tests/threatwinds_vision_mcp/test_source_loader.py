"""Tests for ThreatWinds Vision MCP source loader module."""

import base64
from pathlib import Path
from unittest.mock import patch

import pytest

from skills.mcp_builder.examples.threatwinds_vision_mcp.source_loader import (
    DecodedPayload,
    DEFAULT_TIMEOUT,
    LoadedSource,
    download_url_source,
    load_path_source,
    materialize_base64_source,
    parse_base64_payload,
    validate_url,
)


class TestValidateUrl:
    """Tests for validate_url function."""

    def test_validate_url_accepts_https(self) -> None:
        """HTTPS URLs should be accepted."""
        assert validate_url("https://example.com/file.pdf") == "https://example.com/file.pdf"

    def test_validate_url_accepts_http(self) -> None:
        """HTTP URLs should be accepted."""
        assert validate_url("http://example.com/file.pdf") == "http://example.com/file.pdf"

    def test_validate_url_rejects_file_scheme(self) -> None:
        """File:// URLs should be rejected."""
        with pytest.raises(ValueError, match="Only http and https"):
            validate_url("file:///path/to/file.pdf")

    def test_validate_url_rejects_ftp(self) -> None:
        """FTP URLs should be rejected."""
        with pytest.raises(ValueError, match="Only http and https"):
            validate_url("ftp://example.com/file.pdf")

    def test_validate_url_rejects_missing_netloc(self) -> None:
        """URL with scheme but no netloc should be rejected."""
        with pytest.raises(ValueError, match="network location"):
            validate_url("https://")


class TestLoadedSource:
    """Tests for LoadedSource dataclass."""

    def test_loaded_source_fields(self, tmp_path: Path) -> None:
        """Verify LoadedSource fields are set correctly."""
        test_path = tmp_path / "test.pdf"
        test_path.write_bytes(b"%PDF-1.4")
        source = LoadedSource(
            source_type="path",
            local_path=test_path,
            mime_type="application/pdf"
        )
        assert source.source_type == "path"
        assert source.local_path == test_path
        assert source.mime_type == "application/pdf"

    def test_loaded_source_url_type(self, tmp_path: Path) -> None:
        """Verify LoadedSource with URL source type."""
        test_path = tmp_path / "downloaded.pdf"
        test_path.write_bytes(b"%PDF-1.4")
        source = LoadedSource(
            source_type="url",
            local_path=test_path,
            mime_type="application/pdf"
        )
        assert source.source_type == "url"

    def test_loaded_source_base64_type(self, tmp_path: Path) -> None:
        """Verify LoadedSource with base64 source type."""
        test_path = tmp_path / "decoded.png"
        test_path.write_bytes(b"image data")
        source = LoadedSource(
            source_type="base64",
            local_path=test_path,
            mime_type="image/png"
        )
        assert source.source_type == "base64"


class TestParseBase64Payload:
    """Tests for parse_base64_payload function."""

    def test_parse_base64_payload_supports_data_url(self) -> None:
        """Data URLs with MIME type should be parsed correctly."""
        raw = base64.b64encode(b"hello").decode("ascii")
        payload = parse_base64_payload(f"data:image/png;base64,{raw}")
        assert payload.content == b"hello"
        assert payload.mime_type == "image/png"

    def test_parse_base64_payload_raw_base64(self) -> None:
        """Raw base64 without data URL prefix should work."""
        raw = base64.b64encode(b"test content").decode("ascii")
        payload = parse_base64_payload(raw)
        assert payload.content == b"test content"
        assert payload.mime_type is None

    def test_parse_base64_payload_invalid_base64(self) -> None:
        """Invalid base64 should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid base64"):
            parse_base64_payload("not-valid-base64!!!")

    def test_parse_base64_payload_empty(self) -> None:
        """Empty base64 should raise ValueError."""
        with pytest.raises(ValueError, match="empty content"):
            parse_base64_payload("")

    def test_parse_base64_payload_data_url_no_mime_type(self) -> None:
        """Data URL with no MIME type (data:;base64,<base64>) should work."""
        raw = base64.b64encode(b"content").decode("ascii")
        # Data URL with empty MIME type: data:;base64,<base64data>
        # header = 'data:;base64', encoded = base64data
        # mime_type = header[5:].split(";", 1)[0] = ';base64'.split(";", 1)[0] = '' -> None
        payload = parse_base64_payload(f"data:;base64,{raw}")
        assert payload.content == b"content"
        assert payload.mime_type is None


class TestLoadPathSource:
    """Tests for load_path_source function."""

    def test_load_path_source_requires_file(self, tmp_path: Path) -> None:
        """Should load files correctly."""
        file_path = tmp_path / "sample.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        source = load_path_source(str(file_path), expected_kind="pdf")
        assert source.source_type == "path"
        assert source.local_path == file_path

    def test_load_path_source_nonexistent(self) -> None:
        """Nonexistent path should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            load_path_source("/nonexistent/file.pdf", expected_kind="pdf")

    def test_load_path_source_is_directory(self, tmp_path: Path) -> None:
        """Directory path should raise ValueError."""
        with pytest.raises(ValueError, match="not a file"):
            load_path_source(str(tmp_path), expected_kind="pdf")

    def test_load_path_source_wrong_kind(self, tmp_path: Path) -> None:
        """Wrong file extension should raise ValueError."""
        txt_file = tmp_path / "sample.txt"
        txt_file.write_text("hello")
        with pytest.raises(ValueError, match="Expected a PDF"):
            load_path_source(str(txt_file), expected_kind="pdf")

    def test_load_path_source_image_wrong_kind(self, tmp_path: Path) -> None:
        """Non-image file with expected_kind='image' should raise ValueError."""
        txt_file = tmp_path / "sample.txt"
        txt_file.write_text("hello")
        with pytest.raises(ValueError, match="Expected an image"):
            load_path_source(str(txt_file), expected_kind="image")


class TestDownloadUrlSource:
    """Tests for download_url_source function."""

    @pytest.mark.skip(reason="Requires network access")
    def test_download_url_source(self) -> None:
        """Should download URL and create temp file."""
        # This would require network access, skip for now
        pass

    def test_download_url_source_http_error(self) -> None:
        """HTTP errors should raise ValueError with URL context."""
        from urllib.error import HTTPError
        from http.client import HTTPMessage

        with patch(
            "skills.mcp_builder.examples.threatwinds_vision_mcp.source_loader.urllib.request.urlopen"
        ) as mock_urlopen:
            mock_urlopen.side_effect = HTTPError(
                url="https://example.com/file.pdf",
                code=404,
                msg="Not Found",
                hdrs=HTTPMessage(),
                fp=None
            )
            with pytest.raises(ValueError, match="HTTP error downloading URL: https://example.com/file.pdf"):
                download_url_source("https://example.com/file.pdf", expected_kind="pdf")

    def test_download_url_source_network_error(self) -> None:
        """Network errors should raise ValueError with URL context."""
        from urllib.error import URLError

        with patch(
            "skills.mcp_builder.examples.threatwinds_vision_mcp.source_loader.urllib.request.urlopen"
        ) as mock_urlopen:
            mock_urlopen.side_effect = URLError("Network unreachable")
            with pytest.raises(ValueError, match="URL error downloading: https://example.com/file.pdf"):
                download_url_source("https://example.com/file.pdf", expected_kind="pdf")

    def test_download_url_source_timeout(self) -> None:
        """Timeout errors should raise ValueError with URL context."""
        with patch(
            "skills.mcp_builder.examples.threatwinds_vision_mcp.source_loader.urllib.request.urlopen"
        ) as mock_urlopen:
            mock_urlopen.side_effect = TimeoutError("Connection timed out")
            with pytest.raises(ValueError, match="Timeout downloading URL: https://example.com/file.pdf"):
                download_url_source("https://example.com/file.pdf", expected_kind="pdf")

    def test_download_url_source_empty_response(self) -> None:
        """Empty response should raise ValueError."""
        from unittest.mock import MagicMock

        mock_handle = MagicMock()
        mock_handle.__enter__ = MagicMock(return_value=mock_handle)
        mock_handle.__exit__ = MagicMock(return_value=False)
        mock_handle.headers.get_content_type = MagicMock(return_value="application/pdf")
        mock_handle.read = MagicMock(return_value=b"")

        with patch(
            "skills.mcp_builder.examples.threatwinds_vision_mcp.source_loader.urllib.request.urlopen"
        ) as mock_urlopen:
            mock_urlopen.return_value = mock_handle
            with pytest.raises(ValueError, match="Downloaded content is empty"):
                download_url_source("https://example.com/file.pdf", expected_kind="pdf")

    def test_download_url_source_invalid_content_type_pdf(self) -> None:
        """Wrong Content-Type for PDF should raise ValueError."""
        from unittest.mock import MagicMock

        mock_handle = MagicMock()
        mock_handle.__enter__ = MagicMock(return_value=mock_handle)
        mock_handle.__exit__ = MagicMock(return_value=False)
        mock_handle.headers.get_content_type = MagicMock(return_value="text/html")
        mock_handle.read = MagicMock(return_value=b"<html>not a pdf</html>")

        with patch(
            "skills.mcp_builder.examples.threatwinds_vision_mcp.source_loader.urllib.request.urlopen"
        ) as mock_urlopen:
            mock_urlopen.return_value = mock_handle
            with pytest.raises(ValueError, match="URL did not resolve to PDF content"):
                download_url_source("https://example.com/file.pdf", expected_kind="pdf")

    def test_download_url_source_invalid_content_type_image(self) -> None:
        """Wrong Content-Type for image should raise ValueError."""
        from unittest.mock import MagicMock

        mock_handle = MagicMock()
        mock_handle.__enter__ = MagicMock(return_value=mock_handle)
        mock_handle.__exit__ = MagicMock(return_value=False)
        mock_handle.headers.get_content_type = MagicMock(return_value="application/pdf")
        mock_handle.read = MagicMock(return_value=b"%PDF-1.4")

        with patch(
            "skills.mcp_builder.examples.threatwinds_vision_mcp.source_loader.urllib.request.urlopen"
        ) as mock_urlopen:
            mock_urlopen.return_value = mock_handle
            with pytest.raises(ValueError, match="URL did not resolve to image content"):
                download_url_source("https://example.com/image.png", expected_kind="image")


class TestMaterializeBase64Source:
    """Tests for materialize_base64_source function."""

    def test_materialize_base64_source_pdf(self) -> None:
        """PDF base64 should create temp file."""
        raw = base64.b64encode(b"%PDF-1.4 test").decode("ascii")
        payload = f"data:application/pdf;base64,{raw}"
        source = materialize_base64_source(payload, expected_kind="pdf")
        assert source.source_type == "base64"
        assert source.local_path.exists()
        assert source.local_path.suffix == ".pdf"
        # Cleanup
        source.local_path.unlink()

    def test_materialize_base64_source_image(self) -> None:
        """Image base64 should create temp file."""
        raw = base64.b64encode(b"fake image content").decode("ascii")
        payload = f"data:image/png;base64,{raw}"
        source = materialize_base64_source(payload, expected_kind="image")
        assert source.source_type == "base64"
        assert source.local_path.exists()
        # Cleanup
        source.local_path.unlink()

    def test_materialize_base64_source_wrong_kind(self) -> None:
        """Wrong kind should raise ValueError."""
        raw = base64.b64encode(b"fake image").decode("ascii")
        payload = f"data:image/png;base64,{raw}"
        with pytest.raises(ValueError, match="not a PDF"):
            materialize_base64_source(payload, expected_kind="pdf")

    def test_materialize_base64_source_image_mismatch(self) -> None:
        """Image base64 with non-image MIME type and expected_kind='image' should raise ValueError."""
        raw = base64.b64encode(b"not an image").decode("ascii")
        payload = f"data:text/plain;base64,{raw}"
        with pytest.raises(ValueError, match="not an image"):
            materialize_base64_source(payload, expected_kind="image")
