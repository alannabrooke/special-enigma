#!/bin/bash
set -e

echo "=============================================="
echo "  PDF Processing Toolkit - Setup"
echo "=============================================="
echo ""

# System dependencies
echo "[1/4] Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    qpdf \
    libgl1-mesa-glx \
    libglib2.0-0 \
    > /dev/null

echo "  ✓ poppler-utils (pdftotext, pdfimages, pdftoppm)"
echo "  ✓ tesseract-ocr (OCR engine)"
echo "  ✓ qpdf (PDF manipulation)"

# Python dependencies
echo ""
echo "[2/4] Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "  ✓ Core: pypdf, pdfplumber, reportlab"
echo "  ✓ OCR: pytesseract, pdf2image, Pillow"
echo "  ✓ Data: pandas, openpyxl"
echo "  ✓ Docling: document conversion"

# Verify installations
echo ""
echo "[3/4] Verifying installations..."

python -c "import pypdf; print('  ✓ pypdf', pypdf.__version__)" 2>/dev/null || echo "  ⚠ pypdf not installed"
python -c "import pdfplumber; print('  ✓ pdfplumber')" 2>/dev/null || echo "  ⚠ pdfplumber not installed"
python -c "import docling; print('  ✓ docling')" 2>/dev/null || echo "  ⚠ docling not installed"

pdftotext -v 2>&1 | head -1 | sed 's/^/  ✓ /' || echo "  ⚠ pdftotext not available"
tesseract --version 2>&1 | head -1 | sed 's/^/  ✓ /' || echo "  ⚠ tesseract not available"

# Create output directories
echo ""
echo "[4/4] Creating directories..."
mkdir -p output/markdown output/json output/images output/tables
echo "  ✓ output/markdown"
echo "  ✓ output/json"
echo "  ✓ output/images"
echo "  ✓ output/tables"

# Done
echo ""
echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "QUICK START COMMANDS:"
echo ""
echo "  📄 Convert PDF to Markdown (Docling):"
echo "     python scripts/pdf_to_markdown.py input.pdf"
echo "     python scripts/pdf_to_markdown.py --batch ./pdfs/"
echo ""
echo "  📋 Extract text/tables (pdfplumber):"
echo "     python scripts/extract_content.py input.pdf"
echo ""
echo "  📝 Fill PDF forms:"
echo "     python scripts/check_form_fields.py input.pdf"
echo ""
echo "  🔧 Manipulate PDFs (merge/split/rotate):"
echo "     python scripts/pdf_tools.py merge file1.pdf file2.pdf -o merged.pdf"
echo "     python scripts/pdf_tools.py split input.pdf"
echo ""
echo "DOCUMENTATION:"
echo "  docs/README.md              - Start here!"
echo "  docs/COPILOT_GUIDE.md       - How to use with Copilot"
echo "  docs/WORKFLOWS.md           - Step-by-step workflows"
echo ""
