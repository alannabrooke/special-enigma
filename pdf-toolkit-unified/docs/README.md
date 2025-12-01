# PDF Processing Toolkit Documentation

A unified toolkit combining the best of Claude's PDF skills and Docling capabilities, designed for GitHub Codespaces with Copilot.

## 🎯 What This Toolkit Does

| Capability | Tool | Best For |
|------------|------|----------|
| **PDF → Markdown** | `pdf_to_markdown.py` | Structured document conversion with Docling |
| **Text/Table Extraction** | `extract_content.py` | Precise extraction with pdfplumber |
| **OCR** | `ocr_pdf.py` | Scanned/image-based documents |
| **Form Filling** | `check_form_fields.py` | Fillable PDF forms |
| **PDF Manipulation** | `pdf_tools.py` | Merge, split, rotate, watermark |

## 🚀 Quick Start

### In Codespaces:
```bash
# The setup runs automatically, but you can re-run:
bash setup.sh

# Convert a PDF to Markdown
python scripts/pdf_to_markdown.py document.pdf

# Batch convert all PDFs
python scripts/pdf_to_markdown.py --batch ./pdfs/ ./output/
```

## 📁 Directory Structure

```
pdf-toolkit-unified/
├── scripts/
│   ├── pdf_to_markdown.py     # Main Docling converter
│   ├── extract_content.py     # pdfplumber extraction
│   ├── pdf_tools.py           # Merge, split, rotate
│   ├── check_form_fields.py   # Form field operations
│   └── ocr_pdf.py             # OCR with Tesseract
├── docs/
│   ├── README.md              # This file
│   ├── COPILOT_GUIDE.md       # How to use with Copilot
│   └── WORKFLOWS.md           # Step-by-step workflows
├── output/                     # Default output directory
│   ├── markdown/
│   ├── json/
│   ├── images/
│   └── tables/
└── examples/                   # Sample files
```

## 🔧 Script Reference

### pdf_to_markdown.py (Docling)
**The primary conversion tool.** Uses Docling to convert PDFs while preserving document structure.

```bash
# Basic conversion
python scripts/pdf_to_markdown.py input.pdf

# With output directory
python scripts/pdf_to_markdown.py input.pdf ./output/

# Batch mode
python scripts/pdf_to_markdown.py --batch ./pdfs/ ./output/

# All options
python scripts/pdf_to_markdown.py --batch ./pdfs/ ./output/ --ocr --json --tables --all
```

**Options:**
- `--batch` - Process directory of PDFs
- `--ocr` - Enable OCR for scanned documents
- `--json` - Also save JSON structure
- `--tables` - Extract tables to CSV
- `--all` - Enable all output options
- `--recursive` - Include subdirectories

### extract_content.py (pdfplumber)
**Precise text and table extraction.** Use when you need exact positioning or clean table data.

```bash
# Extract everything
python scripts/extract_content.py document.pdf

# Tables only to Excel
python scripts/extract_content.py document.pdf --tables --format xlsx

# Batch extraction
python scripts/extract_content.py --batch ./invoices/ -o ./extracted/
```

### pdf_tools.py
**PDF manipulation utilities.**

```bash
# Merge PDFs
python scripts/pdf_tools.py merge file1.pdf file2.pdf -o combined.pdf

# Split into pages
python scripts/pdf_tools.py split document.pdf -o ./pages/

# Rotate pages
python scripts/pdf_tools.py rotate input.pdf 90 -o rotated.pdf

# Extract specific pages
python scripts/pdf_tools.py extract input.pdf 1-5,10,15-20 -o subset.pdf

# Show PDF info
python scripts/pdf_tools.py info document.pdf

# Add watermark
python scripts/pdf_tools.py watermark input.pdf watermark.pdf -o output.pdf

# Encrypt
python scripts/pdf_tools.py encrypt input.pdf mypassword -o encrypted.pdf
```

### check_form_fields.py
**PDF form operations.**

```bash
# Check for form fields
python scripts/check_form_fields.py form.pdf

# List all fields
python scripts/check_form_fields.py form.pdf --list

# Extract field info
python scripts/check_form_fields.py form.pdf --extract -o fields.json

# Fill form
python scripts/check_form_fields.py form.pdf --fill values.json -o filled.pdf
```

### ocr_pdf.py
**OCR for scanned documents.**

```bash
# Basic OCR to text
python scripts/ocr_pdf.py scanned.pdf

# OCR to Markdown
python scripts/ocr_pdf.py scanned.pdf --format md

# Batch OCR
python scripts/ocr_pdf.py --batch ./scanned/ ./output/ --format txt
```

## 📚 When to Use What

| Situation | Use This | Why |
|-----------|----------|-----|
| Convert documents to Markdown | `pdf_to_markdown.py` | Preserves structure (headings, lists, tables) |
| Extract tables to Excel | `extract_content.py --tables --format xlsx` | Clean table extraction |
| Scanned/image PDFs | `ocr_pdf.py` or `pdf_to_markdown.py --ocr` | OCR capabilities |
| Fill out forms | `check_form_fields.py` | Form field detection/filling |
| Merge/split PDFs | `pdf_tools.py` | Fast PDF manipulation |
| Extract specific regions | `extract_content.py` (with Python API) | Precise positioning |

## 🤖 Using with Copilot

See [COPILOT_GUIDE.md](COPILOT_GUIDE.md) for detailed instructions on using this toolkit with GitHub Copilot in Codespaces.

**Quick example:**
> "@workspace I have 800 PDFs in the products folder. Help me convert them all to Markdown using the pdf_to_markdown.py script."

## ⚡ Performance Tips

1. **Batch processing** is faster than individual files
2. **Disable OCR** if PDFs aren't scanned (it's slower)
3. **Use --recursive** for nested directories
4. **Check the summary file** after batch processing

## 🔍 Troubleshooting

### "docling not installed"
```bash
pip install docling
```

### "tesseract not found"
```bash
sudo apt-get install tesseract-ocr
```

### "poppler not found" (pdf2image error)
```bash
sudo apt-get install poppler-utils
```

### Poor OCR quality
- Increase DPI: `--dpi 300`
- Check language: `--lang deu` for German, etc.
- Scans should be at least 200 DPI

## 📖 Further Reading

- [WORKFLOWS.md](WORKFLOWS.md) - Step-by-step workflows for common tasks
- [COPILOT_GUIDE.md](COPILOT_GUIDE.md) - Using with GitHub Copilot
