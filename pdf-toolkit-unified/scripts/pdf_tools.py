#!/usr/bin/env python3
"""
pdf_tools.py - PDF manipulation utilities (merge, split, rotate, watermark)

A collection of common PDF operations using pypdf.

USAGE:
  python pdf_tools.py <command> [arguments]

COMMANDS:
  merge      Merge multiple PDFs into one
  split      Split PDF into individual pages
  rotate     Rotate pages in a PDF
  extract    Extract specific pages
  info       Show PDF metadata
  watermark  Add watermark to PDF
  encrypt    Add password protection
  decrypt    Remove password protection

EXAMPLES:
  python pdf_tools.py merge file1.pdf file2.pdf -o combined.pdf
  python pdf_tools.py split document.pdf -o ./pages/
  python pdf_tools.py rotate input.pdf 90 -o rotated.pdf
  python pdf_tools.py extract input.pdf 1-5,10,15-20 -o subset.pdf
  python pdf_tools.py info document.pdf
"""

import sys
from pathlib import Path
from typing import List, Optional

try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def check_pypdf():
    if not PYPDF_AVAILABLE:
        print("Error: pypdf not installed. Run: pip install pypdf")
        sys.exit(1)


def merge_pdfs(pdf_files: List[str], output_path: str):
    """Merge multiple PDFs into one."""
    check_pypdf()
    
    writer = PdfWriter()
    
    for pdf_file in pdf_files:
        print(f"Adding: {pdf_file}")
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            writer.add_page(page)
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    print(f"✓ Merged {len(pdf_files)} files → {output_path}")


def split_pdf(pdf_path: str, output_dir: str):
    """Split PDF into individual pages."""
    check_pypdf()
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    reader = PdfReader(pdf_path)
    base_name = Path(pdf_path).stem
    
    for i, page in enumerate(reader.pages, 1):
        writer = PdfWriter()
        writer.add_page(page)
        
        output_path = output_dir / f"{base_name}_page_{i:03d}.pdf"
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    print(f"✓ Split into {len(reader.pages)} pages → {output_dir}/")


def rotate_pdf(pdf_path: str, degrees: int, output_path: str, pages: str = "all"):
    """Rotate pages in a PDF."""
    check_pypdf()
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    # Parse page specification
    if pages == "all":
        page_nums = range(len(reader.pages))
    else:
        page_nums = parse_page_spec(pages, len(reader.pages))
    
    for i, page in enumerate(reader.pages):
        if i in page_nums:
            page.rotate(degrees)
        writer.add_page(page)
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    print(f"✓ Rotated {len(page_nums)} pages by {degrees}° → {output_path}")


def extract_pages(pdf_path: str, page_spec: str, output_path: str):
    """Extract specific pages from PDF."""
    check_pypdf()
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    page_nums = parse_page_spec(page_spec, len(reader.pages))
    
    for page_num in sorted(page_nums):
        writer.add_page(reader.pages[page_num])
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    print(f"✓ Extracted {len(page_nums)} pages → {output_path}")


def parse_page_spec(spec: str, total_pages: int) -> set:
    """
    Parse page specification like '1-5,10,15-20'.
    Returns set of 0-indexed page numbers.
    """
    pages = set()
    
    for part in spec.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start) - 1
            end = int(end)
            pages.update(range(start, min(end, total_pages)))
        else:
            page = int(part) - 1
            if 0 <= page < total_pages:
                pages.add(page)
    
    return pages


def show_info(pdf_path: str):
    """Show PDF metadata."""
    check_pypdf()
    
    reader = PdfReader(pdf_path)
    meta = reader.metadata
    
    print(f"File: {pdf_path}")
    print(f"Pages: {len(reader.pages)}")
    print(f"Encrypted: {reader.is_encrypted}")
    
    if meta:
        print("\nMetadata:")
        if meta.title:
            print(f"  Title: {meta.title}")
        if meta.author:
            print(f"  Author: {meta.author}")
        if meta.subject:
            print(f"  Subject: {meta.subject}")
        if meta.creator:
            print(f"  Creator: {meta.creator}")
        if meta.producer:
            print(f"  Producer: {meta.producer}")
    
    # Check for form fields
    fields = reader.get_fields()
    if fields:
        print(f"\nForm fields: {len(fields)}")


