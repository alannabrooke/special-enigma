# GitHub Codespaces Setup Guide

Complete guide for using the PDF toolkit in GitHub Codespaces.

---

## ✨ Automatic Setup

Good news! The devcontainer is already configured. When you open this repo in Codespaces, everything installs automatically.

---

## 🚀 Getting Started in Codespaces

### Step 1: Open in Codespaces

1. Go to your GitHub repository: https://github.com/alannabrooke/special-enigma
2. Click the **Code** button
3. Select **Codespaces** tab
4. Click **Create codespace on testa4** (or your branch)

### Step 2: Wait for Setup

The devcontainer will automatically:
- ✅ Install Python 3.11
- ✅ Install system dependencies (Tesseract OCR, poppler-utils, etc.)
- ✅ Install Python packages (docling, pypdf, pdfplumber, pandas)
- ✅ Set up VS Code extensions (Copilot, Python)
- ✅ Create output directories

This takes **2-3 minutes** on first launch.

### Step 3: Verify Installation

Once the Codespace is ready, you'll see:

```
==============================================
  Setup Complete!
==============================================

QUICK START COMMANDS:

  🌟 NEW: PDF → JSON Workflow (for databases):
     python scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --keep-md
     → Creates clean JSON files ready for database import!
```

---

## 🎯 Using the Workflow in Codespaces

### Convert All Your PDFs

The PDFs are already in the repository at `../pdfs/`. Just run:

```bash
# Navigate to toolkit
cd pdf-toolkit-unified

# Run the workflow
python scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --keep-md
```

**This will:**
1. Process all PDFs in the `pdfs/` directory
2. Create individual JSON files for each product
3. Generate a combined `database.json`
4. Save clean markdown files (for review)
5. Create a processing summary report

---

## 📂 File Structure in Codespaces

```
/workspaces/special-enigma/          (Repository root)
├── pdfs/                             ← Your 850 product PDFs
│   ├── 105_Amino2000_snf.pdf
│   ├── 141_ProWhey_snf.pdf
│   └── ...
│
└── pdf-toolkit-unified/              ← Toolkit directory
    ├── scripts/
    │   ├── pdf_to_clean_json.py      ← Main workflow script
    │   ├── pdf_to_markdown.py
    │   └── ...
    │
    ├── output/                       ← Generated files
    │   └── products/
    │       ├── *.json                ← Individual product files
    │       ├── database.json         ← Combined database file
    │       ├── _processing_summary.json
    │       └── markdown/             ← Clean markdown files
    │
    ├── QUICK_START.md
    ├── CODESPACES_GUIDE.md          ← You are here!
    └── docs/
        └── DATABASE_WORKFLOW.md
```

---

## 💡 Codespaces-Specific Tips

### 1. No Virtual Environment Needed

In Codespaces, everything is already isolated. You don't need to create a venv:

```bash
# ❌ Not needed in Codespaces
python3 -m venv venv
source venv/bin/activate

# ✅ Just run directly
python scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/
```

### 2. All Dependencies Pre-Installed

The devcontainer handles everything:
- Python packages from `requirements.txt`
- System tools (Tesseract, poppler-utils)
- VS Code extensions

### 3. Processing Large Batches

For 850+ PDFs, consider running in the background:

```bash
# Start processing in background
nohup python scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --keep-md > conversion.log 2>&1 &

# Monitor progress
tail -f conversion.log

# Or check status
ls output/products/*.json | wc -l
```

### 4. Download Results

After processing, download the output:

1. Right-click on `output/products/` in VS Code
2. Select **Download...**
3. Save to your local machine

Or download just the database file:
- Right-click `output/products/database.json`
- Select **Download**

---

## 🔧 Common Codespaces Commands

### View a Sample Output

```bash
# Check one product JSON
cat output/products/105_Amino2000_snf.json | python -m json.tool | head -30

# View the combined database
cat output/products/database.json | python -m json.tool | head -50

# Check processing summary
cat output/products/_processing_summary.json | python -m json.tool
```

