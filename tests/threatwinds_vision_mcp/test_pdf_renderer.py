"""Tests for ThreatWinds Vision MCP PDF rendering helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_servers.threatwinds_vision.pdf_renderer import (
    filter_rendered_pages,
    parse_pages,
    RenderedPage,
    render_pdf_to_images,
)


class TestParsePages:
    """Tests for parse_pages function."""

    def test_parse_pages_range(self) -> None:
        """Range notation should expand to set of page numbers."""
        assert parse_pages("1-3") == {1, 2, 3}

    def test_parse_pages_csv(self) -> None:
        """CSV notation should parse to set of page numbers."""
        assert parse_pages("1,3,5") == {1, 3, 5}

    def test_parse_pages_single(self) -> None:
        """Single page number should parse correctly."""
        assert parse_pages("5") == {5}

    def test_parse_pages_mixed(self) -> None:
        """Mixed range and CSV notation should work."""
        assert parse_pages("1-3,5,7-8") == {1, 2, 3, 5, 7, 8}

    def test_parse_pages_whitespace(self) -> None:
        """Whitespace around values should be ignored."""
        assert parse_pages(" 1 , 3 , 5 ") == {1, 3, 5}

    def test_parse_pages_rejects_zero(self) -> None:
        """Page number zero should raise ValueError."""
        with pytest.raises(ValueError, match="positive"):
            parse_pages("0-2")

    def test_parse_pages_rejects_negative(self) -> None:
        """Negative page numbers should raise ValueError."""
        with pytest.raises(ValueError, match="positive"):
            parse_pages("-1,2")

    def test_parse_pages_rejects_empty(self) -> None:
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            parse_pages("")

    def test_parse_pages_rejects_invalid(self) -> None:
        """Non-numeric input should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid page"):
            parse_pages("abc")

    def test_parse_pages_rejects_reverse_range(self) -> None:
        """Reverse range (high-low) should raise ValueError."""
        with pytest.raises(ValueError, match="invalid range"):
            parse_pages("5-3")


class TestFilterRenderedPages:
    """Tests for filter_rendered_pages function."""

    def _make_rendered(self, pages: list[int]) -> list[RenderedPage]:
        return [RenderedPage(page_num=p, image_path=Path(f"page_{p}.png")) for p in pages]

    def test_filter_all_pages(self) -> None:
        """When no pages specified, all rendered pages should be returned."""
        rendered = self._make_rendered([1, 2, 3])
        result = filter_rendered_pages(rendered, pages=None)
        assert len(result) == 3

    def test_filter_specific_pages(self) -> None:
        """Only requested pages should be returned."""
        rendered = self._make_rendered([1, 2, 3, 4])
        result = filter_rendered_pages(rendered, pages="1,3")
        page_nums = {r.page_num for r in result}
        assert page_nums == {1, 3}

    def test_filter_range(self) -> None:
        """Range notation should filter correctly."""
        rendered = self._make_rendered([1, 2, 3, 4, 5])
        result = filter_rendered_pages(rendered, pages="2-4")
        page_nums = {r.page_num for r in result}
        assert page_nums == {2, 3, 4}

    def test_filter_out_of_order(self) -> None:
        """Results should maintain original order from rendered list."""
        rendered = self._make_rendered([1, 2, 3])
        result = filter_rendered_pages(rendered, pages="3,1")
        assert [r.page_num for r in result] == [1, 3]

    def test_filter_missing_pages(self) -> None:
        """Requested pages not in rendered list should be silently skipped."""
        rendered = self._make_rendered([1, 2])
        result = filter_rendered_pages(rendered, pages="1,5")
        assert len(result) == 1
        assert result[0].page_num == 1


