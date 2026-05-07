# ThreatWinds Vision MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python FastMCP server that analyzes scanned PDFs and images through the ThreatWinds vision API using an arbitrary caller-provided extraction prompt.

**Architecture:** Refactor the existing PDF OCR CLI script into shared Python modules for source loading, PDF rendering, ThreatWinds API access, and orchestration, then expose that functionality through two FastMCP tools: one for PDFs and one for images. Keep the existing CLI entrypoint working by turning it into a thin wrapper around the shared service layer.

**Tech Stack:** Python 3.12, FastMCP (`mcp`), Pydantic, `pypdfium2`, `urllib.request`, existing repo install flow via `install.sh`.

---

## File Structure Map

### Create
- `mcp_servers/threatwinds_vision/README.md` — focused usage/setup docs for the new MCP example server.
- `mcp_servers/threatwinds_vision/server.py` — FastMCP entrypoint exposing `analyze_pdf` and `analyze_image`.
- `mcp_servers/threatwinds_vision/source_loader.py` — normalize local path, URL, and base64 inputs into validated local artifacts.
- `mcp_servers/threatwinds_vision/pdf_renderer.py` — page range parsing and PDF-to-image rendering helpers.
- `mcp_servers/threatwinds_vision/vision_client.py` — ThreatWinds request/response client.
- `mcp_servers/threatwinds_vision/analysis_service.py` — orchestration layer for PDF/image analysis and response aggregation.
- `mcp_servers/threatwinds_vision/models.py` — shared Pydantic request/response models and enums.
- `mcp_servers/threatwinds_vision/__init__.py` — package marker.
- `tests/threatwinds_vision_mcp/test_source_loader.py` — source validation and normalization tests.
- `tests/threatwinds_vision_mcp/test_pdf_renderer.py` — page parsing and PDF rendering edge-case tests.
- `tests/threatwinds_vision_mcp/test_analysis_service.py` — mocked orchestration tests.
- `tests/threatwinds_vision_mcp/test_server_models.py` — tool input model validation tests.

### Modify
- `skills/pdf/scripts/ocr_vision.py` — convert existing CLI into a thin wrapper over shared modules.
- `README.md` — document the new MCP server example and ThreatWinds use case.
- `.opencode/opencode.json` — optionally register the local MCP server if this repo keeps runnable examples wired into local config.
- `AGENTS.md` — only if needed to note a non-obvious operational detail discovered during implementation.

---

### Task 1: Create shared input and output models

**Files:**
- Create: `mcp_servers/threatwinds_vision/models.py`
- Test: `tests/threatwinds_vision_mcp/test_server_models.py`

- [ ] **Step 1: Write the failing validation tests**

```python
from pydantic import ValidationError

from mcp_servers.threatwinds_vision.models import (
    AnalyzePdfInput,
    AnalyzeImageInput,
)


def test_pdf_input_requires_exactly_one_source() -> None:
    try:
        AnalyzePdfInput(prompt="extract text")
    except ValidationError as exc:
        assert "exactly one" in str(exc)
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
        assert "exactly one" in str(exc)
    else:
        raise AssertionError("expected validation error")


def test_image_input_accepts_one_source() -> None:
    params = AnalyzeImageInput(
        prompt="describe image",
        image_path="image.png",
    )
    assert params.image_path == "image.png"
    assert params.model == "qwen-3.6"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_server_models.py -v`
Expected: FAIL with import or model-not-found errors.

- [ ] **Step 3: Write file skeleton**

```python
from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SourceType(str, Enum):
    PATH = "path"
    URL = "url"
    BASE64 = "base64"


class AnalyzePdfInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    prompt: str = Field(..., min_length=1)
    pdf_path: Optional[str] = None
    pdf_url: Optional[str] = None
    pdf_base64: Optional[str] = None
    pages: Optional[str] = None
    model: str = "qwen-3.6"
    dpi: int = 200
    max_tokens: int = 4096

    @model_validator(mode="after")
    def validate_single_source(self) -> "AnalyzePdfInput":
        ...


class AnalyzeImageInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    prompt: str = Field(..., min_length=1)
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    model: str = "qwen-3.6"
    max_tokens: int = 4096

    @model_validator(mode="after")
    def validate_single_source(self) -> "AnalyzeImageInput":
        ...
```