def add_watermark(pdf_path: str, watermark_path: str, output_path: str):
    """Add watermark to PDF."""
    check_pypdf()
    
    reader = PdfReader(pdf_path)
    watermark_reader = PdfReader(watermark_path)
    watermark_page = watermark_reader.pages[0]
    
    writer = PdfWriter()
    
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    print(f"✓ Added watermark → {output_path}")


def encrypt_pdf(pdf_path: str, output_path: str, 
                user_password: str, owner_password: str = None):
    """Add password protection to PDF."""
    check_pypdf()
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
    
    writer.encrypt(user_password, owner_password or user_password)
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    print(f"✓ Encrypted → {output_path}")


def decrypt_pdf(pdf_path: str, password: str, output_path: str):
    """Remove password protection from PDF."""
    check_pypdf()
    
    reader = PdfReader(pdf_path)
    
    if reader.is_encrypted:
        reader.decrypt(password)
    
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    print(f"✓ Decrypted → {output_path}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    # Parse -o/--output flag
    output_path = None
    remaining_args = []
    i = 0
    while i < len(args):
        if args[i] in ('-o', '--output') and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        else:
            remaining_args.append(args[i])
            i += 1
    
    if command == 'merge':
        if len(remaining_args) < 2:
            print("Usage: pdf_tools.py merge file1.pdf file2.pdf ... -o output.pdf")
            sys.exit(1)
        output = output_path or 'merged.pdf'
        merge_pdfs(remaining_args, output)
    
    elif command == 'split':
        if not remaining_args:
            print("Usage: pdf_tools.py split input.pdf -o output_dir/")
            sys.exit(1)
        output = output_path or './split_pages'
        split_pdf(remaining_args[0], output)
    
    elif command == 'rotate':
        if len(remaining_args) < 2:
            print("Usage: pdf_tools.py rotate input.pdf 90 -o output.pdf")
            sys.exit(1)
        degrees = int(remaining_args[1])
        output = output_path or f"{Path(remaining_args[0]).stem}_rotated.pdf"
        rotate_pdf(remaining_args[0], degrees, output)
    
    elif command == 'extract':
        if len(remaining_args) < 2:
            print("Usage: pdf_tools.py extract input.pdf 1-5,10 -o output.pdf")
            sys.exit(1)
        output = output_path or f"{Path(remaining_args[0]).stem}_extracted.pdf"
        extract_pages(remaining_args[0], remaining_args[1], output)
    
    elif command == 'info':
        if not remaining_args:
            print("Usage: pdf_tools.py info input.pdf")
            sys.exit(1)
        show_info(remaining_args[0])
    
    elif command == 'watermark':
        if len(remaining_args) < 2:
            print("Usage: pdf_tools.py watermark input.pdf watermark.pdf -o output.pdf")
            sys.exit(1)
        output = output_path or f"{Path(remaining_args[0]).stem}_watermarked.pdf"
        add_watermark(remaining_args[0], remaining_args[1], output)
    
    elif command == 'encrypt':
        if len(remaining_args) < 2:
            print("Usage: pdf_tools.py encrypt input.pdf password -o output.pdf")
            sys.exit(1)
        output = output_path or f"{Path(remaining_args[0]).stem}_encrypted.pdf"
        encrypt_pdf(remaining_args[0], output, remaining_args[1])
    
    elif command == 'decrypt':
        if len(remaining_args) < 2:
            print("Usage: pdf_tools.py decrypt input.pdf password -o output.pdf")
            sys.exit(1)
        output = output_path or f"{Path(remaining_args[0]).stem}_decrypted.pdf"
        decrypt_pdf(remaining_args[0], remaining_args[1], output)
    
    else:
        print(f"Unknown command: {command}")
        print("Run 'python pdf_tools.py' for help")
        sys.exit(1)


if __name__ == "__main__":
    main()
