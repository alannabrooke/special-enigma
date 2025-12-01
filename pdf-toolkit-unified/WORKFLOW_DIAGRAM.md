# PDF to Database Workflow - Visual Guide

## Complete Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PDF TO DATABASE WORKFLOW                          │
└─────────────────────────────────────────────────────────────────────┘

STEP 1: INPUT
┌──────────────┐
│  Your PDFs   │
│  (850 files) │
│              │
│ 📄 Product 1 │
│ 📄 Product 2 │
│ 📄 ...       │
└──────┬───────┘
       │
       ▼

STEP 2: CONVERSION (pdf_to_clean_json.py)
┌──────────────────────────────────────────┐
│  Docling PDF Converter                   │
│  • Extracts text & structure             │
│  • Preserves tables                      │
│  • Handles scanned docs (OCR optional)   │
└──────────────┬───────────────────────────┘
               │
               ▼

STEP 3: MARKDOWN CLEANING
┌──────────────────────────────────────────┐
│  MarkdownCleaner                         │
│  • Remove excess whitespace              │
│  • Normalize headings                    │
│  • Clean table formatting                │
│  • Extract title & description           │
└──────────────┬───────────────────────────┘
               │
               ▼

STEP 4: DATA EXTRACTION
┌──────────────────────────────────────────┐
│  Structured Data Extractor               │
│  • Title (first H1/H2)                   │
│  • Description (first paragraph)         │
│  • Tables → headers + rows               │
│  • Metadata (file size, dates, etc.)     │
└──────────────┬───────────────────────────┘
               │
               ▼

STEP 5: JSON OUTPUT
┌──────────────┬───────────────┬────────────────┐
│              │               │                │
│ product1.json│ product2.json │ database.json  │
│ {            │ {             │ {              │
│   id: "..."  │   id: "..."   │   metadata: {} │
│   title: ""  │   title: ""   │   products: [  │
│   content: ""│   content: "" │     {...},     │
│   tables: [] │   tables: []  │     {...}      │
│ }            │ }             │   ]            │
│              │               │ }              │
└──────────────┴───────────────┴────────────────┘
               │
               ▼

STEP 6: DATABASE IMPORT
┌────────────┬──────────────┬─────────────────┐
│            │              │                 │
│ PostgreSQL │   MongoDB    │  Elasticsearch  │
│            │              │                 │
│ [Table]    │ [Collection] │    [Index]      │
│  products  │   products   │    products     │
│            │              │                 │
└────────────┴──────────────┴─────────────────┘
```

---

## Detailed Data Flow

### Input: PDF File
```
product.pdf
├── Pages
├── Text content
├── Tables
└── Images (optional)
```

### Processing: Markdown
```markdown
# Product Title

Product description paragraph with details...

## Nutritional Information

| Nutrient | Amount |
|----------|--------|
| Protein  | 25g    |
| Calories | 120    |

## Ingredients

List of ingredients...
```

### Output: JSON
```json
{
  "id": "product",
  "source_file": "product.pdf",
  "title": "Product Title",
  "description": "Product description paragraph with details...",
  "content": "# Product Title\n\nProduct description...",
  "tables": [
    {
      "id": 1,
      "headers": ["Nutrient", "Amount"],
      "rows": [
        ["Protein", "25g"],
        ["Calories", "120"]
      ],
      "raw": "| Nutrient | Amount |..."
    }
  ],
  "metadata": {
    "file_size": 12345,
    "file_modified": "2025-12-01T10:00:00",
    "ocr_used": false,
    "table_count": 1
  },
  "extracted_at": "2025-12-01T10:30:00"
}
```

---

## Command Flow

### Single File
```
Input:  product.pdf
   ↓
Command: python3 scripts/pdf_to_clean_json.py product.pdf
   ↓
Output: output/json/product.json
```

### Batch Processing
```
Input:  pdfs/ (850 files)
   ↓
Command: python3 scripts/pdf_to_clean_json.py --batch pdfs/ output/ --keep-md
   ↓
Output:
  ├── output/product1.json
  ├── output/product2.json
  ├── output/...
  ├── output/database.json (combined)
  ├── output/_processing_summary.json
  └── output/markdown/ (optional)
      ├── product1.md
      └── ...
