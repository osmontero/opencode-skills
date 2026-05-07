from pydantic import ValidationError

from mcp_servers.threatwinds_vision.models import (
    AnalyzePdfInput,
    AnalyzeImageInput,
)


def test_pdf_input_requires_exactly_one_source() -> None:
    try:
        AnalyzePdfInput(prompt="extract text")
    except ValidationError as exc:
        assert "exactly one" in str(exc).lower()
    else:
        raise AssertionError("expected validation error")


def test_pdf_input_rejects_multiple_sources() -> None:
    try:
        AnalyzePdfInput(
            prompt="extract text",
            pdf_path="invoice.pdf",
            pdf_url="https://example.com/invoice.pdf",
        )
    except ValidationError as exc:
        assert "exactly one" in str(exc).lower()
    else:
        raise AssertionError("expected validation error")


def test_image_input_accepts_one_source() -> None:
    params = AnalyzeImageInput(
        prompt="describe image",
        image_path="image.png",
    )
    assert params.image_path == "image.png"
    assert params.model == "qwen-3.6"
