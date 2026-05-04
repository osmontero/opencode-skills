#!/usr/bin/env python3
"""Convert PDF pages to images."""
import argparse
import os
import sys

try:
    from pypdfium2 import PdfDocument
except ImportError:
    print("Error: pypdfium2 not installed. Run: PYENV_VERSION=3.12.12 pip3 install pypdfium2", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Convert PDF pages to images")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("-o", "--output_dir", default=".", help="Output directory")
    parser.add_argument("--dpi", type=int, default=150, help="DPI (default: 150)")
    parser.add_argument("--format", choices=["png", "jpg"], default="png", help="Image format")
    args = parser.parse_args()

    try:
        doc = PdfDocument(args.pdf)
        os.makedirs(args.output_dir, exist_ok=True)

        scale = args.dpi / 72
        ext = args.format

        for i, page in enumerate(doc):
            render = page.render(scale=scale)
            filename = f"page_{i + 1:03d}.{ext}"
            filepath = f"{args.output_dir}/{filename}"
            render.save(filepath)
            print(f"  {filepath} ({render.width}x{render.height})")

        doc.close()
        print(f"\nConverted {len(doc)} page(s) at {args.dpi} DPI.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