- [ ] **Step 4: Implement validation and shared response model**

```python
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_server_models.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add mcp_servers/threatwinds_vision/models.py tests/threatwinds_vision_mcp/test_server_models.py
git commit -m "feat: add ThreatWinds MCP request models"
```

### Task 2: Build source loading for path, URL, and base64 inputs

**Files:**
- Create: `mcp_servers/threatwinds_vision/source_loader.py`
- Test: `tests/threatwinds_vision_mcp/test_source_loader.py`

- [ ] **Step 1: Write the failing tests for source normalization**

```python
import base64
from pathlib import Path

from mcp_servers.threatwinds_vision.source_loader import (
    load_path_source,
    parse_base64_payload,
    validate_url,
)


def test_validate_url_accepts_https() -> None:
    assert validate_url("https://example.com/file.pdf") == "https://example.com/file.pdf"


def test_parse_base64_payload_supports_data_url() -> None:
    raw = base64.b64encode(b"hello").decode("ascii")
    payload = parse_base64_payload(f"data:image/png;base64,{raw}")
    assert payload.content == b"hello"
    assert payload.mime_type == "image/png"


def test_load_path_source_requires_file(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.pdf"
    file_path.write_bytes(b"%PDF-1.4")
    source = load_path_source(str(file_path), expected_kind="pdf")
    assert source.source_type == "path"
    assert source.local_path == file_path
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_source_loader.py -v`
Expected: FAIL with import or missing function errors.

- [ ] **Step 3: Write file skeleton**

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional


@dataclass
class LoadedSource:
    source_type: Literal["path", "url", "base64"]
    local_path: Path
    mime_type: Optional[str]


@dataclass
class DecodedPayload:
    content: bytes
    mime_type: Optional[str]


def validate_url(url: str) -> str:
    ...


def parse_base64_payload(value: str) -> DecodedPayload:
    ...


def load_path_source(path_str: str, expected_kind: str) -> LoadedSource:
    ...
```

- [ ] **Step 4: Implement local path and base64 helpers**

```python
import base64
import binascii
import mimetypes
from urllib.parse import urlparse


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https URLs are supported")
    if not parsed.netloc:
        raise ValueError("URL must include a network location")
    return url


def parse_base64_payload(value: str) -> DecodedPayload:
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
```

- [ ] **Step 5: Implement URL download with temp file management**

```python
import tempfile
import urllib.request


def download_url_source(url: str, expected_kind: str, timeout: int = 30) -> LoadedSource:
    validate_url(url)
    with urllib.request.urlopen(url, timeout=timeout) as response:
        content_type = response.headers.get_content_type()
        content = response.read()

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
    if expected_kind == "pdf" and suffix != ".pdf":
        raise ValueError("URL did not resolve to PDF content")
    if expected_kind == "image" and not (content_type or "").startswith("image/"):
        raise ValueError("URL did not resolve to image content")

    return LoadedSource(source_type="url", local_path=path, mime_type=content_type)


def materialize_base64_source(value: str, expected_kind: str) -> LoadedSource:
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
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_source_loader.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add mcp_servers/threatwinds_vision/source_loader.py tests/threatwinds_vision_mcp/test_source_loader.py
git commit -m "feat: add ThreatWinds MCP source loading"
```

### Task 3: Build PDF rendering helpers

**Files:**
- Create: `mcp_servers/threatwinds_vision/pdf_renderer.py`
- Test: `tests/threatwinds_vision_mcp/test_pdf_renderer.py`

- [ ] **Step 1: Write the failing page-range tests**

```python
from mcp_servers.threatwinds_vision.pdf_renderer import parse_pages


def test_parse_pages_range() -> None:
    assert parse_pages("1-3") == {1, 2, 3}


def test_parse_pages_csv() -> None:
    assert parse_pages("1,3,5") == {1, 3, 5}


def test_parse_pages_rejects_zero() -> None:
    try:
        parse_pages("0-2")
    except ValueError as exc:
        assert "positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_pdf_renderer.py -v`
Expected: FAIL with import or missing helper errors.