class TestRenderPdfToImages:
    """Tests for render_pdf_to_images function."""

    def test_render_pdf_to_images(self) -> None:
        """PDF should render to list of RenderedPage objects."""
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=2)

        mock_page = MagicMock()
        mock_bitmap = MagicMock()
        mock_bitmap.to_pil.return_value.save = MagicMock()

        mock_page.render.return_value = mock_bitmap
        mock_doc.__getitem__.return_value = mock_page

        test_path = Path("/tmp/test.pdf")
        with patch(
            "mcp_servers.threatwinds_vision.pdf_renderer.pypdfium2.PdfDocument"
        ) as mock_pdf:
            with patch.object(Path, "exists", return_value=True):
                mock_pdf.return_value = mock_doc

                rendered = render_pdf_to_images(test_path, dpi=200)

                assert len(rendered) == 2
                assert rendered[0].page_num == 1
                assert rendered[1].page_num == 2
                assert rendered[0].image_path.suffix == ".png"

    def test_render_pdf_to_images_with_pages_filter(self) -> None:
        """Pages filter should limit which pages are rendered."""
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=3)

        mock_page = MagicMock()
        mock_bitmap = MagicMock()
        mock_bitmap.to_pil.return_value.save = MagicMock()

        mock_page.render.return_value = mock_bitmap
        mock_doc.__getitem__.return_value = mock_page

        test_path = Path("/tmp/test.pdf")
        with patch(
            "mcp_servers.threatwinds_vision.pdf_renderer.pypdfium2.PdfDocument"
        ) as mock_pdf:
            with patch.object(Path, "exists", return_value=True):
                mock_pdf.return_value = mock_doc

                rendered = render_pdf_to_images(test_path, pages="1,3", dpi=200)

                assert len(rendered) == 2
                assert rendered[0].page_num == 1
                assert rendered[1].page_num == 3

    def test_render_pdf_to_images_invalid_pdf(self) -> None:
        """Invalid PDF path should raise ValueError."""
        with pytest.raises(ValueError, match="PDF file does not exist"):
            render_pdf_to_images(Path("/tmp/nonexistent.pdf"), dpi=200)

    def test_render_pdf_to_images_creates_png(self) -> None:
        """Rendered images should be saved as PNG files."""
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=1)

        mock_page = MagicMock()
        mock_bitmap = MagicMock()
        mock_bitmap.to_pil.return_value.save = MagicMock()

        mock_page.render.return_value = mock_bitmap
        mock_doc.__getitem__.return_value = mock_page

        test_path = Path("/tmp/test.pdf")
        with patch(
            "mcp_servers.threatwinds_vision.pdf_renderer.pypdfium2.PdfDocument"
        ) as mock_pdf:
            with patch.object(Path, "exists", return_value=True):
                mock_pdf.return_value = mock_doc

                rendered = render_pdf_to_images(test_path, dpi=100)

                # Verify to_pil().save was called (image was written)
                mock_bitmap.to_pil.assert_called_once()
                mock_bitmap.to_pil.return_value.save.assert_called_once()

    def test_render_pdf_to_images_dpi_validation(self) -> None:
        """DPI outside 72-600 range should raise ValueError."""
        test_path = Path("/tmp/test.pdf")
        with patch.object(Path, "exists", return_value=True):
            with pytest.raises(ValueError, match="DPI must be between 72 and 600"):
                render_pdf_to_images(test_path, dpi=71)
            with pytest.raises(ValueError, match="DPI must be between 72 and 600"):
                render_pdf_to_images(test_path, dpi=601)

    def test_render_pdf_to_images_out_of_range_pages(self) -> None:
        """Pages beyond document length should be silently filtered out."""
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=2)

        mock_page = MagicMock()
        mock_bitmap = MagicMock()
        mock_bitmap.to_pil.return_value.save = MagicMock()

        mock_page.render.return_value = mock_bitmap
        mock_doc.__getitem__.return_value = mock_page

        test_path = Path("/tmp/test.pdf")
        with patch(
            "mcp_servers.threatwinds_vision.pdf_renderer.pypdfium2.PdfDocument"
        ) as mock_pdf:
            with patch.object(Path, "exists", return_value=True):
                mock_pdf.return_value = mock_doc

                # Request pages 1, 3, 5 but doc only has 2 pages
                rendered = render_pdf_to_images(test_path, pages="1,3,5", dpi=200)

                assert len(rendered) == 1
                assert rendered[0].page_num == 1
