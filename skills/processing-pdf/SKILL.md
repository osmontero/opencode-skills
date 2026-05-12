---
name: processing-pdf
description: >
  Use when the user needs to read, extract data from, or work with PDF files. Converts PDF pages to PNG images so the LLM can read them natively. Triggers include: "extract text from PDF", "read this PDF", "what does this PDF say", "summarize this PDF", PDF file paths or extensions (.pdf), or any mention of .pdf files requiring data extraction or analysis.
---

# PDF Processing

Convert PDF pages to PNG images so the LLM can read them directly.

## How It Works

1. Convert each PDF page to a PNG image using `scripts/to_images.py`
2. Send the images to the LLM (OpenCode handles images natively)
3. Ask the LLM to extract text, tables, fill forms, or answer questions

## Convert PDF to Images

```bash
# All pages (default: 150 DPI PNGs)
python3 scripts/to_images.py document.pdf -o ./pdf-pages/

# Higher quality for detailed documents
python3 scripts/to_images.py document.pdf -o ./pdf-pages/ --dpi 200

# Specific page range — use pypdf to split first
python3 -c "
from pypdf import PdfReader, PdfWriter
reader = PdfReader('document.pdf')
writer = PdfWriter()
for i in range(2, 5):  # pages 3-5
    writer.add_page(reader.pages[i])
with open('pages_3_5.pdf', 'wb') as f:
    writer.write(f)
" && python3 scripts/to_images.py pages_3_5.pdf -o ./pdf-pages/ --dpi 200
```

Then simply reference or attach the generated PNGs and ask the LLM to do the work:

- "Extract all text from these images"
- "What tables are in these pages?"
- "Summarize this document"
- "Extract the invoice number, line items, and total"

## Tips

- **150 DPI** is sufficient for most documents
- **200-300 DPI** for handwritten content or low-quality scans
- For large PDFs, convert pages in batches to avoid generating too many images at once
- Clean up generated images after use: `rm -rf ./pdf-pages/`
