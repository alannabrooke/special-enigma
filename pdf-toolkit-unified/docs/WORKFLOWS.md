# PDF Processing Workflows

Step-by-step guides for common PDF processing tasks.

---

## Workflow 1: Batch Convert PDFs to Markdown (Docling)

**Goal:** Convert a folder of PDFs to structured Markdown files.

### Step 1: Check Your Files
```bash
# See how many PDFs you have
ls -la ./products/*.pdf | wc -l
```

### Step 2: Run Batch Conversion
```bash
# Basic conversion
python scripts/pdf_to_markdown.py --batch ./products/ ./output/markdown/

# With all features (OCR, JSON, tables)
python scripts/pdf_to_markdown.py --batch ./products/ ./output/markdown/ --all

# For scanned documents
python scripts/pdf_to_markdown.py --batch ./scans/ ./output/ --ocr
```

### Step 3: Review Results
```bash
# Check the summary
cat ./output/markdown/_conversion_summary.json

# View a sample output
head -50 ./output/markdown/sample.md
```

### Step 4: Handle Failures
If some files failed, check the summary for errors and either:
- Fix the source files
- Try with `--ocr` if they're scanned
- Process them individually for debugging

---

## Workflow 2: Extract Tables to Excel

**Goal:** Extract all tables from PDFs and save to Excel.

### Step 1: Single File Test
```bash
python scripts/extract_content.py invoice.pdf --tables --format xlsx
```

### Step 2: Batch Extraction
```bash
python scripts/extract_content.py --batch ./invoices/ --tables --format xlsx -o ./tables/
```

### Step 3: Combine Tables (Python)
If you need all tables in one Excel file:

```python
import pandas as pd
from pathlib import Path

# Find all extracted Excel files
xlsx_files = Path("./tables").glob("*.xlsx")

# Combine into one workbook
with pd.ExcelWriter("all_tables.xlsx") as writer:
    for xlsx_file in xlsx_files:
        df = pd.read_excel(xlsx_file)
        sheet_name = xlsx_file.stem[:31]  # Excel sheet name limit
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Combined all tables into all_tables.xlsx")
```

---

## Workflow 3: Process Scanned Documents (OCR)

**Goal:** Extract text from scanned/image-based PDFs.

### Step 1: Check if PDF Needs OCR
```bash
# Try extracting text normally
python scripts/extract_content.py scanned.pdf --text

# If output is empty or garbled, you need OCR
```

### Step 2: Run OCR
```bash
# Basic OCR
python scripts/ocr_pdf.py scanned.pdf

# High quality with Markdown output
python scripts/ocr_pdf.py scanned.pdf --dpi 300 --format md

# Batch OCR
python scripts/ocr_pdf.py --batch ./scanned_docs/ ./output/ocr/ --format md
```

### Step 3: Alternative: Docling with OCR
```bash
# Docling can also do OCR with better structure preservation
python scripts/pdf_to_markdown.py scanned.pdf --ocr
```

---

## Workflow 4: Fill PDF Forms

**Goal:** Fill out a PDF form programmatically.

### Step 1: Check for Fillable Fields
```bash
python scripts/check_form_fields.py form.pdf
```

**If it has fields:**

### Step 2: Extract Field Information
```bash
python scripts/check_form_fields.py form.pdf --extract -o fields.json

# View the fields
cat fields.json
```

### Step 3: Create Values File
Create `values.json`:
```json
[
  {
    "field_id": "first_name",
    "page": 1,
    "value": "John"
  },
  {
    "field_id": "last_name",
    "page": 1,
    "value": "Smith"
  },
  {
    "field_id": "agree_checkbox",
    "page": 1,
    "value": "/Yes"
  }
]
```

### Step 4: Fill the Form
```bash
python scripts/check_form_fields.py form.pdf --fill values.json -o filled_form.pdf
```

---

## Workflow 5: Merge Multiple PDFs

**Goal:** Combine several PDFs into one.

### Simple Merge
```bash
python scripts/pdf_tools.py merge doc1.pdf doc2.pdf doc3.pdf -o combined.pdf
```

### Merge All PDFs in Directory
```bash
# Bash one-liner
python scripts/pdf_tools.py merge $(ls ./reports/*.pdf) -o all_reports.pdf
```

### Merge with Specific Order
Create a list file and process:
```bash
# files.txt contains one PDF path per line
cat files.txt | xargs python scripts/pdf_tools.py merge -o combined.pdf
```

