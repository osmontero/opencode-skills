#!/usr/bin/env python3
"""Fill a fillable PDF form with values from a JSON file."""
import argparse
import json
import sys

from pypdf import PdfReader, PdfWriter


def main():
    parser = argparse.ArgumentParser(description="Fill a PDF form")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("fields", help="Path to JSON file with field values")
    parser.add_argument("-o", "--output", default="filled.pdf", help="Output PDF file")
    args = parser.parse_args()

    try:
        with open(args.fields) as f:
            field_values = json.load(f)
    except Exception as e:
        print(f"Error reading fields file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        reader = PdfReader(args.pdf)
        writer = PdfWriter()
        writer.append(reader)

        if writer.is_encrypted:
            writer.decrypt("")

        form = writer.get_form_text_fields()
        missing = [k for k in field_values if k not in form]
        if missing:
            print(f"Warning: fields not found in form: {missing}")

        writer.update_page_form_field_values(None, field_values)

        with open(args.output, "wb") as f:
            writer.write(f)

        print(f"Form filled. Output: {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
