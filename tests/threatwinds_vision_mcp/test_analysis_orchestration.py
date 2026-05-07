"""Tests for ThreatWinds Vision MCP analysis orchestration service."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_servers.threatwinds_vision.analysis_service import (
    _resolve_image_source,
    _resolve_pdf_source,
    analyze_image_source,
    analyze_pdf_source,
    combine_page_content,
)
from mcp_servers.threatwinds_vision.models import (
    ImageAnalysisResult,
    PdfAnalysisResult,
)


class TestCombinePageContent:
    """Tests for combine_page_content function."""

    def test_combine_page_content_joins_pages(self) -> None:
        """Multiple page results should be joined with page headers."""
        combined = combine_page_content(
            [(1, "first page"), (2, "second page")]
        )
        assert "=== Page 1 ===" in combined
        assert "first page" in combined
        assert "=== Page 2 ===" in combined
        assert "second page" in combined

    def test_combine_page_content_single_page(self) -> None:
        """Single page should still have a header."""
        combined = combine_page_content([(1, "only page")])
        assert "=== Page 1 ===" in combined
        assert "only page" in combined

    def test_combine_page_content_empty(self) -> None:
        """Empty list should return empty string."""
        combined = combine_page_content([])
        assert combined == ""

    def test_combine_page_content_preserves_order(self) -> None:
        """Pages should appear in the order provided."""
        combined = combine_page_content(
            [(3, "third"), (1, "first"), (2, "second")]
        )
        assert combined.index("third") < combined.index("first")
        assert combined.index("first") < combined.index("second")

    def test_combine_page_content_multiline_content(self) -> None:
        """Multi-line content should be preserved with proper separation."""
        combined = combine_page_content(
            [
                (1, "line1\nline2"),
                (2, "line3\nline4"),
            ]
        )
        # Each page header and content should be separated by newlines
        assert "=== Page 1 ===\nline1\nline2\n=== Page 2 ===\nline3\nline4" == combined


class TestAnalyzeImageSource:
    """Tests for analyze_image_source function."""

    def _make_image_path(self, tmp_path: Path) -> Path:
        img = tmp_path / "test.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\nfake")
        return img

    def test_analyze_image_source_returns_result(self, tmp_path: Path) -> None:
        """Successful analysis should return ImageAnalysisResult."""
        img_path = self._make_image_path(tmp_path)
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_image_source"
        ) as mock_resolve:
            mock_resolve.return_value = (img_path, "path")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.request_vision_analysis"
            ) as mock_vision:
                mock_vision.return_value = "analysis text"
                result = analyze_image_source(
                    image_path=str(img_path),
                    prompt="describe this",
                    model="qwen-3.6",
                    max_tokens=2048,
                )
                assert isinstance(result, ImageAnalysisResult)
                assert result.content == "analysis text"
                assert result.source_type == "path"
                assert result.model == "qwen-3.6"
                assert result.prompt == "describe this"

    def test_analyze_image_source_passes_params_to_vision(
        self, tmp_path: Path
    ) -> None:
        """Vision client should receive correct parameters."""
        img_path = self._make_image_path(tmp_path)
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_image_source"
        ) as mock_resolve:
            mock_resolve.return_value = (img_path, "path")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.request_vision_analysis"
            ) as mock_vision:
                mock_vision.return_value = "result"
                analyze_image_source(
                    image_path=str(img_path),
                    prompt="my prompt",
                    model="gpt-4o",
                    max_tokens=4096,
                )
                mock_vision.assert_called_once_with(
                    image_path=img_path,
                    prompt="my prompt",
                    model="gpt-4o",
                    max_tokens=4096,
                )

    def test_analyze_image_source_from_url(self, tmp_path: Path) -> None:
        """Image source_type should reflect URL origin."""
        img_path = self._make_image_path(tmp_path)
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_image_source"
        ) as mock_resolve:
            mock_resolve.return_value = (img_path, "url")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.request_vision_analysis"
            ) as mock_vision:
                mock_vision.return_value = "url result"
                result = analyze_image_source(
                    image_url="https://example.com/img.png",
                    prompt="test",
                    model="qwen-3.6",
                    max_tokens=1024,
                )
                assert result.source_type == "url"

    def test_analyze_image_source_from_base64(self, tmp_path: Path) -> None:
        """Image source_type should reflect base64 origin."""
        img_path = self._make_image_path(tmp_path)
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_image_source"
        ) as mock_resolve:
            mock_resolve.return_value = (img_path, "base64")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.request_vision_analysis"
            ) as mock_vision:
                mock_vision.return_value = "b64 result"
                result = analyze_image_source(
                    image_base64="data:image/png;base64,abc",
                    prompt="test",
                    model="qwen-3.6",
                    max_tokens=1024,
                )
                assert result.source_type == "base64"

    def test_analyze_image_source_propagates_error(self, tmp_path: Path) -> None:
        """Errors from vision client should propagate."""
        img_path = self._make_image_path(tmp_path)
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_image_source"
        ) as mock_resolve:
            mock_resolve.return_value = (img_path, "path")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.request_vision_analysis"
            ) as mock_vision:
                mock_vision.side_effect = RuntimeError("API error")
                with pytest.raises(RuntimeError, match="API error"):
                    analyze_image_source(
                        image_path=str(img_path),
                        prompt="test",
                        model="qwen-3.6",
                        max_tokens=1024,
                    )


class TestAnalyzePdfSource:
    """Tests for analyze_pdf_source function."""

    def test_analyze_pdf_source_returns_result(self) -> None:
        """Successful analysis should return PdfAnalysisResult."""
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_pdf_source"
        ) as mock_resolve:
            mock_resolve.return_value = (Path("/tmp/doc.pdf"), "path")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.render_pdf_to_images"
            ) as mock_render:
                mock_render.return_value = [
                    MagicMock(page_num=1, image_path=Path("/tmp/p1.png")),
                    MagicMock(page_num=2, image_path=Path("/tmp/p2.png")),
                ]
                with patch(
                    "mcp_servers.threatwinds_vision.analysis_service.request_vision_analysis"
                ) as mock_vision:
                    mock_vision.side_effect = ["page1 analysis", "page2 analysis"]
                    result = analyze_pdf_source(
                        pdf_path="/tmp/doc.pdf",
                        prompt="describe",
                        model="qwen-3.6",
                        max_tokens=2048,
                    )
                    assert isinstance(result, PdfAnalysisResult)
                    assert result.source_type == "path"
                    assert result.model == "qwen-3.6"
                    assert result.prompt == "describe"
                    assert len(result.results) == 2
                    assert result.results[0].page == 1
                    assert result.results[0].content == "page1 analysis"
                    assert result.results[1].page == 2
                    assert result.results[1].content == "page2 analysis"
                    assert "=== Page 1 ===" in result.combined_content

    def test_analyze_pdf_source_passes_dpi_to_render(self) -> None:
        """DPI parameter should be passed to PDF renderer."""
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_pdf_source"
        ) as mock_resolve:
            mock_resolve.return_value = (Path("/tmp/doc.pdf"), "path")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.render_pdf_to_images"
            ) as mock_render:
                mock_render.return_value = []
                analyze_pdf_source(
                    pdf_path="/tmp/doc.pdf",
                    prompt="test",
                    model="qwen-3.6",
                    max_tokens=1024,
                    dpi=300,
                    pages="1-3",
                )
                mock_render.assert_called_once_with(
                    pdf_path=Path("/tmp/doc.pdf"),
                    dpi=300,
                    pages="1-3",
                )

    def test_analyze_pdf_source_partial_page_failure(self) -> None:
        """Failed pages should produce errors but not stop analysis."""
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_pdf_source"
        ) as mock_resolve:
            mock_resolve.return_value = (Path("/tmp/doc.pdf"), "url")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.render_pdf_to_images"
            ) as mock_render:
                mock_render.return_value = [
                    MagicMock(page_num=1, image_path=Path("/tmp/p1.png")),
                    MagicMock(page_num=2, image_path=Path("/tmp/p2.png")),
                ]
                with patch(
                    "mcp_servers.threatwinds_vision.analysis_service.request_vision_analysis"
                ) as mock_vision:
                    # Page 1 succeeds, page 2 fails
                    def vision_side_effect(image_path, prompt, model, max_tokens):
                        if image_path.name == "p1.png":
                            return "page1 ok"
                        raise RuntimeError("page 2 failed")

                    mock_vision.side_effect = vision_side_effect
                    result = analyze_pdf_source(
                        pdf_path="/tmp/doc.pdf",
                        prompt="test",
                        model="qwen-3.6",
                        max_tokens=1024,
                    )
                    # Should have one successful result
                    assert len(result.results) == 1
                    assert result.results[0].page == 1
                    # Should have one error for page 2
                    assert len(result.errors) == 1
                    assert result.errors[0].page == 2
                    assert result.source_type == "url"

    def test_analyze_pdf_source_all_pages_fail(self) -> None:
        """If all pages fail, results should be empty with errors."""
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_pdf_source"
        ) as mock_resolve:
            mock_resolve.return_value = (Path("/tmp/doc.pdf"), "base64")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.render_pdf_to_images"
            ) as mock_render:
                mock_render.return_value = [
                    MagicMock(page_num=1, image_path=Path("/tmp/p1.png")),
                ]
                with patch(
                    "mcp_servers.threatwinds_vision.analysis_service.request_vision_analysis"
                ) as mock_vision:
                    mock_vision.side_effect = RuntimeError("all failed")
                    result = analyze_pdf_source(
                        pdf_path="/tmp/doc.pdf",
                        prompt="test",
                        model="qwen-3.6",
                        max_tokens=1024,
                    )
                    assert len(result.results) == 0
                    assert len(result.errors) == 1
                    assert result.errors[0].page == 1
                    assert result.combined_content == ""

    def test_analyze_pdf_source_from_url(self) -> None:
        """PDF source_type should reflect URL origin."""
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_pdf_source"
        ) as mock_resolve:
            mock_resolve.return_value = (Path("/tmp/doc.pdf"), "url")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.render_pdf_to_images"
            ) as mock_render:
                mock_render.return_value = []
                result = analyze_pdf_source(
                    pdf_url="https://example.com/doc.pdf",
                    prompt="test",
                    model="qwen-3.6",
                    max_tokens=1024,
                )
                assert result.source_type == "url"

    def test_analyze_pdf_source_from_base64(self) -> None:
        """PDF source_type should reflect base64 origin."""
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_pdf_source"
        ) as mock_resolve:
            mock_resolve.return_value = (Path("/tmp/doc.pdf"), "base64")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.render_pdf_to_images"
            ) as mock_render:
                mock_render.return_value = []
                result = analyze_pdf_source(
                    pdf_base64="data:application/pdf;base64,abc",
                    prompt="test",
                    model="qwen-3.6",
                    max_tokens=1024,
                )
                assert result.source_type == "base64"

    def test_analyze_pdf_source_empty_pages(self) -> None:
        """PDF with no rendered pages should return empty results."""
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_pdf_source"
        ) as mock_resolve:
            mock_resolve.return_value = (Path("/tmp/doc.pdf"), "path")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.render_pdf_to_images"
            ) as mock_render:
                mock_render.return_value = []
                result = analyze_pdf_source(
                    pdf_path="/tmp/doc.pdf",
                    prompt="test",
                    model="qwen-3.6",
                    max_tokens=1024,
                )
                assert len(result.results) == 0
                assert result.combined_content == ""

    def test_analyze_pdf_source_propagates_render_error(self) -> None:
        """Errors from PDF rendering should propagate."""
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_pdf_source"
        ) as mock_resolve:
            mock_resolve.return_value = (Path("/tmp/doc.pdf"), "path")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.render_pdf_to_images"
            ) as mock_render:
                mock_render.side_effect = ValueError("Invalid PDF")
                with pytest.raises(ValueError, match="Invalid PDF"):
                    analyze_pdf_source(
                        pdf_path="/tmp/doc.pdf",
                        prompt="test",
                        model="qwen-3.6",
                        max_tokens=1024,
                    )


class TestResolverMutualExclusion:
    """Tests for resolver mutual-exclusion validation."""

    def test_resolve_image_source_no_source_raises(self) -> None:
        """Providing no image source should raise ValueError."""
        with pytest.raises(ValueError, match="No image source provided"):
            _resolve_image_source()

    def test_resolve_image_source_multiple_sources_raises(self) -> None:
        """Providing multiple image sources should raise ValueError."""
        with pytest.raises(ValueError, match="Exactly one image source"):
            _resolve_image_source(
                image_path="/tmp/img.png",
                image_url="https://example.com/img.png",
            )

    def test_resolve_image_source_all_three_sources_raises(self) -> None:
        """Providing all three image sources should raise ValueError."""
        with pytest.raises(ValueError, match="Exactly one image source"):
            _resolve_image_source(
                image_path="/tmp/img.png",
                image_url="https://example.com/img.png",
                image_base64="data:image/png;base64,abc",
            )

    def test_resolve_pdf_source_no_source_raises(self) -> None:
        """Providing no PDF source should raise ValueError."""
        with pytest.raises(ValueError, match="No PDF source provided"):
            _resolve_pdf_source()

    def test_resolve_pdf_source_multiple_sources_raises(self) -> None:
        """Providing multiple PDF sources should raise ValueError."""
        with pytest.raises(ValueError, match="Exactly one PDF source"):
            _resolve_pdf_source(
                pdf_path="/tmp/doc.pdf",
                pdf_url="https://example.com/doc.pdf",
            )

    def test_resolve_pdf_source_all_three_sources_raises(self) -> None:
        """Providing all three PDF sources should raise ValueError."""
        with pytest.raises(ValueError, match="Exactly one PDF source"):
            _resolve_pdf_source(
                pdf_path="/tmp/doc.pdf",
                pdf_url="https://example.com/doc.pdf",
                pdf_base64="data:application/pdf;base64,abc",
            )


class TestPdfPartialFailureWarning:
    """Tests for partial PDF analysis warnings."""

    def test_analyze_pdf_source_partial_failure_has_warning(self) -> None:
        """Partial page failure should produce a partial_pdf_analysis warning."""
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_pdf_source"
        ) as mock_resolve:
            mock_resolve.return_value = (Path("/tmp/doc.pdf"), "path")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.render_pdf_to_images"
            ) as mock_render:
                mock_render.return_value = [
                    MagicMock(page_num=1, image_path=Path("/tmp/p1.png")),
                    MagicMock(page_num=2, image_path=Path("/tmp/p2.png")),
                ]
                with patch(
                    "mcp_servers.threatwinds_vision.analysis_service.request_vision_analysis"
                ) as mock_vision:
                    mock_vision.side_effect = [
                        "page1 ok",
                        RuntimeError("page 2 failed"),
                    ]
                    result = analyze_pdf_source(
                        pdf_path="/tmp/doc.pdf",
                        prompt="test",
                        model="qwen-3.6",
                        max_tokens=1024,
                    )
                    assert len(result.warnings) == 1
                    assert result.warnings[0].code == "partial_pdf_analysis"
                    assert "1 of 2" in result.warnings[0].message

    def test_analyze_pdf_source_no_failure_no_warning(self) -> None:
        """Successful analysis of all pages should have no warnings."""
        with patch(
            "mcp_servers.threatwinds_vision.analysis_service._resolve_pdf_source"
        ) as mock_resolve:
            mock_resolve.return_value = (Path("/tmp/doc.pdf"), "path")
            with patch(
                "mcp_servers.threatwinds_vision.analysis_service.render_pdf_to_images"
            ) as mock_render:
                mock_render.return_value = [
                    MagicMock(page_num=1, image_path=Path("/tmp/p1.png")),
                ]
                with patch(
                    "mcp_servers.threatwinds_vision.analysis_service.request_vision_analysis"
                ) as mock_vision:
                    mock_vision.return_value = "page1 ok"
                    result = analyze_pdf_source(
                        pdf_path="/tmp/doc.pdf",
                        prompt="test",
                        model="qwen-3.6",
                        max_tokens=1024,
                    )
                    assert len(result.warnings) == 0
