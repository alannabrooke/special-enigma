# Database Indexing Workflow

Complete guide for converting PDFs to clean, structured JSON for database indexing.

---

## Overview

This workflow transforms PDF documents into clean, structured JSON data ready for database import.

**Pipeline:**
```
PDF Files → Docling Conversion → Clean Markdown → Extract Structure → JSON Output
```

**Key Features:**
- ✅ Clean, normalized markdown intermediate format
- ✅ Structured JSON with consistent schema
- ✅ Automatic table extraction
- ✅ Metadata preservation
- ✅ Batch processing
- ✅ Database-ready combined output

---

## Quick Start

### Single File Conversion
```bash
python scripts/pdf_to_clean_json.py product.pdf
```

This creates:
- `output/json/product.json` - Structured JSON data

### Batch Conversion
```bash
python scripts/pdf_to_clean_json.py --batch ./pdfs/ ./output/
```

This creates:
- Individual JSON files for each PDF
- `database.json` - Combined database-ready file
- `_processing_summary.json` - Conversion report

---

## JSON Schema

Each converted PDF produces a JSON file with this structure:

```json
{
  "id": "product_filename",
  "source_file": "product.pdf",
  "title": "Product Name",
  "description": "First paragraph or summary",
  "content": "Full cleaned markdown content...",
  "tables": [
    {
      "id": 1,
      "headers": ["Column 1", "Column 2"],
      "rows": [
        ["Row 1 Col 1", "Row 1 Col 2"],
        ["Row 2 Col 1", "Row 2 Col 2"]
      ],
      "raw": "| Column 1 | Column 2 |\n|---|---|..."
    }
  ],
  "metadata": {
    "file_size": 12345,
    "file_modified": "2025-12-01T10:00:00",
    "ocr_used": false,
    "table_count": 2
  },
  "extracted_at": "2025-12-01T10:30:00"
}
```

---

## Command Reference

### Basic Usage

```bash
# Single file (creates product.json)
python scripts/pdf_to_clean_json.py product.pdf

# Specify output directory
python scripts/pdf_to_clean_json.py product.pdf ./my_output/

# Batch mode
python scripts/pdf_to_clean_json.py --batch ./pdfs/ ./output/
```

### Options

| Flag | Description |
|------|-------------|
| `--batch` | Process all PDFs in directory |
| `--ocr` | Enable OCR for scanned documents |
| `--keep-md` | Keep intermediate markdown files |
| `--recursive` | Include subdirectories |

### Examples

```bash
# Basic batch conversion
python scripts/pdf_to_clean_json.py --batch ./pdfs/ ./output/

# With OCR for scanned documents
python scripts/pdf_to_clean_json.py --batch ./scanned_pdfs/ ./output/ --ocr

# Keep markdown files for review
python scripts/pdf_to_clean_json.py --batch ./pdfs/ ./output/ --keep-md

# Process nested directories
python scripts/pdf_to_clean_json.py --batch ./all_products/ ./output/ --recursive
```

---

## Workflow Steps

### Step 1: Prepare Your PDFs

Organize your PDFs in a directory:
```
pdfs/
├── product_001.pdf
├── product_002.pdf
└── product_003.pdf
```

### Step 2: Run Conversion

```bash
python scripts/pdf_to_clean_json.py --batch ./pdfs/ ./output/json/
```

**Output:**
```
======================================================================
PDF → Clean Markdown → JSON Workflow
======================================================================
Input:  pdfs (850 files)
Output: output/json
Options: OCR=off, Keep MD=no
----------------------------------------------------------------------
[1/850] Processing: product_001.pdf... ✓
[2/850] Processing: product_002.pdf... ✓
[3/850] Processing: product_003.pdf... ✓
...
----------------------------------------------------------------------
✓ Successful: 847
✗ Failed: 3

Processing summary: output/json/_processing_summary.json
Combined database: output/json/database.json
```

### Step 3: Review Output

```bash
# Check the combined database
cat output/json/database.json

# View processing summary
cat output/json/_processing_summary.json

# Check a single product
cat output/json/product_001.json | python -m json.tool
```

### Step 4: Handle Failures (if any)

If some files failed:

```bash
# Review failed files in summary
cat output/json/_processing_summary.json | grep -A 3 '"success": false'

# Try with OCR for scanned documents
python scripts/pdf_to_clean_json.py failed_product.pdf ./output/ --ocr
```

---

## Database Import Examples

### PostgreSQL

```sql
-- Create table
CREATE TABLE products (
    id VARCHAR PRIMARY KEY,
    source_file VARCHAR,
    title VARCHAR,
    description TEXT,
    content TEXT,
    tables JSONB,
    metadata JSONB,
    extracted_at TIMESTAMP
);

-- Import from JSON (using a loader script)
-- See examples/postgres_import.py
```

### MongoDB

