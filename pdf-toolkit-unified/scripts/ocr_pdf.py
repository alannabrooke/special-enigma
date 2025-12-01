#!/usr/bin/env python3
"""
ocr_pdf.py - OCR for scanned PDFs using Tesseract

Convert scanned/image-based PDFs to searchable text or Markdown.

USAGE:
  python ocr_pdf.py input.pdf [output_dir]
  python ocr_pdf.py --batch input_dir/ [output_dir]

OPTIONS:
  --format       Output format: txt, md, json (default: txt)
  --lang         OCR language (default: eng)
  --dpi          Resolution for conversion (default: 200)
  --pages        Specific pages to OCR: 1-5,10 (default: all)

EXAMPLES:
  python ocr_pdf.py scanned.pdf
  python ocr_pdf.py scanned.pdf --format md
  python ocr_pdf.py --batch ./scanned_docs/ ./output/ --format txt
"""

import sys
from pathlib import Path
from typing import List, Optional

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def check_dependencies():
    if not PDF2IMAGE_AVAILABLE:
        print("Error: pdf2image not installed. Run: pip install pdf2image")
        sys.exit(1)
    if not TESSERACT_AVAILABLE:
        print("Error: pytesseract not installed. Run: pip install pytesseract")
        sys.exit(1)


def ocr_pdf(pdf_path: str, output_dir: str = None, 
            output_format: str = "txt", lang: str = "eng",
            dpi: int = 200, pages: str = None) -> str:
    """
    OCR a PDF and save the extracted text.
    
    Args:
        pdf_path: Path to PDF
        output_dir: Output directory
        output_format: txt, md, or json
        lang: Tesseract language code
        dpi: Resolution for page rendering
        pages: Page specification (e.g., "1-5,10")
    
    Returns:
        Path to output file
    """
    check_dependencies()
    
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir or "output/ocr")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing: {pdf_path.name}")
    print(f"  Converting to images (DPI: {dpi})...", end=" ", flush=True)
    
    # Convert PDF to images
    try:
        images = convert_from_path(str(pdf_path), dpi=dpi)
        print(f"✓ ({len(images)} pages)")
    except Exception as e:
        print(f"✗ Error: {e}")
        return None
    
    # Parse page specification
    if pages:
        page_nums = parse_page_spec(pages, len(images))
        images = [images[i] for i in sorted(page_nums)]
    
    # OCR each page
    text_parts = []
    
    for i, image in enumerate(images, 1):
        print(f"  OCR page {i}/{len(images)}...", end=" ", flush=True)
        try:
            text = pytesseract.image_to_string(image, lang=lang)
            text_parts.append({
                'page': i,
                'text': text.strip()
            })
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
            text_parts.append({
                'page': i,
                'text': f"[OCR Error: {e}]"
            })
    
    # Format output
    base_name = pdf_path.stem
    
    if output_format == "json":
        import json
        content = json.dumps({
            'source': str(pdf_path),
            'pages': text_parts
        }, indent=2, ensure_ascii=False)
        ext = ".json"
    
    elif output_format == "md":
        lines = [f"# {pdf_path.name}\n"]
        for part in text_parts:
            lines.append(f"\n## Page {part['page']}\n")
            lines.append(part['text'])
        content = "\n".join(lines)
        ext = ".md"
    
    else:  # txt
        lines = []
        for part in text_parts:
            lines.append(f"--- Page {part['page']} ---")
            lines.append(part['text'])
            lines.append("")
        content = "\n".join(lines)
        ext = ".txt"
    
    # Save
    output_path = output_dir / f"{base_name}_ocr{ext}"
    output_path.write_text(content, encoding='utf-8')
    
    print(f"✓ Saved: {output_path}")
    return str(output_path)


def parse_page_spec(spec: str, total: int) -> set:
    """Parse page specification like '1-5,10'."""
    pages = set()
    for part in spec.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start) - 1
            end = int(end)
            pages.update(range(start, min(end, total)))
        else:
            page = int(part) - 1
            if 0 <= page < total:
                pages.add(page)
    return pages


def batch_ocr(input_dir: str, output_dir: str = None, **kwargs) -> List[str]:
    """OCR all PDFs in a directory."""
    input_dir = Path(input_dir)
    output_dir = output_dir or str(input_dir / "ocr_output")
    
    pdf_files = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return []
    
    print(f"Found {len(pdf_files)} PDF files")
    print("-" * 40)
    
    results = []
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}]")
        result = ocr_pdf(str(pdf_file), output_dir, **kwargs)
        if result:
            results.append(result)
    
    print("-" * 40)
    print(f"Completed: {len(results)}/{len(pdf_files)}")
    
    return results


def main():
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print(__doc__)
        sys.exit(0)
    
    args = sys.argv[1:]
    
    # Parse flags
    batch_mode = '--batch' in args
    
    output_format = "txt"
    lang = "eng"
    dpi = 200
    pages = None
    output_dir = None
    
    i = 0
    path_args = []
    while i < len(args):
        if args[i] == '--format' and i + 1 < len(args):
            output_format = args[i + 1]
            i += 2
        elif args[i] == '--lang' and i + 1 < len(args):
            lang = args[i + 1]
            i += 2
        elif args[i] == '--dpi' and i + 1 < len(args):
            dpi = int(args[i + 1])
            i += 2
        elif args[i] == '--pages' and i + 1 < len(args):
            pages = args[i + 1]
            i += 2
        elif args[i] in ('-o', '--output') and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        elif args[i].startswith('--'):
            i += 1
        else:
            path_args.append(args[i])
            i += 1
    
    if not path_args:
        print("Error: Please specify input path")
        sys.exit(1)
    
    input_path = path_args[0]
    if len(path_args) > 1 and not output_dir:
        output_dir = path_args[1]
    
    kwargs = {
        'output_format': output_format,
        'lang': lang,
        'dpi': dpi,
        'pages': pages
    }
    
    if batch_mode:
        batch_ocr(input_path, output_dir, **kwargs)
    else:
        ocr_pdf(input_path, output_dir, **kwargs)


if __name__ == "__main__":
    main()
