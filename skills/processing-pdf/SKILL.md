---
name: processing-pdf
description: >
  Use when the user needs to extract data from PDFs, work with scanned documents, or manipulate PDF files. Triggers include: "extract text from PDF", "convert PDF to text/CSV/images", "merge/split/rotate PDF", "fill PDF form", "PDF is blank/empty" (likely scanned), or any mention of .pdf files requiring data extraction or transformation. Also use for invoices, receipts, forms, contracts, reports, or any document where structured data (text, tables, form fields) needs to be extracted. For scanned PDFs, convert to images and let the LLM read them.
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

### Decision Guide: Which Tool Should I Use?

```
Need to process a PDF?
│
├─ Extract text?
│  ├─ Try: pdftotext input.pdf output.txt
│  ├─ Got empty output? → PDF is scanned → Use: python3 scripts/to_images.py input.pdf --dpi 200 (then let the LLM read the images)
│  └─ Need page control? → Use: python3 scripts/extract_text.py input.pdf -f 1 -l 5
│
├─ Extract tables?
│  └─ Use: python3 scripts/extract_tables.py input.pdf -o ./tables/
│
├─ Fill a form?
│  ├─ First check fields: python3 scripts/check_forms.py input.pdf
│  ├─ Create JSON with field values
│  └─ Fill: python3 scripts/fill_form.py input.pdf fields.json output.pdf
│
├─ Merge/Split/Rotate?
│  └─ Use pypdf Python examples (see sections below)
│
├─ Convert to images?
│  └─ Use: python3 scripts/to_images.py input.pdf --dpi 300
│
└─ Large file (>50MB)?
   ├─ Quick text: pdftotext (fastest)
   └─ Specific pages: pdftotext -f N -l M for page ranges
```

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

For scanned PDFs (image-based, no selectable text), standard extraction will return empty results. Convert pages to images and let the LLM read them.

### How to Detect a Scanned PDF

Quick test:
```bash
pdftotext document.pdf - | head -20
```
If output is empty or just whitespace, the PDF is scanned.

Programmatic check in Python:
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    text = page.extract_text()
    if not text or not text.strip():
        print("PDF appears to be scanned (image-based)")
```

### Read a Scanned PDF with the LLM

1. Convert pages to images:
   ```bash
   python3 scripts/to_images.py scanned.pdf -o ./scanned-pages/ --dpi 200
   ```
2. Reference or attach the images and ask the LLM to extract text, tables, or structured data.

**Best practices:**
- Use 200 DPI for most documents, 300+ for handwritten or low-quality scans
- Clean up generated images after use: `rm -rf ./scanned-pages/`

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

## Output Format Examples

### Text extraction output
```
=== Page 1 of 5 ===
Invoice #12345
Date: 2024-01-15
Customer: Acme Corp

=== Page 2 of 5 ===
Line Items:
  Widget A    $100.00
  Widget B    $250.00
```

### Table extraction output (CSV)
```csv
Product,Quantity,Price,Total
Widget A,10,100.00,1000.00
Widget B,5,250.00,1250.00
```

### Form field detection output
```
Found 3 fillable form field(s):

  name:
    Type:  /Tx
    Value: (empty)

  email:
    Type:  /Tx
    Value: (empty)

  date:
    Type:  /Tx
    Value: (empty)

To fill these fields, create a JSON file with field names as keys:
{
  "name": "",
  "email": "",
  "date": ""
}
```

## Edge Cases and Error Handling

### Encrypted PDFs
If you encounter "Permission denied" or "encrypted" errors:
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("")  # Try empty password first
    # Or: reader.decrypt("password") if you know it
```

### Corrupted or Invalid PDFs
Always wrap PDF operations in try-except:
```python
try:
    with pdfplumber.open("file.pdf") as pdf:
        # process...
except Exception as e:
    print(f"Error processing PDF: {e}")
    # Fallback: try pdftotext or inform user
```

### Very Large PDFs (>100MB)
- Use `pdftotext` for speed
- Process in page batches with pdfplumber
- Avoid loading entire file into memory

### Mixed Content (Some pages scanned, some not)
1. First try standard extraction
2. Check which pages returned empty text
3. Convert only those pages to images and let the LLM read them