```

---

## Options & Flags

```
┌────────────────────────────────────────────────────────────┐
│  COMMAND OPTIONS                                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  --batch          Process entire directory                │
│  --ocr            Enable OCR for scanned documents        │
│  --keep-md        Keep markdown intermediate files        │
│  --recursive      Include subdirectories                  │
│                                                            │
└────────────────────────────────────────────────────────────┘

EXAMPLES:

Basic:     python3 scripts/pdf_to_clean_json.py --batch pdfs/ output/
With OCR:  python3 scripts/pdf_to_clean_json.py --batch pdfs/ output/ --ocr
Keep MD:   python3 scripts/pdf_to_clean_json.py --batch pdfs/ output/ --keep-md
All:       python3 scripts/pdf_to_clean_json.py --batch pdfs/ output/ --ocr --keep-md
```

---

## File Organization

### Before Processing
```
/Users/alannaembury/Desktop/Repositories/special-enigma/
├── pdfs/
│   ├── 105_Amino2000_snf.pdf
│   ├── 141_ProWhey_snf.pdf
│   ├── 410_Taurine_snf.pdf
│   └── ... (850 files)
└── pdf-toolkit-unified/
    └── scripts/
        └── pdf_to_clean_json.py
```

### After Processing
```
/Users/alannaembury/Desktop/Repositories/special-enigma/
├── pdfs/
│   └── ... (original PDFs unchanged)
└── pdf-toolkit-unified/
    ├── scripts/
    └── output/
        └── products/
            ├── 105_Amino2000_snf.json     ┐
            ├── 141_ProWhey_snf.json       │ Individual
            ├── 410_Taurine_snf.json       │ JSON files
            ├── ...                        ┘
            ├── database.json              ← Combined file
            ├── _processing_summary.json   ← Report
            └── markdown/                  ┐ Optional
                ├── 105_Amino2000_snf.md   │ (if --keep-md)
                └── ...                    ┘
```

---

## Database Import Strategies

### Strategy 1: Use Combined File
```
database.json
    ↓
Parse JSON
    ↓
Loop through products array
    ↓
Insert each record to database
```

### Strategy 2: Individual Files
```
For each *.json file:
    ↓
Load JSON
    ↓
Insert to database
```

### Strategy 3: Bulk Import
```
Convert database.json to format needed:
- PostgreSQL: COPY from JSON
- MongoDB: mongoimport
- Elasticsearch: Bulk API
    ↓
Single bulk import operation
```

---

## Performance Metrics

```
┌─────────────────────────────────────────────┐
│  ESTIMATED PROCESSING TIME                  │
├─────────────────────────────────────────────┤
│                                             │
│  10 PDFs    →  ~1 minute                   │
│  100 PDFs   →  ~10 minutes                 │
│  850 PDFs   →  ~60-90 minutes              │
│                                             │
│  (without OCR, typical product PDFs)        │
│                                             │
│  With OCR: 2-3x longer                     │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Workflow States

```
┌──────────┐     ┌────────────┐     ┌──────────┐     ┌──────────┐
│  READY   │ --> │ PROCESSING │ --> │ COMPLETE │ --> │ IMPORTED │
└──────────┘     └────────────┘     └──────────┘     └──────────┘
     │                  │                  │                │
     │                  │                  │                │
  Setup env      Converting PDFs    Review JSON    Database ready
  Install deps   Progress: 50/850   Check quality  Start using!
```

---

## Error Handling

```
PDF Processing
     │
     ├─ Success → JSON created
     │
     └─ Failed → Logged in _processing_summary.json
              │
              ├─ Reason: Corrupted file
              ├─ Reason: No extractable text (try --ocr)
              ├─ Reason: Encrypted PDF
              └─ Solution: Process individually with --ocr
```

---

## Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║  QUICK COMMANDS                                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Setup (once):                                           ║
║  $ python3 -m venv venv                                  ║
║  $ source venv/bin/activate                              ║
║  $ pip install docling pypdf pdfplumber pandas           ║
║                                                           ║
║  Run workflow:                                           ║
║  $ source venv/bin/activate                              ║
║  $ python3 scripts/pdf_to_clean_json.py \                ║
║      --batch ../pdfs/ ./output/products/ --keep-md       ║
║                                                           ║
║  Check results:                                          ║
║  $ cat output/products/_processing_summary.json          ║
║  $ cat output/products/database.json | head -50          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```
