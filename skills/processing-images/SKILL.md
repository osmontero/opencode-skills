---
name: processing-images
description: Use when the user needs to analyze images (PNG, JPG, JPEG, GIF, WEBP, BMP, TIFF) using AI vision. Triggers include: "analyze this image", "what's in this picture", "extract text from screenshot", "describe this chart/graph/diagram", "read the text in this image", "what does this image show", image file extensions (.png .jpg .jpeg .gif .webp .bmp .tiff), URLs ending in image formats. Also use for screenshots, scanned documents as images, photos with text, charts, graphs, diagrams, forms, receipts, or any visual content requiring AI interpretation.
---

# Image Processing with AI Vision

Analyze images using the ThreatWinds AI vision API (Qwen 3.6). Extract text, describe content, identify objects, read charts and diagrams, and answer questions about visual content.

## Prerequisites

Before running any Python scripts, **activate the opencode virtual environment**:

```bash
source ~/.local/opencode-venv/bin/activate
```

Set your ThreatWinds API credentials:
```bash
export THREATWINDS_API_KEY="your-key-here"
# Optional for some API configurations:
export THREATWINDS_API_SECRET="your-secret-here"
```

## Quick Start

### Analyze a local image

```bash
python3 scripts/analyze_image.py screenshot.png
```

### Analyze an image from a URL

```bash
python3 scripts/analyze_image.py https://example.com/chart.jpg
```

### Custom prompt for specific extraction

```bash
python3 scripts/analyze_image.py form.png \
  --prompt "Extract all field names and their values from this form. Output as a list."
```

### Specify model and token limits

```bash
python3 scripts/analyze_image.py image.jpg --model qwen-3.6 --max-tokens 2048
```

## Supported Image Formats

- PNG (`.png`)
- JPEG/JPG (`.jpg`, `.jpeg`)
- GIF (`.gif`)
- WebP (`.webp`)
- BMP (`.bmp`)
- TIFF/TIF (`.tiff`, `.tif`)

## Common Use Cases

### Extract text from a screenshot

```bash
python3 scripts/analyze_image.py screenshot.png \
  --prompt "Extract all visible text from this screenshot. Preserve the layout and structure."
```

### Describe a chart or graph

```bash
python3 scripts/analyze_image.py chart.png \
  --prompt "Describe this chart. What type of chart is it? What are the key data points and trends?"
```

### Read a form or receipt

```bash
python3 scripts/analyze_image.py receipt.jpg \
  --prompt "Extract the merchant name, date, line items, quantities, prices, and total from this receipt."
```

### Analyze a diagram

```bash
python3 scripts/analyze_image.py diagram.png \
  --prompt "Describe this diagram. What are the components and how are they connected?"
```

### Identify objects in a photo

```bash
python3 scripts/analyze_image.py photo.jpg \
  --prompt "What objects do you see in this photo? Describe them in detail."
```

## Script Usage

### Basic syntax

```bash
python3 scripts/analyze_image.py <image_path_or_url> [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-p, --prompt` | Custom prompt for the vision model | Generic description prompt |
| `--model` | Model ID to use | `qwen-3.6` |
| `--api-key` | ThreatWinds API key (or use `THREATWINDS_API_KEY` env var) | From env var |
| `--api-secret` | ThreatWinds API secret (optional) | From env var |
| `--max-tokens` | Maximum output tokens | `4096` |

### Examples

**Analyze a local PNG:**
```bash
python3 scripts/analyze_image.py ./screenshot.png
```

**Analyze a URL:**
```bash
python3 scripts/analyze_image.py https://example.com/image.jpg
```

**With a custom prompt:**
```bash
python3 scripts/analyze_image.py chart.png --prompt "What trends do you see in this chart?"
```

**With explicit API key:**
```bash
python3 scripts/analyze_image.py image.png --api-key "tw-..."
```

## Python Module Usage

For custom workflows, use the Python module directly:

```python
from vision.analysis_service import analyze_image_source

# From a local file
result = analyze_image_source(
    prompt="Describe this image in detail",
    model="qwen-3.6",
    max_tokens=4096,
    image_path="screenshot.png"
)
print(result.content)

# From a URL
result = analyze_image_source(
    prompt="What text is visible in this image?",
    model="qwen-3.6",
    max_tokens=4096,
    image_url="https://example.com/image.jpg"
)
print(result.content)

# From base64-encoded image data
result = analyze_image_source(
    prompt="Analyze this image",
    model="qwen-3.6",
    max_tokens=4096,
    image_base64="iVBORw0KGgoAAAANSUhEUgAA..."
)
print(result.content)
```

## Prompt Templates

### Text extraction
```
Extract all visible text from this image. Preserve the layout and structure as much as possible. If there are multiple sections, separate them clearly.
```

### Chart analysis
```
Analyze this chart. Identify:
1. The type of chart (bar, line, pie, scatter, etc.)
2. The axes labels and units
3. The data series and their values
4. Key trends or insights
```

### Form extraction
```
Extract all form fields from this image. For each field, provide:
- Field label/name
- Field value (if filled)
- Field type (text, checkbox, dropdown, etc.)
```

### Document description
```
Describe this document image in detail. What type of document is it? What sections or elements does it contain? What is the overall purpose?
```

## Error Handling

### API key errors
If you see `THREATWINDS_API_KEY is required`, set the environment variable:
```bash
export THREATWINDS_API_KEY="your-key-here"
```

### Network errors
If the request times out or fails:
- Check your internet connection
- Verify the API key is valid
- For large images, ensure they're accessible (especially for URLs)

### Unsupported image format
If the image format is not supported, you'll see an error mentioning the file type. Convert the image to PNG or JPEG first.

### Large images
For very large images (>10MB):
- Consider resizing before analysis
- The API may have size limits on uploaded images

## Tips for Better Results

1. **Be specific in prompts**: Instead of "analyze this", try "extract all email addresses and phone numbers from this business card"

2. **High-resolution images work better**: Text extraction is more accurate with clearer, higher-resolution images

3. **Break down complex tasks**: For images with multiple elements, ask for each part separately

4. **Specify output format**: Tell the model how you want the output (list, table, JSON, etc.)

## Troubleshooting

**Q: The text extraction seems incomplete**
- Try a higher-resolution image
- Add more specific instructions about what text to extract
- Check if the image is blurry or has poor contrast

**Q: The description is too brief**
- Increase `--max-tokens` to allow longer responses
- Add "in detail" or "thoroughly" to your prompt

**Q: URL images aren't loading**
- Verify the URL is publicly accessible
- Check that the URL ends with an image extension
- Try downloading the image first and analyzing locally

## Output Format

The script outputs the model's response directly to stdout. For programmatic use, capture the output:

```bash
result=$(python3 scripts/analyze_image.py image.png --prompt "Extract the title")
echo "$result"
```

## Comparison with PDF Processing

| Feature | processing-images | processing-pdf |
|---------|------------------|----------------|
| Input | Single images | Multi-page PDFs |
| Vision analysis | ✓ | ✓ (via page rendering) |
| Text extraction | ✓ | ✓ (pdftotext + vision) |
| Table extraction | ✓ (via vision) | ✓ (pdfplumber + vision) |
| Form filling | ✗ | ✓ |
| Page operations | ✗ | ✓ (merge/split/rotate) |

Use `processing-images` for standalone image files. Use `processing-pdf` for PDF documents (even scanned ones).