```javascript
// Import directly
const fs = require('fs');
const database = JSON.parse(fs.readFileSync('output/json/database.json'));

db.products.insertMany(database.products);

// With indexes
db.products.createIndex({ title: "text", description: "text", content: "text" });
db.products.createIndex({ "metadata.table_count": 1 });
```

### Elasticsearch

```bash
# Bulk import
curl -X POST "localhost:9200/products/_bulk" \
  -H 'Content-Type: application/json' \
  --data-binary @output/json/database.ndjson

# Or use Python client (see examples/elasticsearch_import.py)
```

---

## Markdown Cleaning Features

The workflow automatically cleans markdown to ensure consistency:

### What Gets Cleaned:

1. **Whitespace Normalization**
   - Removes excessive blank lines
   - Trims trailing whitespace
   - Normalizes line endings

2. **Heading Cleanup**
   - Ensures proper spacing after `#`
   - Consistent heading hierarchy

3. **Table Formatting**
   - Cleans table borders
   - Normalizes column separators
   - Extracts structured table data

4. **Content Extraction**
   - Identifies title (first H1/H2)
   - Extracts description (first paragraph)
   - Preserves full content for indexing

---

## Advanced Usage

### Custom Processing Script

For advanced needs, you can import the converter:

```python
from scripts.pdf_to_clean_json import PDFToJSONConverter, MarkdownCleaner

# Initialize
converter = PDFToJSONConverter(keep_markdown=True, ocr_enabled=False)

# Convert single file
result = converter.convert_file('product.pdf', 'output')

# Custom post-processing
if result['success']:
    json_path = result['json_path']
    # Add your custom processing here
    print(f"Processed: {json_path}")
```

### Batch with Custom Logic

```python
from pathlib import Path
from scripts.pdf_to_clean_json import PDFToJSONConverter

converter = PDFToJSONConverter()

# Process only files matching pattern
pdf_dir = Path('./pdfs')
for pdf in pdf_dir.glob('*nutrition*.pdf'):
    result = converter.convert_file(str(pdf), 'output/nutrition')
    if result['success']:
        print(f"✓ {pdf.name}")
```

---

## Troubleshooting

### Issue: OCR not working

**Solution:**
```bash
# Install Tesseract OCR
sudo apt-get install tesseract-ocr  # Linux
brew install tesseract              # macOS

# Verify installation
tesseract --version
```

### Issue: Memory errors with large batches

**Solution:**
Process in smaller batches:
```bash
# Split into chunks
ls pdfs/*.pdf | head -100 | xargs -I {} python scripts/pdf_to_clean_json.py {} output/batch1/
ls pdfs/*.pdf | tail -n +101 | head -100 | xargs -I {} python scripts/pdf_to_clean_json.py {} output/batch2/

# Then combine JSON files
python scripts/combine_json.py output/batch*/ output/final/
```

### Issue: Tables not extracted correctly

**Solution:**
1. Check markdown file to see raw table structure (use `--keep-md`)
2. If tables are images, use `--ocr`
3. For complex tables, use `extract_content.py` with pdfplumber:
```bash
python scripts/extract_content.py product.pdf --tables --format xlsx
```

---

## Performance Tips

### For Large Batches (500+ files)

1. **Run overnight** - Let it process unattended
   ```bash
   nohup python scripts/pdf_to_clean_json.py --batch ./pdfs/ ./output/ > conversion.log 2>&1 &
   ```

2. **Monitor progress**
   ```bash
   tail -f conversion.log
   ```

3. **Check status**
   ```bash
   # Count completed files
   ls output/json/*.json | wc -l
   ```

### Optimize Settings

```bash
# Minimal processing (fastest)
python scripts/pdf_to_clean_json.py --batch ./pdfs/ ./output/

# With OCR (slower but necessary for scans)
python scripts/pdf_to_clean_json.py --batch ./pdfs/ ./output/ --ocr

# Keep markdown for debugging (uses more disk space)
python scripts/pdf_to_clean_json.py --batch ./pdfs/ ./output/ --keep-md
```

---

## Output Structure

After running batch conversion:

```
output/
├── json/
│   ├── product_001.json          # Individual product files
│   ├── product_002.json
│   ├── ...
│   ├── database.json              # Combined database-ready file
│   ├── _processing_summary.json  # Conversion report
│   └── markdown/                  # (if --keep-md used)
│       ├── product_001.md
│       └── ...
```

### database.json Structure

```json
{
  "metadata": {
    "created_at": "2025-12-01T10:00:00",
    "total_records": 847,
    "source": "pdfs"
  },
  "products": [
    { /* product 1 data */ },
    { /* product 2 data */ },
    ...
  ]
}
```

---

## Next Steps

1. **Review the output** - Check a few JSON files to ensure quality
2. **Test database import** - Try importing a small batch first
3. **Set up indexing** - Create appropriate indexes for your use case
4. **Build search** - Implement full-text search on content field

For database-specific import examples, see:
- `examples/postgres_import.py`
- `examples/mongodb_import.py`
- `examples/elasticsearch_import.py`