---

## Workflow 6: Split PDF into Chapters

**Goal:** Split a large PDF into sections.

### Split into Individual Pages
```bash
python scripts/pdf_tools.py split large_document.pdf -o ./pages/
```

### Extract Specific Pages
```bash
# Extract pages 1-10
python scripts/pdf_tools.py extract document.pdf 1-10 -o chapter1.pdf

# Extract pages 11-20
python scripts/pdf_tools.py extract document.pdf 11-20 -o chapter2.pdf

# Extract non-contiguous pages
python scripts/pdf_tools.py extract document.pdf 1-5,10,15-20 -o selected.pdf
```

---

## Workflow 7: Ultimate Nutrition Product Processing

**Goal:** Process the Ultimate Nutrition product PDFs for structured data extraction.

### Step 1: Inventory
```bash
# Count PDFs
ls -la "./Ultimate Nutrition Product Line/"*.pdf | wc -l

# Check a sample
python scripts/pdf_to_markdown.py "./Ultimate Nutrition Product Line/Amino 2000.pdf"
cat ./output/markdown/Amino\ 2000.md
```

### Step 2: Batch Convert with Tables
```bash
python scripts/pdf_to_markdown.py \
    --batch "./Ultimate Nutrition Product Line/" \
    ./output/products/ \
    --all
```

### Step 3: Review and Fix Issues
```bash
# Check summary
cat ./output/products/_conversion_summary.json | python -m json.tool

# View any failures
grep -A1 '"success": false' ./output/products/_conversion_summary.json
```

### Step 4: If Products are Scanned
```bash
# Re-run with OCR
python scripts/pdf_to_markdown.py \
    --batch "./Ultimate Nutrition Product Line/" \
    ./output/products/ \
    --ocr --all
```

### Step 5: Extract Nutrition Tables Separately
```bash
python scripts/extract_content.py \
    --batch "./Ultimate Nutrition Product Line/" \
    --tables --format xlsx \
    -o ./output/nutrition_tables/
```

---

## Workflow 8: Custom Processing Script

**Goal:** Create a custom script that chains multiple operations.

### Example: Smart PDF Processor
```python
#!/usr/bin/env python3
"""
smart_process.py - Automatically detect and process PDFs appropriately.
"""

import sys
from pathlib import Path

# Import toolkit scripts
sys.path.insert(0, str(Path(__file__).parent))
from scripts.extract_content import ContentExtractor
from scripts.pdf_to_markdown import PDFToMarkdownConverter, ConversionOptions

def has_extractable_text(pdf_path: str) -> bool:
    """Check if PDF has extractable text (not scanned)."""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:3]:  # Check first 3 pages
                text = page.extract_text()
                if text and len(text.strip()) > 100:
                    return True
        return False
    except:
        return False

def process_pdf(pdf_path: str, output_dir: str):
    """Process a single PDF with appropriate method."""
    pdf_path = Path(pdf_path)
    
    # Check if scanned
    is_scanned = not has_extractable_text(str(pdf_path))
    
    # Configure options
    options = ConversionOptions(
        output_dir=output_dir,
        ocr_enabled=is_scanned,
        save_json=True,
        extract_tables=True
    )
    
    # Convert
    converter = PDFToMarkdownConverter(options)
    result = converter.convert_file(str(pdf_path))
    
    method = "OCR" if is_scanned else "text"
    print(f"Processed with {method}: {pdf_path.name}")
    
    return result

# Usage
if __name__ == "__main__":
    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    if Path(input_path).is_dir():
        for pdf in Path(input_path).glob("*.pdf"):
            process_pdf(str(pdf), output_dir)
    else:
        process_pdf(input_path, output_dir)
```

---

## Performance Tips

### For Large Batches (100+ files)
1. Run overnight in Codespaces
2. Use `nohup` to prevent disconnection:
   ```bash
   nohup python scripts/pdf_to_markdown.py --batch ./large_folder/ ./output/ --all > conversion.log 2>&1 &
   ```
3. Monitor progress:
   ```bash
   tail -f conversion.log
   ```

### For Slow Conversions
1. Disable OCR if not needed
2. Skip JSON/tables if not needed
3. Use lower DPI for OCR (150 instead of 200)

### For Memory Issues
1. Process in smaller batches
2. Clear the output folder between runs
3. Restart the Codespace if needed
