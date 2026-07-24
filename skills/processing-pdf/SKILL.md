---
name: processing-pdf
description: >
  Use when the user needs to extract data from PDFs, work with scanned documents, or manipulate PDF files. Triggers include: "extract text from PDF", "convert PDF to text/CSV/images", "scan/OCR this document", "merge/split/rotate PDF", "fill PDF form", "PDF is blank/empty" (likely scanned), or any mention of .pdf files requiring data extraction or transformation. Also use for invoices, receipts, forms, contracts, reports, or any document where structured data (text, tables, form fields) needs to be extracted.
---

# PDF Processing

Process PDF files using command-line tools and Python libraries. For scanned PDFs, convert pages to images and have the LLM read them using its built-in image understanding.

## Prerequisites

Before running any Python scripts, **activate the opencode virtual environment**:

```bash
source ~/.local/opencode-venv/bin/activate
```

Then use `python3 scripts/...` normally.

## Available Tools

| Tool                  | Command                          | Use For                                                           |
|-----------------------|----------------------------------|-------------------------------------------------------------------|
| `pdf-extractor` agent | Global agent (dispatch via `task`) | Full PDF extraction (all pages, all data, structured folder tree) |
| `pdftotext`           | System (Poppler)                 | Quick text extraction                                             |
| `pdfinfo`             | System (Poppler)                 | Metadata, page count                                              |
| `pypdf`               | Python (venv)                    | Merge, split, rotate                                              |
| `pdfplumber`          | Python (venv)                    | Table extraction, detailed text                                   |
| `to_images.py`        | Python script (venv)             | Convert pages to PNG images                                       |

## Decision Guide

```
Need to process a PDF?
│
├─ Extract everything from a PDF?
│  └─ Dispatch the `pdf-extractor` agent.
│     It converts all pages to images, reads each one, and stores
│     per-page results in extracted_data/<pdf_name>/page_NNN/content.md
│     along with images and a summary.
│
├─ Quick text from a normal PDF?
│  ├─ Simple: pdftotext input.pdf output.txt
│  └─ With page numbers: python3 scripts/extract_text.py input.pdf
│
├─ Extract tables?
│  └─ python3 scripts/extract_tables.py input.pdf -o ./tables/
│
├─ Fill a form?
│  ├─ Check fields: python3 scripts/check_forms.py input.pdf
│  └─ Fill: python3 scripts/fill_form.py input.pdf fields.json output.pdf
│
├─ Read a scanned PDF (quick)?
│  ├─ Convert: python3 scripts/to_images.py scanned.pdf -o ./pages/ --dpi 200
│  └─ Read the images and extract what you need
│
├─ Merge/Split/Rotate?
│  └─ See pypdf examples below
│
└─ Large file (>50MB)?
   ├─ Quick text: pdftotext (fastest)
   └─ Page ranges: pdftotext -f N -l M input.pdf
```

## Full PDF Extraction

For complete extraction of all data from a PDF (text, tables, forms, structure), dispatch the `pdf-extractor` agent. It:

1. Converts all pages to PNG images
2. Reads each image using LLM vision
3. Extracts text, tables, key facts, form fields, and notes
4. Per-page output in `extracted_data/<pdf_name>/page_NNN/`:
   - `page_NNN.png` — the page image
   - `content.md` — all text and extracted facts as markdown
   - Other LLM-legible files as needed
5. Creates `summary.md` with document-level overview

### When to use the extractor agent

- Multi-page documents where you need all the data
- Scanned PDFs or mixed scanned/digital PDFs
- Documents with complex layouts (tables, columns, forms)
- When you need a structured, browsable folder tree of results

### Quick extraction (no agent)

For a single page or a quick glance, use the manual steps below.

## Reading Scanned PDFs (Quick, No Agent)

When a PDF is scanned (no selectable text), convert its pages to images and let the LLM read them.

### Step 1: Detect if PDF is scanned

```bash
pdftotext document.pdf - | head -20
```
If output is empty or whitespace, the PDF is scanned.

### Step 2: Convert pages to images

```bash
# All pages at 200 DPI (sufficient for most documents)
python3 scripts/to_images.py document.pdf -o ./pdf-pages/ --dpi 200

# Higher quality for handwritten or low-quality scans
python3 scripts/to_images.py document.pdf -o ./pdf-pages/ --dpi 300
```

### Step 3: Read the images

Reference the generated PNG files directly — the LLM can read them natively. Ask it to extract text, tables, fields, or answer questions about the document content.

### Step 4: Clean up

```bash
rm -rf ./pdf-pages/
```

### Tips for scanned PDFs

- **200 DPI** works for most documents
- **300 DPI** for handwritten content or blurry scans
- For large PDFs, convert pages in batches (use pypdf to split first, then convert)
- Always clean up the generated image directory after reading

## Text Extraction

### Quick extraction (pdftotext)

```bash
# Simple extraction
pdftotext input.pdf output.txt

# Single page
pdftotext -f 3 -l 3 input.pdf page3.txt

# With layout preservation
pdftotext -layout input.pdf output.txt

# Page range
pdftotext -f 5 -l 10 input.pdf pages_5_10.txt
```

### With page numbers (script)

```bash
python3 scripts/extract_text.py input.pdf
```

### Get PDF info

```bash
pdfinfo input.pdf
```

## Table Extraction

### Script (recommended)

```bash
python3 scripts/extract_tables.py input.pdf -o ./tables/
```

### Python (inline)

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

## Form Handling

### Check for fillable fields

```bash
python3 scripts/check_forms.py input.pdf
```

### Fill a form

```bash
python3 scripts/fill_form.py input.pdf fields.json output.pdf
```

Where `fields.json` contains:

```json
{
  "field_name": "John Smith",
  "email": "john@example.com",
  "date": "2026-05-04"
}
```

## PDF Manipulation (pypdf)

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

### Split into individual pages

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

## Metadata

```bash
python3 scripts/metadata.py input.pdf
```

## Convert to Images

```bash
python3 scripts/to_images.py input.pdf --dpi 200
```

## Large Files

For large PDFs (>50MB):
- Use `pdftotext` for quick extraction (faster than Python)
- Process pages in batches with `pdfplumber`
- Use `-f` and `-l` flags with `pdftotext` for specific page ranges

## Writing Large Output Files

If extracting text from a very large PDF, write the output incrementally (~1000 tokens per edit) rather than in a single pass.

## Common Patterns

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

## Edge Cases

### Encrypted PDFs

```python
from pypdf import PdfReader

reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("")  # Try empty password first
```

### Corrupted or Invalid PDFs

```python
try:
    with pdfplumber.open("file.pdf") as pdf:
        # process...
except Exception as e:
    print(f"Error processing PDF: {e}")
```

### Very Large PDFs (>100MB)

- Use `pdftotext` for speed
- Process in page batches with pdfplumber
- Avoid loading entire file into memory

### Mixed Content (Some pages scanned, some not)

1. First try standard extraction (`pdftotext`)
2. Check which pages returned empty text
3. Convert only those pages to images and have the LLM read them
