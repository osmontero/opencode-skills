#!/usr/bin/env python3
"""
Analyze images using LLM vision.

Sends images to the ThreatWinds AI API with a prompt to extract text,
describe content, identify objects, or answer questions about visual content.

Usage:
    python3 scripts/analyze_image.py image.png
    python3 scripts/analyze_image.py image.png --prompt "Extract all text from this image"
    python3 scripts/analyze_image.py https://example.com/chart.jpg
    python3 scripts/analyze_image.py screenshot.png --model qwen-3.6 --max-tokens 2048
"""
import argparse
import os
import sys

# Ensure the vision module is on sys.path
# Layout: <repo>/skills/processing-images/scripts/analyze_image.py
#          └── go up 1 level → <repo>/skills/processing-images/ (where vision/ module lives)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_images_skill_dir = os.path.dirname(_script_dir)
if _images_skill_dir not in sys.path:
    sys.path.insert(0, _images_skill_dir)

from vision.analysis_service import (
    analyze_image_source,
)

DEFAULT_MODEL = "qwen-3.6"
DEFAULT_PROMPT = (
    "Analyze this image and describe what you see in detail. If there is visible text, "
    "extract it and preserve the layout. If this is a chart or graph, describe the data "
    "and any trends. If this is a form or document, identify the fields and their values."
)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze images using LLM vision"
    )
    parser.add_argument(
        "image",
        help="Path to image file or URL (e.g., 'image.png' or 'https://example.com/image.jpg')"
    )
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
        "--max-tokens", type=int, default=4096, help="Max output tokens (default: 4096)"
    )
    args = parser.parse_args()

    if not args.api_key:
        print("Error: THREATWINDS_API_KEY is required.", file=sys.stderr)
        print("Set it via --api-key or the THREATWINDS_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    # Forward CLI API credentials to the shared service via environment variables.
    os.environ["THREATWINDS_API_KEY"] = args.api_key
    if args.api_secret:
        os.environ["THREATWINDS_API_SECRET"] = args.api_secret

    # Determine if input is a URL or local path
    is_url = args.image.startswith("http://") or args.image.startswith("https://")
    
    print("Analyzing image...", file=sys.stderr)
    
    try:
        if is_url:
            result = analyze_image_source(
                prompt=args.prompt,
                model=args.model,
                max_tokens=args.max_tokens,
                image_url=args.image,
            )
        else:
            result = analyze_image_source(
                prompt=args.prompt,
                model=args.model,
                max_tokens=args.max_tokens,
                image_path=args.image,
            )
        
        print(f"Analysis complete.", file=sys.stderr)
        print(result.content)
        
    except FileNotFoundError as e:
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
