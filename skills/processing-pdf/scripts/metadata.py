#!/usr/bin/env python3
"""Extract metadata from a PDF file."""
import argparse
import json
import sys

from pypdf import PdfReader


def main():
    parser = argparse.ArgumentParser(description="Extract PDF metadata")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    try:
        reader = PdfReader(args.pdf)
        meta = reader.metadata
        info = {
            "pages": len(reader.pages),
            "encrypted": reader.is_encrypted,
        }

        if meta:
            for key in ["/Title", "/Author", "/Subject", "/Creator", "/Producer", "/CreationDate", "/ModDate"]:
                val = meta.get(key)
                if val:
                    info[key.lstrip("/").replace("/", " ")] = str(val)

        if args.json:
            print(json.dumps(info, indent=2))
        else:
            for k, v in info.items():
                print(f"  {k}: {v}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
