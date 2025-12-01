# Quick Start - Your Product PDFs to Database

Fast setup guide for converting your product PDFs to clean JSON for database indexing.

---

## 🎯 Goal

Convert all PDFs in `/pdfs/` directory to structured JSON files ready for database import.

---

## Step 1: Setup (One-time)

```bash
# Navigate to toolkit directory
cd /Users/alannaembury/Desktop/Repositories/special-enigma/pdf-toolkit-unified

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install docling pypdf pdfplumber pandas
```

---

## Step 2: Convert Your PDFs

```bash
# Make sure virtual environment is active
source venv/bin/activate

# Run batch conversion on all product PDFs
python3 scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --keep-md
```

**What this does:**
- Processes all PDFs in the `../pdfs/` directory
- Creates clean markdown files (for review)
- Generates structured JSON for each PDF
- Creates a combined `database.json` file
- Produces a processing summary report

---

## Step 3: Review Output

```bash
# Check how many files were processed
ls -la output/products/*.json | wc -l

# View the combined database file
cat output/products/database.json | python3 -m json.tool | head -50

# Check processing summary
cat output/products/_processing_summary.json | python3 -m json.tool

# View a single product
cat output/products/105_Amino2000_snf.json | python3 -m json.tool
```

---

## Step 4: Check the JSON Structure

Each JSON file contains:

```json
{
  "id": "product_filename",
  "source_file": "product.pdf",
  "title": "Product Name",
  "description": "First paragraph...",
  "content": "Full clean markdown content...",
  "tables": [
    {
      "id": 1,
      "headers": ["Nutrition", "Per Serving"],
      "rows": [["Calories", "120"], ["Protein", "25g"]],
      "raw": "markdown table..."
    }
  ],
  "metadata": {
    "file_size": 12345,
    "table_count": 2,
    "ocr_used": false
  },
  "extracted_at": "2025-12-01T..."
}
```

---

## Step 5: Import to Database

### Option A: Use Combined File

The `database.json` file contains all products in one file:

```json
{
  "metadata": {
    "created_at": "2025-12-01T...",
    "total_records": 850
  },
  "products": [
    { /* product 1 */ },
    { /* product 2 */ },
    ...
  ]
}
```

Import this directly into your database.

### Option B: Process Individual Files

```python
import json
from pathlib import Path

# Load all individual JSON files
json_dir = Path('output/products')
for json_file in json_dir.glob('*.json'):
    if json_file.name.startswith('_'):
        continue  # Skip summary files

    data = json.loads(json_file.read_text())
    # Import to your database
    print(f"Importing: {data['title']}")
```

---

## Common Commands

### Run for First Time
```bash
cd /Users/alannaembury/Desktop/Repositories/special-enigma/pdf-toolkit-unified
source venv/bin/activate
python3 scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --keep-md
```

### Process Scanned PDFs (with OCR)
```bash
python3 scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --ocr --keep-md
```

### Single File Test
```bash
python3 scripts/pdf_to_clean_json.py ../pdfs/105_Amino2000_snf.pdf ./test_output/
```

### View Help
```bash
python3 scripts/pdf_to_clean_json.py --help
```

---

## Troubleshooting

### If you get "No module named 'docling'"
```bash
source venv/bin/activate
pip install docling
```

### If conversion fails for some files
Check the processing summary:
```bash
cat output/products/_processing_summary.json | grep -A 3 '"success": false'
```

Try those files with OCR:
```bash
python3 scripts/pdf_to_clean_json.py failed_file.pdf ./output/retry/ --ocr
```

### To start fresh
```bash
# Delete output and reprocess
rm -rf output/products
python3 scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --keep-md
```

---

## Next Steps

1. ✅ Complete setup (Step 1)
2. ✅ Run conversion (Step 2)
3. ✅ Review JSON files (Step 3-4)
4. ✅ Import to your database (Step 5)
5. ✅ Set up search/indexing on the `content` field

For detailed information, see:
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed installation options
- **[docs/DATABASE_WORKFLOW.md](docs/DATABASE_WORKFLOW.md)** - Complete workflow guide
