"""Comprehensive tests for ThreatWinds Vision MCP models."""

import pytest
from pydantic import ValidationError

from threatwinds_vision_mcp.models import (
    AnalyzeImageInput,
    AnalyzePdfInput,
    AnalysisError,
    AnalysisWarning,
    ImageAnalysisResult,
    PageResult,
    PdfAnalysisResult,
    SourceType,
)


class TestAnalyzeImageInputValidationErrors:
    """Tests for AnalyzeImageInput validation errors."""

    def test_no_source_provided_raises_error(self) -> None:
        """Test that providing no source raises a validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeImageInput(prompt="Analyze this image")

        assert "Exactly one source input must be provided" in str(exc_info.value)

    def test_multiple_sources_raises_error(self) -> None:
        """Test that providing multiple sources raises a validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeImageInput(
                prompt="Analyze this image",
                image_path="/path/to/image.png",
                image_url="https://example.com/image.png",
            )

        assert "Exactly one source input must be provided" in str(exc_info.value)

    def test_all_three_sources_raises_error(self) -> None:
        """Test that providing all three sources raises a validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeImageInput(
                prompt="Analyze this image",
                image_path="/path/to/image.png",
                image_url="https://example.com/image.png",
                image_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ",
            )

        assert "Exactly one source input must be provided" in str(exc_info.value)


class TestAnalyzePdfInputValidationErrors:
    """Tests for AnalyzePdfInput validation errors."""

    def test_no_source_provided_raises_error(self) -> None:
        """Test that providing no source raises a validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(prompt="Analyze this PDF")

        assert "Exactly one source input must be provided" in str(exc_info.value)

    def test_multiple_sources_raises_error(self) -> None:
        """Test that providing multiple sources raises a validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(
                prompt="Analyze this PDF",
                pdf_path="/path/to/document.pdf",
                pdf_url="https://example.com/document.pdf",
            )

        assert "Exactly one source input must be provided" in str(exc_info.value)

    def test_all_three_sources_raises_error(self) -> None:
        """Test that providing all three sources raises a validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(
                prompt="Analyze this PDF",
                pdf_path="/path/to/document.pdf",
                pdf_url="https://example.com/document.pdf",
                pdf_base64="JVBERi0xLjQK",
            )

        assert "Exactly one source input must be provided" in str(exc_info.value)


class TestAnalyzeImageInputFieldConstraints:
    """Tests for AnalyzeImageInput field constraints."""

    def test_prompt_min_length_enforced(self) -> None:
        """Test that prompt requires at least one character."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeImageInput(
                prompt="",
                image_path="/path/to/image.png",
            )
        assert "string" in str(exc_info.value).lower() or "length" in str(exc_info.value).lower()

    def test_prompt_whitespace_stripped(self) -> None:
        """Test that whitespace is stripped from prompt."""
        result = AnalyzeImageInput(
            prompt="  analyze this  ",
            image_path="/path/to/image.png",
        )
        assert result.prompt == "analyze this"

    def test_max_tokens_minimum_bound(self) -> None:
        """Test that max_tokens cannot be less than 1."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeImageInput(
                prompt="Analyze this",
                image_path="/path/to/image.png",
                max_tokens=0,
            )
        assert "max_tokens" in str(exc_info.value).lower()

    def test_max_tokens_maximum_bound(self) -> None:
        """Test that max_tokens cannot be more than 32768."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeImageInput(
                prompt="Analyze this",
                image_path="/path/to/image.png",
                max_tokens=32769,
            )
        assert "max_tokens" in str(exc_info.value).lower()

    def test_max_tokens_valid_bounds(self) -> None:
        """Test that max_tokens accepts values at boundary limits."""
        result_min = AnalyzeImageInput(
            prompt="Analyze this",
            image_path="/path/to/image.png",
            max_tokens=1,
        )
        assert result_min.max_tokens == 1

        result_max = AnalyzeImageInput(
            prompt="Analyze this",
            image_path="/path/to/image.png",
            max_tokens=32768,
        )
        assert result_max.max_tokens == 32768

    def test_model_min_length_enforced(self) -> None:
        """Test that model requires at least one character."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeImageInput(
                prompt="Analyze this",
                image_path="/path/to/image.png",
                model="",
            )
        assert "model" in str(exc_info.value).lower()

    def test_image_url_whitespace_stripped(self) -> None:
        """Test that whitespace is stripped from image_url."""
        result = AnalyzeImageInput(
            prompt="Analyze this",
            image_url="  https://example.com/image.png  ",
        )
        assert result.image_url == "https://example.com/image.png"