- [ ] **Step 3: Write file skeleton**

```python
from __future__ import annotations

from pathlib import Path

from pypdfium2 import PdfDocument


def parse_pages(pages: str | None) -> set[int] | None:
    ...


def render_pdf_to_images(pdf_path: Path, output_dir: Path, dpi: int = 200) -> list[Path]:
    ...


def filter_rendered_pages(image_paths: list[Path], selected_pages: set[int] | None) -> list[tuple[int, Path]]:
    ...
```

- [ ] **Step 4: Implement page parsing and filtering**

```python
def parse_pages(pages: str | None) -> set[int] | None:
    if pages is None:
        return None

    value = pages.strip()
    if not value:
        return None

    if "-" in value:
        start_text, end_text = value.split("-", 1)
        start = int(start_text)
        end = int(end_text)
        if start < 1 or end < 1:
            raise ValueError("Page numbers must be positive")
        if end < start:
            raise ValueError("Page range end must be greater than or equal to start")
        return set(range(start, end + 1))

    selected = {int(part.strip()) for part in value.split(",") if part.strip()}
    if not selected or min(selected) < 1:
        raise ValueError("Page numbers must be positive")
    return selected


def filter_rendered_pages(image_paths: list[Path], selected_pages: set[int] | None) -> list[tuple[int, Path]]:
    if selected_pages is None:
        return [(index + 1, path) for index, path in enumerate(image_paths)]
    return [
        (index + 1, path)
        for index, path in enumerate(image_paths)
        if index + 1 in selected_pages
    ]
```

- [ ] **Step 5: Implement PDF rendering**

```python
def render_pdf_to_images(pdf_path: Path, output_dir: Path, dpi: int = 200) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    document = PdfDocument(str(pdf_path))
    scale = dpi / 72
    image_paths: list[Path] = []

    try:
        for index, page in enumerate(document):
            bitmap = page.render(scale=scale)
            image_path = output_dir / f"page_{index + 1:03d}.png"
            bitmap.to_pil().save(image_path)
            image_paths.append(image_path)
    finally:
        try:
            document.close()
        except Exception:
            pass

    return image_paths
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_pdf_renderer.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add mcp_servers/threatwinds_vision/pdf_renderer.py tests/threatwinds_vision_mcp/test_pdf_renderer.py
git commit -m "feat: add ThreatWinds MCP PDF rendering helpers"
```

### Task 4: Implement the ThreatWinds vision client

**Files:**
- Create: `mcp_servers/threatwinds_vision/vision_client.py`
- Test: `tests/threatwinds_vision_mcp/test_analysis_service.py`

- [ ] **Step 1: Write the failing payload test**

```python
from mcp_servers.threatwinds_vision.vision_client import build_chat_payload


def test_build_chat_payload_embeds_prompt_and_image() -> None:
    payload = build_chat_payload(
        model="qwen-3.6",
        prompt="extract invoice number",
        data_url="data:image/png;base64,abc",
        max_tokens=2048,
    )
    assert payload["model"] == "qwen-3.6"
    assert payload["messages"][0]["content"][0]["text"] == "extract invoice number"
    assert payload["messages"][0]["content"][1]["image_url"]["url"] == "data:image/png;base64,abc"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_analysis_service.py -v`
Expected: FAIL with import or missing function errors.

- [ ] **Step 3: Write file skeleton**

```python
from __future__ import annotations

import base64
import json
import mimetypes
import os
from pathlib import Path


API_BASE = "https://apis.threatwinds.com/api/ai/v1"


def image_file_to_data_url(image_path: Path) -> str:
    ...


def build_headers(api_key: str, api_secret: str | None) -> dict[str, str]:
    ...


def build_chat_payload(model: str, prompt: str, data_url: str, max_tokens: int) -> dict[str, object]:
    ...


def request_vision_analysis(image_path: Path, prompt: str, model: str, max_tokens: int, api_key: str | None = None, api_secret: str | None = None) -> str:
    ...
```

- [ ] **Step 4: Implement payload and header helpers**

```python
import urllib.error
import urllib.request


def image_file_to_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(image_path.name)
    if not mime_type:
        mime_type = "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def build_headers(api_key: str, api_secret: str | None) -> dict[str, str]:
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
```

