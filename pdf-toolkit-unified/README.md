# PDF Processing Toolkit

A unified toolkit combining the best of Claude's PDF skills and Docling capabilities, optimized for GitHub Codespaces with Copilot.

## ✨ What's Included

| Feature | Tool | Source |
|---------|------|--------|
| **PDF → Markdown** | Docling | Best structure preservation |
| **Text/Table Extraction** | pdfplumber | Precise positioning |
| **OCR** | Tesseract | Scanned documents |
| **Form Filling** | pypdf | Fillable PDFs |
| **PDF Manipulation** | pypdf | Merge, split, rotate |

## 🚀 Quick Start

### Open in Codespaces
1. Click **Code** → **Codespaces** → **Create codespace**
2. Wait for setup (~2-3 minutes)
3. Start converting PDFs!

### First Commands
```bash
# Convert a single PDF to Markdown
python scripts/pdf_to_markdown.py document.pdf

# Batch convert entire folder
python scripts/pdf_to_markdown.py --batch ./products/ ./output/

# With OCR for scanned documents
python scripts/pdf_to_markdown.py --batch ./scans/ ./output/ --ocr --all
```

## 📋 Script Reference

### pdf_to_clean_json.py (🌟 NEW - Database Workflow)
Complete workflow: PDF → Clean Markdown → Structured JSON for database indexing.

```bash
# Single file
python scripts/pdf_to_clean_json.py product.pdf

# Batch conversion with clean JSON output
python scripts/pdf_to_clean_json.py --batch ./pdfs/ ./output/ --keep-md

# Creates: Individual JSON files + combined database.json
```

**See [docs/DATABASE_WORKFLOW.md](docs/DATABASE_WORKFLOW.md) for complete guide**

### pdf_to_markdown.py (⭐ Primary Tool)
Convert PDFs to structured Markdown using Docling.

```bash
python scripts/pdf_to_markdown.py input.pdf [output_dir]
python scripts/pdf_to_markdown.py --batch ./pdfs/ ./output/ [--ocr] [--json] [--tables] [--all]
```

### extract_content.py
Extract text and tables with pdfplumber.

```bash
python scripts/extract_content.py input.pdf [--tables] [--format xlsx]
python scripts/extract_content.py --batch ./invoices/ --tables -o ./tables/
```

### pdf_tools.py
Merge, split, rotate, and manipulate PDFs.

```bash
python scripts/pdf_tools.py merge file1.pdf file2.pdf -o combined.pdf
python scripts/pdf_tools.py split input.pdf -o ./pages/
python scripts/pdf_tools.py extract input.pdf 1-5,10 -o subset.pdf
python scripts/pdf_tools.py rotate input.pdf 90 -o rotated.pdf
```

### check_form_fields.py
Work with PDF form fields.

```bash
python scripts/check_form_fields.py form.pdf              # Check for fields
python scripts/check_form_fields.py form.pdf --list       # List fields
python scripts/check_form_fields.py form.pdf --extract    # Extract to JSON
python scripts/check_form_fields.py form.pdf --fill values.json -o filled.pdf
```

### ocr_pdf.py
OCR for scanned documents.

```bash
python scripts/ocr_pdf.py scanned.pdf [--format md] [--dpi 300]
python scripts/ocr_pdf.py --batch ./scans/ --format md
```

## 🤖 Using with Copilot

Reference the documentation:
```
@workspace I have 800 PDFs to convert. Help me use pdf_to_markdown.py for batch processing.
```

```
@workspace Read docs/WORKFLOWS.md and help me extract nutrition tables from product PDFs.
```

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Installation & setup instructions
- **[docs/DATABASE_WORKFLOW.md](docs/DATABASE_WORKFLOW.md)** - 🌟 PDF → JSON workflow for databases
- **[docs/WORKFLOWS.md](docs/WORKFLOWS.md)** - Step-by-step workflows
- **[docs/README.md](docs/README.md)** - Full script reference
- **[docs/COPILOT_GUIDE.md](docs/COPILOT_GUIDE.md)** - Using with Copilot

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    PDF Processing Toolkit                       │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Input PDFs         Processing Layer         Output Formats    │
│   ──────────         ────────────────         ──────────────    │
│                                                                  │
│   ┌─────────┐       ┌──────────────┐        ┌───────────────┐  │
│   │ Regular │──────▶│   Docling    │───────▶│   Markdown    │  │
│   │  PDFs   │       │  (structure) │        │     JSON      │  │
│   └─────────┘       └──────────────┘        └───────────────┘  │
│                                                                  │
│   ┌─────────┐       ┌──────────────┐        ┌───────────────┐  │
│   │ Scanned │──────▶│  Tesseract   │───────▶│   Text/MD     │  │
│   │  PDFs   │       │    (OCR)     │        │               │  │
│   └─────────┘       └──────────────┘        └───────────────┘  │
│                                                                  │
│   ┌─────────┐       ┌──────────────┐        ┌───────────────┐  │
│   │  PDFs   │──────▶│  pdfplumber  │───────▶│  Excel/CSV    │  │
│   │ w/Tables│       │   (tables)   │        │     JSON      │  │
│   └─────────┘       └──────────────┘        └───────────────┘  │
│                                                                  │
│   ┌─────────┐       ┌──────────────┐        ┌───────────────┐  │
│   │  PDF    │──────▶│    pypdf     │───────▶│  Filled PDF   │  │
│   │  Forms  │       │   (forms)    │        │               │  │
│   └─────────┘       └──────────────┘        └───────────────┘  │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

## 📦 Dependencies

**Python:**
- docling (document conversion)
- pypdf (PDF manipulation)
- pdfplumber (text/table extraction)
- pytesseract (OCR)
- pdf2image (image conversion)
- pandas (data handling)

**System:**
- poppler-utils
- tesseract-ocr
- qpdf

## 📝 License

MIT License - use freely for your projects.