class TestAnalyzePdfInputFieldConstraints:
    """Tests for AnalyzePdfInput field constraints."""

    def test_prompt_min_length_enforced(self) -> None:
        """Test that prompt requires at least one character."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(
                prompt="",
                pdf_path="/path/to/document.pdf",
            )
        assert "string" in str(exc_info.value).lower() or "length" in str(exc_info.value).lower()

    def test_prompt_whitespace_stripped(self) -> None:
        """Test that whitespace is stripped from prompt."""
        result = AnalyzePdfInput(
            prompt="  analyze this  ",
            pdf_path="/path/to/document.pdf",
        )
        assert result.prompt == "analyze this"

    def test_dpi_minimum_bound(self) -> None:
        """Test that dpi cannot be less than 72."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(
                prompt="Analyze this",
                pdf_path="/path/to/document.pdf",
                dpi=71,
            )
        assert "dpi" in str(exc_info.value).lower()

    def test_dpi_maximum_bound(self) -> None:
        """Test that dpi cannot be more than 600."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(
                prompt="Analyze this",
                pdf_path="/path/to/document.pdf",
                dpi=601,
            )
        assert "dpi" in str(exc_info.value).lower()

    def test_dpi_valid_bounds(self) -> None:
        """Test that dpi accepts values at boundary limits."""
        result_min = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_path="/path/to/document.pdf",
            dpi=72,
        )
        assert result_min.dpi == 72

        result_max = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_path="/path/to/document.pdf",
            dpi=600,
        )
        assert result_max.dpi == 600

    def test_max_tokens_minimum_bound(self) -> None:
        """Test that max_tokens cannot be less than 1."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(
                prompt="Analyze this",
                pdf_path="/path/to/document.pdf",
                max_tokens=0,
            )
        assert "max_tokens" in str(exc_info.value).lower()

    def test_max_tokens_maximum_bound(self) -> None:
        """Test that max_tokens cannot be more than 32768."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(
                prompt="Analyze this",
                pdf_path="/path/to/document.pdf",
                max_tokens=32769,
            )
        assert "max_tokens" in str(exc_info.value).lower()

    def test_max_tokens_valid_bounds(self) -> None:
        """Test that max_tokens accepts values at boundary limits."""
        result_min = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_path="/path/to/document.pdf",
            max_tokens=1,
        )
        assert result_min.max_tokens == 1

        result_max = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_path="/path/to/document.pdf",
            max_tokens=32768,
        )
        assert result_max.max_tokens == 32768

    def test_model_min_length_enforced(self) -> None:
        """Test that model requires at least one character."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(
                prompt="Analyze this",
                pdf_path="/path/to/document.pdf",
                model="",
            )
        assert "model" in str(exc_info.value).lower()

    def test_pdf_url_whitespace_stripped(self) -> None:
        """Test that whitespace is stripped from pdf_url."""
        result = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_url="  https://example.com/document.pdf  ",
        )
        assert result.pdf_url == "https://example.com/document.pdf"