- [ ] **Step 5: Implement ThreatWinds request execution**

```python
def request_vision_analysis(
    image_path: Path,
    prompt: str,
    model: str,
    max_tokens: int,
    api_key: str | None = None,
    api_secret: str | None = None,
) -> str:
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
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_analysis_service.py -v`
Expected: PASS for payload-related test(s)

- [ ] **Step 7: Commit**

```bash
git add mcp_servers/threatwinds_vision/vision_client.py tests/threatwinds_vision_mcp/test_analysis_service.py
git commit -m "feat: add ThreatWinds vision client"
```

### Task 5: Implement analysis orchestration for images and PDFs

**Files:**
- Create: `mcp_servers/threatwinds_vision/analysis_service.py`
- Test: `tests/threatwinds_vision_mcp/test_analysis_service.py`

- [ ] **Step 1: Write the failing orchestration tests**

```python
from pathlib import Path

from mcp_servers.threatwinds_vision.models import SourceType
from mcp_servers.threatwinds_vision.analysis_service import combine_page_content


def test_combine_page_content_joins_pages() -> None:
    combined = combine_page_content([
        (1, "first page"),
        (2, "second page"),
    ])
    assert "=== Page 1 ===" in combined
    assert "second page" in combined
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_analysis_service.py -v`
Expected: FAIL with import or missing function errors.

- [ ] **Step 3: Write file skeleton**

```python
from __future__ import annotations

from pathlib import Path

from .models import ImageAnalysisResult, PdfAnalysisResult


def combine_page_content(page_results: list[tuple[int, str]]) -> str:
    ...


def analyze_image_source(...):
    ...


def analyze_pdf_source(...):
    ...
```

- [ ] **Step 4: Implement page aggregation and image analysis**

```python
from .models import AnalysisError, AnalysisWarning, ImageAnalysisResult, PageResult, PdfAnalysisResult, SourceType
from .pdf_renderer import filter_rendered_pages, parse_pages, render_pdf_to_images
from .source_loader import download_url_source, load_path_source, materialize_base64_source
from .vision_client import request_vision_analysis

import tempfile


def combine_page_content(page_results: list[tuple[int, str]]) -> str:
    return "\n\n".join(
        f"=== Page {page} ===\n{content}" for page, content in page_results
    )


def _resolve_image_source(image_path: str | None, image_url: str | None, image_base64: str | None):
    if image_path:
        return load_path_source(image_path, expected_kind="image")
    if image_url:
        return download_url_source(image_url, expected_kind="image")
    return materialize_base64_source(image_base64 or "", expected_kind="image")


def analyze_image_source(image_path: str | None, image_url: str | None, image_base64: str | None, prompt: str, model: str, max_tokens: int) -> ImageAnalysisResult:
    source = _resolve_image_source(image_path, image_url, image_base64)
    content = request_vision_analysis(source.local_path, prompt, model, max_tokens)
    return ImageAnalysisResult(
        source_type=SourceType(source.source_type),
        model=model,
        prompt=prompt,
        content=content,
    )
```

- [ ] **Step 5: Implement PDF analysis with partial page failure support**

