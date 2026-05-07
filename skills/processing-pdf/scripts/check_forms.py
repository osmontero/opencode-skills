#!/usr/bin/env python3
"""Check if a PDF has fillable form fields and list them."""
import argparse
import json
import sys

from pypdf import PdfReader


def main():
    parser = argparse.ArgumentParser(description="Check PDF for fillable form fields")
    parser.add_argument("pdf", help="Path to PDF file")
    args = parser.parse_args()

    try:
        reader = PdfReader(args.pdf)
        fields = reader.get_fields()

        if not fields:
            print("No fillable form fields found.")
            print("\nTo check if this is a scanned form, convert to images and analyze visually.")
            return

        print(f"Found {len(fields)} fillable form field(s):\n")
        for name, field in sorted(fields.items()):
            ftype = field.get("/FT", "unknown")
            value = field.get("/V", "(empty)")
            print(f"  {name}:")
            print(f"    Type:  {ftype}")
            print(f"    Value: {value}")
            print()

        print("To fill these fields, create a JSON file with field names as keys:")
        print(json.dumps({name: "" for name in sorted(fields.keys())}, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
