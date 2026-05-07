from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SourceType(str, Enum):
    PATH = "path"
    URL = "url"
    BASE64 = "base64"


class AnalysisWarning(BaseModel):
    code: str
    message: str


class AnalysisError(BaseModel):
    code: str
    message: str
    page: int | None = None


class PageResult(BaseModel):
    page: int
    content: str


class PdfAnalysisResult(BaseModel):
    input_type: Literal["pdf"] = "pdf"
    source_type: SourceType
    model: str
    prompt: str
    results: list[PageResult]
    combined_content: str
    warnings: list[AnalysisWarning] = Field(default_factory=list)
    errors: list[AnalysisError] = Field(default_factory=list)


class ImageAnalysisResult(BaseModel):
    input_type: Literal["image"] = "image"
    source_type: SourceType
    model: str
    prompt: str
    content: str
    warnings: list[AnalysisWarning] = Field(default_factory=list)
    errors: list[AnalysisError] = Field(default_factory=list)


def _count_sources(*values: Optional[str]) -> int:
    return sum(1 for value in values if value)


def _validate_exactly_one_source(count: int) -> None:
    if count != 1:
        raise ValueError("Exactly one source input must be provided")


class AnalyzePdfInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    prompt: str = Field(..., min_length=1)
    pdf_path: Optional[str] = None
    pdf_url: Optional[str] = None
    pdf_base64: Optional[str] = None
    pages: Optional[str] = None
    model: str = Field(default="qwen-3.6", min_length=1)
    dpi: int = Field(default=200, ge=72, le=600)
    max_tokens: int = Field(default=4096, ge=1, le=32768)

    @model_validator(mode="after")
    def validate_single_source(self) -> "AnalyzePdfInput":
        _validate_exactly_one_source(
            _count_sources(self.pdf_path, self.pdf_url, self.pdf_base64)
        )
        return self


class AnalyzeImageInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    prompt: str = Field(..., min_length=1)
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    model: str = Field(default="qwen-3.6", min_length=1)
    max_tokens: int = Field(default=4096, ge=1, le=32768)

    @model_validator(mode="after")
    def validate_single_source(self) -> "AnalyzeImageInput":
        _validate_exactly_one_source(
            _count_sources(self.image_path, self.image_url, self.image_base64)
        )
        return self
