# Setup Guide - PDF Toolkit Unified

Quick setup instructions for getting the PDF toolkit working on your system.

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

---

## Installation Options

### Option 1: Virtual Environment (Recommended)

This keeps dependencies isolated and clean:

```bash
# Navigate to the toolkit directory
cd /Users/alannaembury/Desktop/Repositories/special-enigma/pdf-toolkit-unified

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python scripts/pdf_to_clean_json.py --help
```

### Option 2: User Installation

Install packages for your user only (doesn't require sudo):

```bash
cd /Users/alannaembury/Desktop/Repositories/special-enigma/pdf-toolkit-unified

# Install with --user flag
python3 -m pip install --user -r requirements.txt

# Verify
python3 scripts/pdf_to_clean_json.py --help
```

### Option 3: System Packages (macOS)

If you prefer system-wide installation:

```bash
cd /Users/alannaembury/Desktop/Repositories/special-enigma/pdf-toolkit-unified

# Install with break-system-packages (macOS Homebrew Python)
python3 -m pip install --break-system-packages -r requirements.txt

# Or use pipx for isolated app installation
brew install pipx
pipx install docling
```

---

## Quick Test

After installation, test with a single PDF:

```bash
# Test the conversion script
python3 scripts/pdf_to_clean_json.py pdfs/105_Amino2000_snf.pdf

# Check output
cat output/json/105_Amino2000_snf.json
```

---

## Running the Workflow

### For Your Product PDFs

```bash
# Activate virtual environment (if using Option 1)
source venv/bin/activate

# Run batch conversion on all PDFs
python3 scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --keep-md

# Check results
ls -la output/products/
cat output/products/database.json
```

### Expected Output

```
output/
└── products/
    ├── 105_Amino2000_snf.json
    ├── 141_ProWhey_snf.json
    ├── ... (all your product PDFs as JSON)
    ├── database.json              # Combined database file
    ├── _processing_summary.json   # Conversion report
    └── markdown/                  # Clean markdown files
        ├── 105_Amino2000_snf.md
        └── ...
```

---

## Dependencies Explained

From `requirements.txt`:

| Package | Purpose |
|---------|---------|
| `docling` | PDF to Markdown conversion (primary tool) |
| `pypdf` | PDF manipulation (merge, split, forms) |
| `pdfplumber` | Text and table extraction |
| `pytesseract` | OCR for scanned documents |
| `pdf2image` | Convert PDF pages to images |
| `pandas` | Table data handling |

---

## Troubleshooting

### Issue: "command not found: pip"

Use `python3 -m pip` instead:
```bash
python3 -m pip install <package>
```

### Issue: "externally-managed-environment"

This is common on macOS with Homebrew Python. Use virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "No module named 'docling'"

Install docling:
```bash
source venv/bin/activate  # if using venv
pip install docling
```

### Issue: OCR not working

Install Tesseract:
```bash
# macOS
brew install tesseract

# Verify
tesseract --version
```

---

## Next Steps

1. ✅ Complete installation using one of the options above
2. ✅ Test with a single PDF
3. ✅ Run batch conversion on your PDFs folder
4. ✅ Review the generated JSON files
5. ✅ Import into your database

See `docs/DATABASE_WORKFLOW.md` for detailed usage instructions.
