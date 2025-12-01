# Examples Directory

Place your PDF files here for testing.

## Suggested Test Files

1. **Regular PDF** - Text-based document
2. **Scanned PDF** - Image-based document (for OCR testing)
3. **PDF with Tables** - For table extraction testing
4. **Fillable Form** - PDF with form fields

## Quick Tests

```bash
# Test conversion
python scripts/pdf_to_markdown.py examples/sample.pdf

# Test table extraction
python scripts/extract_content.py examples/sample.pdf --tables

# Test form detection
python scripts/check_form_fields.py examples/form.pdf
```
