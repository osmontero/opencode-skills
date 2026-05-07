"""Tests for ThreatWinds Vision MCP source loader module."""

import base64
from pathlib import Path

import pytest

from skills.mcp_builder.examples.threatwinds_vision_mcp.source_loader import (
    DecodedPayload,
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


class TestDownloadUrlSource:
    """Tests for download_url_source function."""

    @pytest.mark.skip(reason="Requires network access")
    def test_download_url_source(self) -> None:
        """Should download URL and create temp file."""
        # This would require network access, skip for now
        pass


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