### Test Single File First

```bash
# Test with one PDF
python scripts/pdf_to_clean_json.py ../pdfs/105_Amino2000_snf.pdf ./test_output/

# Review result
cat test_output/105_Amino2000_snf.json
```

### Reprocess Failed Files

```bash
# Check for failures
cat output/products/_processing_summary.json | grep -B 2 '"success": false'

# Retry with OCR
python scripts/pdf_to_clean_json.py ../pdfs/failed_file.pdf ./output/retry/ --ocr
```

---

## 🎨 Using with Copilot

Since Copilot is pre-installed, you can ask it for help:

### Example Prompts

```
@workspace How do I process all PDFs with OCR enabled?
```

```
@workspace Show me the structure of the JSON output from pdf_to_clean_json.py
```

```
@workspace Help me write a script to import database.json into PostgreSQL
```

```
@workspace Read docs/DATABASE_WORKFLOW.md and help me extract nutrition tables
```

---

## ⚡ Quick Commands Reference

### Basic Workflow
```bash
cd pdf-toolkit-unified
python scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --keep-md
```

### With OCR (for scanned PDFs)
```bash
python scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --ocr --keep-md
```

### Check Progress
```bash
# Count processed files
ls output/products/*.json | wc -l

# View summary
cat output/products/_processing_summary.json | python -m json.tool
```

### View Results
```bash
# List all JSON files
ls -lh output/products/*.json

# Check database file size
ls -lh output/products/database.json

# Preview content
head -100 output/products/database.json
```

---

## 🐛 Troubleshooting in Codespaces

### Issue: "Setup script failed"

Rebuild the container:
1. Press `F1` or `Cmd+Shift+P`
2. Type "Rebuild Container"
3. Select **Codespaces: Rebuild Container**

### Issue: "Out of space"

Codespaces have limited storage. Clean up:
```bash
# Remove test outputs
rm -rf test_output/

# Keep only final results
rm -rf output/products/markdown/
```

### Issue: Slow processing

This is normal for large batches. Consider:
```bash
# Process in smaller batches
python scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/batch1/ --recursive

# Run overnight
nohup python scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/ > conversion.log 2>&1 &
```

### Issue: Codespace times out

For long-running jobs:
```bash
# Use nohup to keep running even if disconnected
nohup python scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ > conversion.log 2>&1 &

# Check if still running
ps aux | grep pdf_to_clean_json
```

---

## 📊 Expected Performance

On a standard GitHub Codespace (2-core):

| Files | Time (without OCR) | Time (with OCR) |
|-------|-------------------|-----------------|
| 10    | ~1 minute         | ~3 minutes      |
| 100   | ~10 minutes       | ~30 minutes     |
| 850   | ~60-90 minutes    | ~3-4 hours      |

---

## 🎯 Complete Example Workflow

```bash
# 1. Make sure you're in the right directory
cd /workspaces/special-enigma/pdf-toolkit-unified

# 2. Test with one file first
python scripts/pdf_to_clean_json.py ../pdfs/105_Amino2000_snf.pdf ./test/

# 3. Check the output
cat test/105_Amino2000_snf.json | python -m json.tool | head -50

# 4. If looks good, run full batch
python scripts/pdf_to_clean_json.py --batch ../pdfs/ ./output/products/ --keep-md

# 5. Monitor progress (in another terminal)
watch -n 10 'ls output/products/*.json | wc -l'

# 6. When done, check results
cat output/products/_processing_summary.json | python -m json.tool

# 7. Download the database.json file
# Right-click in VS Code → Download
```

---

## 🎉 Next Steps

1. ✅ Open repo in Codespaces
2. ✅ Wait for automatic setup (2-3 minutes)
3. ✅ Run the workflow command
4. ✅ Download `database.json`
5. ✅ Import to your database

For detailed documentation, see:
- **QUICK_START.md** - Quick reference
- **docs/DATABASE_WORKFLOW.md** - Complete guide
- **SETUP_GUIDE.md** - Local setup (if needed)
