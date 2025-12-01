# Using This Toolkit with GitHub Copilot

This guide explains how to effectively use the PDF Processing Toolkit with GitHub Copilot in Codespaces.

## 🎯 The Key Insight

Copilot works best when it has context. This toolkit provides:
1. **Well-documented scripts** with docstrings and examples
2. **This documentation** that you can reference with `@workspace`
3. **Consistent patterns** across all scripts

## 📝 How to Ask Copilot for Help

### Reference the Workspace
Always start with `@workspace` to give Copilot context:

```
@workspace How do I convert all PDFs in my products folder to Markdown?
```

### Reference Specific Files
For detailed help, point Copilot to relevant files:

```
@workspace Look at scripts/pdf_to_markdown.py and help me understand the options
```

### Reference This Documentation
```
@workspace Read docs/README.md and tell me which script to use for extracting tables
```

## 💡 Example Prompts

### Batch Conversion
```
@workspace I have 800 product PDFs in ./Ultimate Nutrition Product Line/
Help me convert them all to Markdown with table extraction.
```

### Table Extraction
```
@workspace I need to extract all tables from invoices/*.pdf and save them as Excel files.
Which script should I use and how?
```

### Form Filling
```
@workspace I have a tax form PDF that I need to fill out programmatically.
Walk me through the process using the scripts in this toolkit.
```

### Custom Processing
```
@workspace I need to:
1. Convert scanned PDFs with OCR
2. Extract specific pages (1-5)
3. Save as Markdown

Help me chain these scripts together.
```

### Troubleshooting
```
@workspace The pdf_to_markdown.py script is giving an error about docling.
What's wrong and how do I fix it?
```

## 🔧 Common Workflows

### Workflow 1: Batch PDF to Markdown
```bash
# Simple batch conversion
python scripts/pdf_to_markdown.py --batch ./products/ ./output/

# With all options (OCR, JSON, tables)
python scripts/pdf_to_markdown.py --batch ./products/ ./output/ --all
```

Ask Copilot:
> "@workspace Run the batch conversion on my products folder and show me the summary"

### Workflow 2: Extract Tables to Excel
```bash
# Single file
python scripts/extract_content.py invoice.pdf --tables --format xlsx

# Batch
python scripts/extract_content.py --batch ./invoices/ --tables --format xlsx -o ./tables/
```

Ask Copilot:
> "@workspace Help me write a script that extracts tables from all PDFs and combines them into one Excel file"

### Workflow 3: OCR Scanned Documents
```bash
# Single file to Markdown
python scripts/ocr_pdf.py scanned.pdf --format md

# Batch with high quality
python scripts/ocr_pdf.py --batch ./scans/ --dpi 300 --format md
```

Ask Copilot:
> "@workspace Some of my PDFs are scanned. Help me detect which ones need OCR and process them"

### Workflow 4: Custom Processing Pipeline
Ask Copilot:
> "@workspace I need a Python script that:
> 1. Checks if each PDF needs OCR
> 2. If scanned: uses ocr_pdf.py
> 3. If not: uses pdf_to_markdown.py
> 4. Combines all outputs into a single report
> 
> Use the existing scripts as modules."

## 🐍 Using Scripts as Python Modules

The scripts can be imported and used in your own code:

```python
# Copilot can help you write this
from scripts.pdf_to_markdown import PDFToMarkdownConverter, ConversionOptions

options = ConversionOptions(
    output_dir="./output",
    ocr_enabled=True,
    save_json=True,
    extract_tables=True
)

converter = PDFToMarkdownConverter(options)
result = converter.convert_file("document.pdf")

print(f"Saved to: {result.markdown_path}")
```

Ask Copilot:
> "@workspace Show me how to import pdf_to_markdown.py as a module and customize the conversion"

## 🎓 Learning the Scripts

Ask Copilot to explain:

```
@workspace Explain what pdf_to_markdown.py does step by step
```

```
@workspace What's the difference between pdf_to_markdown.py and extract_content.py?
```

```
@workspace How does the form filling process work? Explain check_form_fields.py
```

## ⚠️ Tips for Better Results

### 1. Be Specific
Instead of:
> "Help me with PDFs"

Say:
> "@workspace I have product PDFs with nutrition labels. I need to extract the nutrition facts tables to Excel."

### 2. Provide Context
Include file locations:
> "@workspace My PDFs are in ./data/products/ and I want output in ./output/markdown/"

### 3. Chain Commands
Ask for complete workflows:
> "@workspace Give me a bash script that converts all PDFs, then creates a summary of what was converted"

### 4. Ask for Verification
> "@workspace After running pdf_to_markdown.py, how can I verify the conversion worked correctly?"

## 🔗 Quick Reference

| Task | Script | Key Options |
|------|--------|-------------|
| PDF → Markdown | `pdf_to_markdown.py` | `--batch`, `--ocr`, `--all` |
| Extract tables | `extract_content.py` | `--tables`, `--format xlsx` |
| OCR scanned | `ocr_pdf.py` | `--dpi`, `--format md` |
| Check forms | `check_form_fields.py` | `--list`, `--extract` |
| Merge/split | `pdf_tools.py` | `merge`, `split`, `extract` |

## 📚 More Documentation

- [README.md](README.md) - Full script reference
- [WORKFLOWS.md](WORKFLOWS.md) - Step-by-step workflows
