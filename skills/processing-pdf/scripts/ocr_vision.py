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
import json
import os
import sys

# Ensure the vision module is on sys.path
# Layout: <repo>/skills/pdf/scripts/ocr_vision.py
#          └── go up 1 level → <repo>/skills/pdf/ (where vision/ module lives)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_pdf_skill_dir = os.path.dirname(_script_dir)
if _pdf_skill_dir not in sys.path:
    sys.path.insert(0, _pdf_skill_dir)

from vision.analysis_service import (
    analyze_pdf_source,
)

DEFAULT_MODEL = "qwen-3.6"
DEFAULT_PROMPT = (
    "Extract all visible text from this document image. Preserve the layout and "
    "structure as much as possible. If there are tables, represent them as markdown "
    "tables. If there are form fields, list them with their labels and any filled values."
)


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
    parser.add_argument(
        "--api-secret",
        default=os.environ.get("THREATWINDS_API_SECRET"),
        help="ThreatWinds API secret",
    )
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

    # Forward CLI API credentials to the shared service via environment variables.
    # The analysis service chain reads from THREATWINDS_API_KEY / THREATWINDS_API_SECRET.
    os.environ["THREATWINDS_API_KEY"] = args.api_key
    if args.api_secret:
        os.environ["THREATWINDS_API_SECRET"] = args.api_secret

    # Delegate to the shared analysis service
    print("Analyzing PDF...", file=sys.stderr)
    result = analyze_pdf_source(
        prompt=args.prompt,
        model=args.model,
        max_tokens=args.max_tokens,
        dpi=args.dpi,
        pages=args.pages,
        pdf_path=args.pdf,
    )
    print(f"Analysis complete ({len(result.results)} pages).", file=sys.stderr)

    # Print any warnings to stderr
    for warning in result.warnings:
        print(f"Warning [{warning.code}]: {warning.message}", file=sys.stderr)

    # Print any errors to stderr
    for error in result.errors:
        page_info = f" (page {error.page})" if error.page else ""
        print(f"Error [{error.code}]{page_info}: {error.message}", file=sys.stderr)

    # Format output
    if args.json:
        results_list = [
            {"page": r.page, "content": r.content} for r in result.results
        ]
        output_text = json.dumps(results_list, indent=2)
    else:
        output_text = result.combined_content

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