class TestExtraForbidBehavior:
    """Tests for extra='forbid' behavior in input models."""

    def test_analyze_image_input_forbids_extra_fields(self) -> None:
        """Test that AnalyzeImageInput rejects unknown fields."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeImageInput(
                prompt="Analyze this",
                image_path="/path/to/image.png",
                unknown_field="value",
            )
        assert "unknown_field" in str(exc_info.value).lower()

    def test_analyze_pdf_input_forbids_extra_fields(self) -> None:
        """Test that AnalyzePdfInput rejects unknown fields."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(
                prompt="Analyze this",
                pdf_path="/path/to/document.pdf",
                unknown_field="value",
            )
        assert "unknown_field" in str(exc_info.value).lower()

    def test_analyze_pdf_input_forbids_multiple_extra_fields(self) -> None:
        """Test that AnalyzePdfInput rejects multiple unknown fields."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzePdfInput(
                prompt="Analyze this",
                pdf_path="/path/to/document.pdf",
                extra1="value1",
                extra2="value2",
            )
        error_str = str(exc_info.value).lower()
        assert "extra1" in error_str or "extra2" in error_str


class TestAnalysisWarning:
    """Tests for AnalysisWarning model."""

    def test_analysis_warning_required_fields(self) -> None:
        """Test that AnalysisWarning requires code and message."""
        warning = AnalysisWarning(code="WARN001", message="Sample warning")
        assert warning.code == "WARN001"
        assert warning.message == "Sample warning"

    def test_analysis_warning_with_empty_message(self) -> None:
        """Test that AnalysisWarning allows empty message."""
        warning = AnalysisWarning(code="WARN001", message="")
        assert warning.message == ""


class TestAnalysisError:
    """Tests for AnalysisError model."""

    def test_analysis_error_required_fields(self) -> None:
        """Test that AnalysisError requires code and message."""
        error = AnalysisError(code="ERR001", message="Sample error")
        assert error.code == "ERR001"
        assert error.message == "Sample error"

    def test_analysis_error_page_optional(self) -> None:
        """Test that page is optional in AnalysisError."""
        error_no_page = AnalysisError(code="ERR001", message="Sample error")
        assert error_no_page.page is None

    def test_analysis_error_page_set(self) -> None:
        """Test that page can be set in AnalysisError."""
        error_with_page = AnalysisError(code="ERR001", message="Sample error", page=5)
        assert error_with_page.page == 5

    def test_analysis_error_page_zero(self) -> None:
        """Test that page can be zero in AnalysisError."""
        error_page_zero = AnalysisError(code="ERR001", message="Sample error", page=0)
        assert error_page_zero.page == 0


class TestPageResult:
    """Tests for PageResult model."""

    def test_page_result_required_fields(self) -> None:
        """Test that PageResult requires page and content."""
        result = PageResult(page=1, content="Sample content")
        assert result.page == 1
        assert result.content == "Sample content"

    def test_page_result_with_empty_content(self) -> None:
        """Test that PageResult allows empty content."""
        result = PageResult(page=1, content="")
        assert result.content == ""

    def test_page_result_with_zero_page(self) -> None:
        """Test that PageResult allows zero page number."""
        result = PageResult(page=0, content="Content")
        assert result.page == 0


class TestPdfAnalysisResult:
    """Tests for PdfAnalysisResult model."""

    def test_pdf_analysis_result_required_fields(self) -> None:
        """Test that PdfAnalysisResult requires source_type, model, prompt, results, combined_content."""
        result = PdfAnalysisResult(
            source_type=SourceType.PATH,
            model="qwen-3.6",
            prompt="Analyze this PDF",
            results=[PageResult(page=1, content="Page content")],
            combined_content="Combined page content",
        )
        assert result.input_type == "pdf"
        assert result.source_type == SourceType.PATH
        assert result.model == "qwen-3.6"
        assert result.prompt == "Analyze this PDF"
        assert len(result.results) == 1
        assert result.combined_content == "Combined page content"

    def test_pdf_analysis_result_waits_defaults_to_empty_list(self) -> None:
        """Test that warnings defaults to empty list."""
        result = PdfAnalysisResult(
            source_type=SourceType.PATH,
            model="qwen-3.6",
            prompt="Analyze this PDF",
            results=[],
            combined_content="",
        )
        assert result.warnings == []

    def test_pdf_analysis_result_errors_defaults_to_empty_list(self) -> None:
        """Test that errors defaults to empty list."""
        result = PdfAnalysisResult(
            source_type=SourceType.PATH,
            model="qwen-3.6",
            prompt="Analyze this PDF",
            results=[],
            combined_content="",
        )
        assert result.errors == []

    def test_pdf_analysis_result_with_warnings(self) -> None:
        """Test that PdfAnalysisResult can have warnings."""
        result = PdfAnalysisResult(
            source_type=SourceType.PATH,
            model="qwen-3.6",
            prompt="Analyze this PDF",
            results=[],
            combined_content="",
            warnings=[AnalysisWarning(code="WARN001", message="Sample warning")],
        )
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "WARN001"

    def test_pdf_analysis_result_with_errors(self) -> None:
        """Test that PdfAnalysisResult can have errors."""
        result = PdfAnalysisResult(
            source_type=SourceType.PATH,
            model="qwen-3.6",
            prompt="Analyze this PDF",
            results=[],
            combined_content="",
            errors=[AnalysisError(code="ERR001", message="Sample error", page=1)],
        )
        assert len(result.errors) == 1
        assert result.errors[0].page == 1

    def test_pdf_analysis_result_input_type_is_pdf(self) -> None:
        """Test that input_type is automatically set to 'pdf'."""
        result = PdfAnalysisResult(
            source_type=SourceType.URL,
            model="qwen-3.6",
            prompt="Analyze this PDF",
            results=[],
            combined_content="",
        )
        assert result.input_type == "pdf"


class TestImageAnalysisResult:
    """Tests for ImageAnalysisResult model."""

    def test_image_analysis_result_required_fields(self) -> None:
        """Test that ImageAnalysisResult requires source_type, model, prompt, content."""
        result = ImageAnalysisResult(
            source_type=SourceType.PATH,
            model="qwen-3.6",
            prompt="Analyze this image",
            content="Image analysis content",
        )
        assert result.input_type == "image"
        assert result.source_type == SourceType.PATH
        assert result.model == "qwen-3.6"
        assert result.prompt == "Analyze this image"
        assert result.content == "Image analysis content"

    def test_image_analysis_result_warnings_defaults_to_empty_list(self) -> None:
        """Test that warnings defaults to empty list."""
        result = ImageAnalysisResult(
            source_type=SourceType.PATH,
            model="qwen-3.6",
            prompt="Analyze this image",
            content="Content",
        )
        assert result.warnings == []

    def test_image_analysis_result_errors_defaults_to_empty_list(self) -> None:
        """Test that errors defaults to empty list."""
        result = ImageAnalysisResult(
            source_type=SourceType.PATH,
            model="qwen-3.6",
            prompt="Analyze this image",
            content="Content",
        )
        assert result.errors == []

    def test_image_analysis_result_with_warnings(self) -> None:
        """Test that ImageAnalysisResult can have warnings."""
        result = ImageAnalysisResult(
            source_type=SourceType.PATH,
            model="qwen-3.6",
            prompt="Analyze this image",
            content="Content",
            warnings=[AnalysisWarning(code="WARN001", message="Sample warning")],
        )
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "WARN001"

    def test_image_analysis_result_with_errors(self) -> None:
        """Test that ImageAnalysisResult can have errors."""
        result = ImageAnalysisResult(
            source_type=SourceType.PATH,
            model="qwen-3.6",
            prompt="Analyze this image",
            content="Content",
            errors=[AnalysisError(code="ERR001", message="Sample error")],
        )
        assert len(result.errors) == 1
        assert result.errors[0].code == "ERR001"

    def test_image_analysis_result_input_type_is_image(self) -> None:
        """Test that input_type is automatically set to 'image'."""
        result = ImageAnalysisResult(
            source_type=SourceType.BASE64,
            model="qwen-3.6",
            prompt="Analyze this image",
            content="Content",
        )
        assert result.input_type == "image"


class TestSourceType:
    """Tests for SourceType enum."""

    def test_source_type_path(self) -> None:
        """Test SOURCE_TYPE.PATH value."""
        assert SourceType.PATH == "path"

    def test_source_type_url(self) -> None:
        """Test SOURCE_TYPE.URL value."""
        assert SourceType.URL == "url"

    def test_source_type_base64(self) -> None:
        """Test SOURCE_TYPE.BASE64 value."""
        assert SourceType.BASE64 == "base64"


class TestAnalyzeImageInputValidCreation:
    """Tests for valid AnalyzeImageInput creation."""

    def test_create_with_path(self) -> None:
        """Test creating AnalyzeImageInput with image_path."""
        result = AnalyzeImageInput(
            prompt="Analyze this",
            image_path="/path/to/image.png",
        )
        assert result.image_path == "/path/to/image.png"
        assert result.image_url is None
        assert result.image_base64 is None

    def test_create_with_url(self) -> None:
        """Test creating AnalyzeImageInput with image_url."""
        result = AnalyzeImageInput(
            prompt="Analyze this",
            image_url="https://example.com/image.png",
        )
        assert result.image_url == "https://example.com/image.png"
        assert result.image_path is None
        assert result.image_base64 is None

    def test_create_with_base64(self) -> None:
        """Test creating AnalyzeImageInput with image_base64."""
        result = AnalyzeImageInput(
            prompt="Analyze this",
            image_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ",
        )
        assert result.image_base64 == "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
        assert result.image_path is None
        assert result.image_url is None

    def test_default_model(self) -> None:
        """Test that model defaults to qwen-3.6."""
        result = AnalyzeImageInput(
            prompt="Analyze this",
            image_path="/path/to/image.png",
        )
        assert result.model == "qwen-3.6"

    def test_default_max_tokens(self) -> None:
        """Test that max_tokens defaults to 4096."""
        result = AnalyzeImageInput(
            prompt="Analyze this",
            image_path="/path/to/image.png",
        )
        assert result.max_tokens == 4096


class TestAnalyzePdfInputValidCreation:
    """Tests for valid AnalyzePdfInput creation."""

    def test_create_with_path(self) -> None:
        """Test creating AnalyzePdfInput with pdf_path."""
        result = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_path="/path/to/document.pdf",
        )
        assert result.pdf_path == "/path/to/document.pdf"
        assert result.pdf_url is None
        assert result.pdf_base64 is None

    def test_create_with_url(self) -> None:
        """Test creating AnalyzePdfInput with pdf_url."""
        result = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_url="https://example.com/document.pdf",
        )
        assert result.pdf_url == "https://example.com/document.pdf"
        assert result.pdf_path is None
        assert result.pdf_base64 is None

    def test_create_with_base64(self) -> None:
        """Test creating AnalyzePdfInput with pdf_base64."""
        result = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_base64="JVBERi0xLjQK",
        )
        assert result.pdf_base64 == "JVBERi0xLjQK"
        assert result.pdf_path is None
        assert result.pdf_url is None

    def test_default_model(self) -> None:
        """Test that model defaults to qwen-3.6."""
        result = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_path="/path/to/document.pdf",
        )
        assert result.model == "qwen-3.6"

    def test_default_dpi(self) -> None:
        """Test that dpi defaults to 200."""
        result = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_path="/path/to/document.pdf",
        )
        assert result.dpi == 200

    def test_default_max_tokens(self) -> None:
        """Test that max_tokens defaults to 4096."""
        result = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_path="/path/to/document.pdf",
        )
        assert result.max_tokens == 4096

    def test_pages_optional(self) -> None:
        """Test that pages is optional."""
        result = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_path="/path/to/document.pdf",
        )
        assert result.pages is None

    def test_pages_set(self) -> None:
        """Test that pages can be set."""
        result = AnalyzePdfInput(
            prompt="Analyze this",
            pdf_path="/path/to/document.pdf",
            pages="1-5",
        )
        assert result.pages == "1-5"
