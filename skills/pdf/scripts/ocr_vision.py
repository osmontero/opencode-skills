#!/usr/bin/env python3
"""
Extract data from scanned PDF pages using LLM vision.

Converts PDF pages to images, then sends them to the ThreatWinds AI API
with a prompt to extract text, tables, forms, or structured data.

Usage:
    PYENV_VERSION=3.12.12 python3 scripts/ocr_vision.py input.pdf
    PYENV_VERSION=3.12.12 python3 scripts/ocr_vision.py input.pdf --prompt "Extract all names and dates"
    PYENV_VERSION=3.12.12 python3 scripts/ocr_vision.py input.pdf --json --output result.json
    PYENV_VERSION=3.12.12 python3 scripts/ocr_vision.py input.pdf --pages 1-3
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request

try:
    from pypdfium2 import PdfDocument
except ImportError:
    print("Error: pypdfium2 not installed.", file=sys.stderr)
    print("Run: PYENV_VERSION=3.12.12 pip3 install pypdfium2", file=sys.stderr)
    sys.exit(1)


API_BASE = "https://apis.threatwinds.com/api/ai/v1"
DEFAULT_MODEL = "threatwinds/qwen-3.6"
DEFAULT_PROMPT = (
    "Extract all visible text from this document image. Preserve the layout and "
    "structure as much as possible. If there are tables, represent them as markdown "
    "tables. If there are form fields, list them with their labels and any filled values."
)


def encode_image(image_path):
    """Encode an image file as base64 data URL."""
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def pdf_to_images(pdf_path, output_dir, dpi=150):
    """Convert PDF pages to PNG images."""
    os.makedirs(output_dir, exist_ok=True)
    doc = PdfDocument(pdf_path)
    scale = dpi / 72
    images = []

    for i, page in enumerate(doc):
        render = page.render(scale=scale)
        path = os.path.join(output_dir, f"page_{i + 1:03d}.png")
        render.save(path)
        images.append(path)

    doc.close()
    return images


def call_vision_api(image_path, prompt, model, api_key, api_secret, max_tokens=4096):
    """Send an image to the ThreatWinds vision API and return the response."""
    data_url = encode_image(image_path)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
            ],
        }
    ]

    payload = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": max_tokens,
    }

    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    if api_key and api_secret:
        headers["api-key"] = api_key
        headers["api-secret"] = api_secret
    elif api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"API error {e.code}: {body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error calling API: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Extract data from scanned PDFs using LLM vision"
    )
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument(
        "-p", "--prompt", default=DEFAULT_PROMPT, help="Prompt for the LLM"
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL, help=f"Model ID (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("THREATWINDS_API_KEY"),
        help="ThreatWinds API key (or set THREATWINDS_API_KEY env var)",
    )
    parser.add_argument("--api-secret", default=os.environ.get("THREATWINDS_API_SECRET"), help="ThreatWinds API secret")
    parser.add_argument(
        "--pages",
        help="Page range to process (e.g., '1-3' or '1,3,5'). Default: all pages.",
    )
    parser.add_argument(
        "-o", "--output", help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output structured JSON (one entry per page)"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=4096, help="Max output tokens per page (default: 4096)"
    )
    parser.add_argument(
        "--dpi", type=int, default=200, help="Image DPI for conversion (default: 200)"
    )
    args = parser.parse_args()

    if not args.api_key:
        print("Error: THREATWINDS_API_KEY is required.", file=sys.stderr)
        print("Set it via --api-key or the THREATWINDS_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    # Parse page range
    pages_to_process = None
    if args.pages:
        if "-" in args.pages:
            start, end = args.pages.split("-", 1)
            pages_to_process = set(range(int(start), int(end) + 1))
        else:
            pages_to_process = set(int(p) for p in args.pages.split(","))

    # Convert PDF to images
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        images = pdf_to_images(args.pdf, tmpdir, dpi=args.dpi)

        if pages_to_process:
            filtered = []
            for i, img in enumerate(images):
                if (i + 1) in pages_to_process:
                    filtered.append(img)
            images = filtered

        if not images:
            print("No pages to process.", file=sys.stderr)
            sys.exit(1)

        results = []
        total = len(images)

        for i, img_path in enumerate(images):
            page_num = i + 1
            print(f"Processing page {page_num}/{total}...", file=sys.stderr)

            text = call_vision_api(
                img_path, args.prompt, args.model,
                args.api_key, args.api_secret, args.max_tokens
            )

            if text is None:
                text = f"(error processing page {page_num})"

            if args.json:
                results.append({"page": page_num, "content": text})
            else:
                results.append(f"=== Page {page_num} ===\n{text}\n")

    # Output
    output_text = json.dumps(results, indent=2) if args.json else "".join(results)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
