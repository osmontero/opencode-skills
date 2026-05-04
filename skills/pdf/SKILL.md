---
name: PDF Processing
description: >
  Extract text and tables from PDF files, fill forms, merge and split documents, convert PDFs to images, and perform OCR on scanned PDFs.
  Use when working with PDF files or when the user mentions PDFs, forms, document extraction, or scanned documents.
---

# PDF Processing

Process PDF files using command-line tools and Python libraries.

## Prerequisites

Before running any Python scripts, **activate the opencode virtual environment**:

```bash
source ~/.local/opencode-venv/bin/activate
```

Then use `python3 scripts/...` normally. To run a single script without activating:

```bash
~/.local/opencode-venv/bin/python3 scripts/extract_text.py input.pdf
```

## Available Tools

| Tool | Command | Use For |
|------|---------|---------|
| `pdftotext` | System (Poppler) | Quick text extraction |
| `pdfinfo` | System (Poppler) | Metadata, page count |
| `pypdf` | Python (venv) | Merge, split, rotate, metadata |
| `pdfplumber` | Python (venv) | Table extraction, detailed text |

## Quick Operations

### Extract text from a PDF

```bash
# Simple extraction (preserves layout)
pdftotext input.pdf output.txt

# Single page
pdftotext -f 3 -l 3 input.pdf page3.txt

# Layout preservation
pdftotext -layout input.pdf output.txt
```

### Get PDF info

```bash
pdfinfo input.pdf
```

### Extract text with Python (more control)

```python
import pdfplumber

with pdfplumber.open("input.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"--- Page {i+1} ---")
        print(text)
```

### Extract tables

```python
import pdfplumber
import csv

with pdfplumber.open("input.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            with open(f"page{i+1}_table{j+1}.csv", "w", newline="") as f:
                writer = csv.writer(f)
                for row in table:
                    writer.writerow([cell or "" for cell in row])
```

### Merge PDFs

```python
from pypdf import PdfReader, PdfWriter

writer = PdfWriter()
for pdf_file in ["file1.pdf", "file2.pdf", "file3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as f:
    writer.write(f)
```

### Split PDF into individual pages

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1:03d}.pdf", "wb") as f:
        writer.write(f)
```

### Rotate pages

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages:
    page.rotate(90)  # 90, 180, or 270 degrees
    writer.add_page(page)

with open("rotated.pdf", "wb") as f:
    writer.write(f)
```

### Remove pages

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
pages_to_keep = {0, 1, 4, 5}  # 0-indexed
for i, page in enumerate(reader.pages):
    if i in pages_to_keep:
        writer.add_page(page)

with open("trimmed.pdf", "wb") as f:
    writer.write(f)
```

## Script-Based Operations

### Extract all text with page numbers

```bash
python3 scripts/extract_text.py input.pdf
```

### Extract tables to CSV

```bash
python3 scripts/extract_tables.py input.pdf
```

### Check if PDF has fillable forms

```bash
python3 scripts/check_forms.py input.pdf
```

### Fill a fillable PDF form

```bash
python3 scripts/fill_form.py input.pdf fields.json output.pdf
```

Where `fields.json` is:

```json
{
  "field_name": "John Smith",
  "email": "john@example.com",
  "date": "2026-05-04"
}
```

### Convert PDF pages to images

```bash
python3 scripts/to_images.py input.pdf --dpi 200
```

### Get PDF metadata

```bash
python3 scripts/metadata.py input.pdf
```

## Working with Scanned PDFs

For scanned PDFs, text extraction will return empty results. Use the LLM vision-based OCR script to extract data from image-based pages.

### OCR with LLM Vision

Uses `threatwinds/qwen-3.6` via the ThreatWinds AI API to extract text, tables, and structured data from scanned document images.

**Prerequisites:**
- `THREATWINDS_API_KEY` environment variable must be set
- opencode Python venv must be active (see Prerequisites section above)

```bash
# Basic extraction (all pages)
python3 scripts/ocr_vision.py scanned.pdf

# Custom prompt for structured data
python3 scripts/ocr_vision.py invoice.pdf \
  --prompt "Extract the invoice number, date, line items, quantities, prices, and total. Output as JSON."

# Specific pages only
python3 scripts/ocr_vision.py document.pdf --pages 1-3

# JSON output to file
python3 scripts/ocr_vision.py form.pdf --json -o extracted.json
```

**How it works:**
1. Converts each PDF page to a PNG image at 200 DPI
2. Sends the image as base64 to the ThreatWinds `/chat/completions` endpoint with vision support
3. Returns extracted text or structured data per page

**Detection workflow:** When given a PDF, first try `pdftotext`. If the output is empty or near-empty, the PDF is scanned — fall back to `ocr_vision.py`.

## Large Files

For large PDFs (>50MB):
- Use `pdftotext` for quick extraction (faster than Python)
- Process pages in batches with `pdfplumber`
- Use `-f` and `-l` flags with `pdftotext` for specific page ranges

## Writing Large Output Files

If extracting text from a very large PDF, write the output incrementally (~1000 tokens per edit) rather than in a single pass.

## Common Patterns

### Extract specific pages

```bash
pdftotext -f 5 -l 10 input.pdf pages_5_10.txt
```

### Search for text in a PDF

```bash
pdftotext input.pdf - | grep -n "search term"
```

### Compare two PDFs (text diff)

```bash
pdftotext doc1.pdf - > /tmp/doc1.txt
pdftotext doc2.pdf - > /tmp/doc2.txt
diff /tmp/doc1.txt /tmp/doc2.txt
```