```python
def _resolve_pdf_source(pdf_path: str | None, pdf_url: str | None, pdf_base64: str | None):
    if pdf_path:
        return load_path_source(pdf_path, expected_kind="pdf")
    if pdf_url:
        return download_url_source(pdf_url, expected_kind="pdf")
    return materialize_base64_source(pdf_base64 or "", expected_kind="pdf")


def analyze_pdf_source(pdf_path: str | None, pdf_url: str | None, pdf_base64: str | None, prompt: str, model: str, dpi: int, max_tokens: int, pages: str | None) -> PdfAnalysisResult:
    source = _resolve_pdf_source(pdf_path, pdf_url, pdf_base64)
    selected_pages = parse_pages(pages)
    page_results: list[tuple[int, str]] = []
    errors: list[AnalysisError] = []
    warnings: list[AnalysisWarning] = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        rendered = render_pdf_to_images(source.local_path, Path(tmp_dir), dpi=dpi)
        filtered = filter_rendered_pages(rendered, selected_pages)
        if not filtered:
            raise ValueError("No PDF pages selected for processing")

        for page_number, image_path in filtered:
            try:
                content = request_vision_analysis(image_path, prompt, model, max_tokens)
                page_results.append((page_number, content))
            except Exception as exc:
                errors.append(
                    AnalysisError(
                        code="page_analysis_failed",
                        message=str(exc),
                        page=page_number,
                    )
                )

    if errors:
        warnings.append(
            AnalysisWarning(
                code="partial_pdf_analysis",
                message="One or more PDF pages could not be analyzed",
            )
        )

    return PdfAnalysisResult(
        source_type=SourceType(source.source_type),
        model=model,
        prompt=prompt,
        results=[PageResult(page=page, content=content) for page, content in page_results],
        combined_content=combine_page_content(page_results),
        warnings=warnings,
        errors=errors,
    )
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_analysis_service.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add mcp_servers/threatwinds_vision/analysis_service.py tests/threatwinds_vision_mcp/test_analysis_service.py
git commit -m "feat: add ThreatWinds analysis orchestration"
```

### Task 6: Expose FastMCP tools

**Files:**
- Create: `mcp_servers/threatwinds_vision/server.py`
- Create: `mcp_servers/threatwinds_vision/__init__.py`
- Test: `tests/threatwinds_vision_mcp/test_server_models.py`

- [ ] **Step 1: Write the failing server import test**

```python
from mcp_servers.threatwinds_vision.server import mcp


def test_server_is_initialized() -> None:
    assert mcp is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_server_models.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write server skeleton**

```python
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .analysis_service import analyze_image_source, analyze_pdf_source
from .models import AnalyzeImageInput, AnalyzePdfInput


mcp = FastMCP("threatwinds_vision_mcp")


@mcp.tool(name="analyze_pdf")
async def analyze_pdf(params: AnalyzePdfInput) -> str:
    ...


@mcp.tool(name="analyze_image")
async def analyze_image(params: AnalyzeImageInput) -> str:
    ...


if __name__ == "__main__":
    mcp.run()
```

- [ ] **Step 4: Implement tool functions**

```python
import json


