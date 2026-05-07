#!/usr/bin/env python3
"""Extract text from a PDF file with page numbers."""
import argparse
import sys

import pdfplumber


def main():
    parser = argparse.ArgumentParser(description="Extract text from a PDF")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("-f", "--first", type=int, help="First page (1-indexed)")
    parser.add_argument("-l", "--last", type=int, help="Last page (1-indexed)")
    args = parser.parse_args()

    try:
        with pdfplumber.open(args.pdf) as pdf:
            total = len(pdf.pages)
            start = (args.first or 1) - 1
            end = args.last if args.last else total

            if args.output:
                out = open(args.output, "w")
            else:
                out = sys.stdout

            for i in range(start, min(end, total)):
                page = pdf.pages[i]
                text = page.extract_text() or "(no text on this page)"
                out.write(f"=== Page {i + 1} of {total} ===\n")
                out.write(text + "\n\n")

            if args.output:
                out.close()
                print(f"Extracted {min(end, total) - start} pages to {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
