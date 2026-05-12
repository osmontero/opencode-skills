#!/usr/bin/env python3
"""Extract tables from a PDF and save each as a CSV file."""
import argparse
import csv
import sys

import pdfplumber


def main():
    parser = argparse.ArgumentParser(description="Extract tables from a PDF")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("-o", "--output_dir", default=".", help="Output directory")
    args = parser.parse_args()

    try:
        with pdfplumber.open(args.pdf) as pdf:
            total_tables = 0
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for j, table in enumerate(tables):
                    total_tables += 1
                    filename = f"page{i + 1}_table{j + 1}.csv"
                    filepath = f"{args.output_dir}/{filename}"
                    with open(filepath, "w", newline="") as f:
                        writer = csv.writer(f)
                        for row in table:
                            writer.writerow([cell or "" for cell in row])
                    print(f"  {filepath} ({len(table)} rows)")

            if total_tables == 0:
                print("No tables found in the PDF.")
            else:
                print(f"\nExtracted {total_tables} table(s).")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