@mcp.tool(
    name="analyze_pdf",
    annotations={
        "title": "Analyze scanned PDF with ThreatWinds",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def analyze_pdf(params: AnalyzePdfInput) -> str:
    result = analyze_pdf_source(
        pdf_path=params.pdf_path,
        pdf_url=params.pdf_url,
        pdf_base64=params.pdf_base64,
        prompt=params.prompt,
        model=params.model,
        dpi=params.dpi,
        max_tokens=params.max_tokens,
        pages=params.pages,
    )
    return json.dumps(result.model_dump(), indent=2)


@mcp.tool(
    name="analyze_image",
    annotations={
        "title": "Analyze image with ThreatWinds",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def analyze_image(params: AnalyzeImageInput) -> str:
    result = analyze_image_source(
        image_path=params.image_path,
        image_url=params.image_url,
        image_base64=params.image_base64,
        prompt=params.prompt,
        model=params.model,
        max_tokens=params.max_tokens,
    )
    return json.dumps(result.model_dump(), indent=2)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_server_models.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add mcp_servers/threatwinds_vision/server.py mcp_servers/threatwinds_vision/__init__.py tests/threatwinds_vision_mcp/test_server_models.py
git commit -m "feat: add ThreatWinds FastMCP server"
```

### Task 7: Refactor the existing OCR CLI to use shared modules

**Files:**
- Modify: `skills/pdf/scripts/ocr_vision.py`
- Test: `tests/threatwinds_vision_mcp/test_analysis_service.py`

- [ ] **Step 1: Write the failing CLI smoke test outline**

```python
def test_existing_cli_can_still_build_json_output(monkeypatch):
    # Smoke-test only: monkeypatch shared service and assert the CLI formats output.
    assert True
```
```

- [ ] **Step 2: Run test to verify it fails or is absent**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_analysis_service.py -v`
Expected: FAIL or missing coverage for CLI integration.

- [ ] **Step 3: Replace inline API/PDF logic with imports from shared modules**

```python
from mcp_servers.threatwinds_vision.analysis_service import analyze_pdf_source
```

Update `main()` so the CLI argument parsing remains, but execution becomes:

```python
result = analyze_pdf_source(
    pdf_path=args.pdf,
    pdf_url=None,
    pdf_base64=None,
    prompt=args.prompt,
    model=args.model,
    dpi=args.dpi,
    max_tokens=args.max_tokens,
    pages=args.pages,
)

if args.json:
    output_text = json.dumps(
        [{"page": item.page, "content": item.content} for item in result.results],
        indent=2,
    )
else:
    output_text = result.combined_content
```

- [ ] **Step 4: Keep CLI output/file-writing behavior intact**

```python
if args.output:
    with open(args.output, "w") as handle:
        handle.write(output_text)
    print(f"Output written to {args.output}", file=sys.stderr)
else:
    print(output_text)
```

- [ ] **Step 5: Run focused verification**

Run: `python -m pytest tests/threatwinds_vision_mcp/test_analysis_service.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add skills/pdf/scripts/ocr_vision.py tests/threatwinds_vision_mcp/test_analysis_service.py
git commit -m "refactor: reuse ThreatWinds analysis modules in OCR CLI"
```

### Task 8: Document setup and optional OpenCode MCP wiring

**Files:**
- Create: `mcp_servers/threatwinds_vision/README.md`
- Modify: `README.md`
- Modify: `.opencode/opencode.json`

- [ ] **Step 1: Write the ThreatWinds MCP example README skeleton**

```md
# ThreatWinds Vision MCP Example

## Requirements
- `THREATWINDS_API_KEY`
- optional `THREATWINDS_API_SECRET`

## Running the server
...

## Tools
- `analyze_pdf`
- `analyze_image`
```

- [ ] **Step 2: Fill in exact example commands**

```md
```bash
source ~/.local/opencode-venv/bin/activate
python mcp_servers/threatwinds_vision/server.py
```

Example OpenCode MCP config:

```json
{
  "mcp": {
    "threatwinds-vision": {
      "type": "local",
      "command": [
        "/home/osmany/.local/opencode-venv/bin/python3",
        "/path/to/repo/mcp_servers/threatwinds_vision/server.py"
      ],
      "environment": {
        "THREATWINDS_API_KEY": "{env:THREATWINDS_API_KEY}",
        "THREATWINDS_API_SECRET": "{env:THREATWINDS_API_SECRET}"
      }
    }
  }
}
```
```

- [ ] **Step 3: Update root README with a short pointer to the new example**

Add a concise section under install or features describing that the repo now includes a FastMCP example for ThreatWinds PDF/image analysis.

- [ ] **Step 4: Optionally register the new server in `.opencode/opencode.json`**

If this repo’s local config is intended to expose the example by default, add:

```json
"threatwinds-vision": {
  "type": "local",
  "command": [
    "/home/osmany/.local/opencode-venv/bin/python3",
    "/home/osmany/Data/Projects/github.com/osmontero/opencode-skills/mcp_servers/threatwinds_vision/server.py"
  ],
  "environment": {
    "THREATWINDS_API_KEY": "{env:THREATWINDS_API_KEY}",
    "THREATWINDS_API_SECRET": "{env:THREATWINDS_API_SECRET}"
  }
}
```

- [ ] **Step 5: Run final focused verification**

Run:
- `python -m pytest tests/threatwinds_vision_mcp -v`
- `python mcp_servers/threatwinds_vision/server.py --help` (or equivalent startup check if supported)

Expected:
- tests PASS
- server starts without import/config errors

- [ ] **Step 6: Commit**

```bash
git add mcp_servers/threatwinds_vision/README.md README.md .opencode/opencode.json
git commit -m "docs: add ThreatWinds MCP server usage"
```

## Self-Review

- Spec coverage: all approved requirements are represented — FastMCP server, arbitrary prompt pass-through, PDF/image support, path/URL/base64 support, shared module refactor, and documentation.
- Placeholder scan: plan uses exact file paths, concrete responsibilities, commands, and code blocks for each code step.
- Type consistency: `AnalyzePdfInput`, `AnalyzeImageInput`, `PdfAnalysisResult`, and `ImageAnalysisResult` are reused consistently across tasks.
