#!/usr/bin/env python3
"""
pdf_to_clean_json.py - Complete workflow: PDF → Clean Markdown → Structured JSON

This script provides an end-to-end workflow for converting PDFs into clean,
structured JSON data ready for database indexing.

WORKFLOW:
  1. Convert PDF to Markdown (using Docling)
  2. Clean and normalize the Markdown
  3. Extract structured data
  4. Export to JSON with consistent schema

USAGE:
  Single file:   python pdf_to_clean_json.py input.pdf
  Batch:         python pdf_to_clean_json.py --batch input_dir/ [output_dir]

OPTIONS:
  --batch           Process all PDFs in a directory
  --ocr             Enable OCR for scanned documents
  --schema FILE     Use custom JSON schema template
  --keep-md         Keep intermediate markdown files
  --recursive       Include subdirectories

EXAMPLES:
  python pdf_to_clean_json.py product.pdf
  python pdf_to_clean_json.py --batch ./pdfs/ ./output/
  python pdf_to_clean_json.py --batch ./pdfs/ --ocr --keep-md
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# Try importing docling
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False


@dataclass
class ProductData:
    """Structured product data schema."""
    id: str
    source_file: str
    title: str
    description: str = ""
    content: str = ""
    tables: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    extracted_at: str = ""

    def __post_init__(self):
        if self.tables is None:
            self.tables = []
        if self.metadata is None:
            self.metadata = {}
        if not self.extracted_at:
            self.extracted_at = datetime.now().isoformat()


class MarkdownCleaner:
    """Clean and normalize markdown content."""

    @staticmethod
    def clean(markdown_text: str) -> str:
        """
        Clean markdown text for better JSON conversion.

        - Removes excessive whitespace
        - Normalizes headings
        - Cleans up tables
        - Removes artifacts
        """
        text = markdown_text

        # Remove multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Normalize heading spacing
        text = re.sub(r'(#+)\s*([^\n]+)', r'\1 \2', text)

        # Clean table borders
        text = re.sub(r'\|\s*-+\s*\|', lambda m: '|' + '-' * (len(m.group(0)) - 2) + '|', text)

        # Remove trailing whitespace
        text = '\n'.join(line.rstrip() for line in text.split('\n'))

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def extract_title(markdown_text: str) -> str:
        """Extract title from markdown (first H1 or H2)."""
        match = re.search(r'^#{1,2}\s+(.+)$', markdown_text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Untitled"

    @staticmethod
    def extract_description(markdown_text: str) -> str:
        """Extract description (first paragraph after title)."""
        # Remove title
        text = re.sub(r'^#{1,2}\s+.+$', '', markdown_text, count=1, flags=re.MULTILINE)
        text = text.strip()

        # Get first paragraph
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if paragraphs:
            # Return first non-header paragraph
            for para in paragraphs:
                if not para.startswith('#'):
                    return para[:500]  # Limit description length
        return ""

    @staticmethod
    def extract_tables(markdown_text: str) -> List[Dict[str, Any]]:
        """Extract tables from markdown."""
        tables = []

        # Find markdown tables (lines with | separators)
        table_pattern = r'(\|.+\|[\n\r]+\|[-:\s|]+\|[\n\r]+(?:\|.+\|[\n\r]+)+)'

        for i, match in enumerate(re.finditer(table_pattern, markdown_text)):
            table_text = match.group(1)
            table_data = MarkdownCleaner._parse_markdown_table(table_text)
            if table_data:
                tables.append({
                    'id': i + 1,
                    'headers': table_data[0] if table_data else [],
                    'rows': table_data[1:] if len(table_data) > 1 else [],
                    'raw': table_text.strip()
                })

        return tables

    @staticmethod
    def _parse_markdown_table(table_text: str) -> List[List[str]]:
        """Parse markdown table into 2D array."""
        lines = [line.strip() for line in table_text.split('\n') if line.strip()]

        # Remove separator line (contains only -, |, and :)
        lines = [line for line in lines if not re.match(r'^[\s\-:|]+$', line)]

        rows = []
        for line in lines:
            # Split by | and clean
            cells = [cell.strip() for cell in line.split('|')]
            # Remove empty first/last cells (from leading/trailing |)
            cells = [c for c in cells if c]
            if cells:
                rows.append(cells)

        return rows


class PDFToJSONConverter:
    """Convert PDFs to clean, structured JSON."""

    def __init__(self, keep_markdown: bool = False, ocr_enabled: bool = False):
        if not DOCLING_AVAILABLE:
            raise ImportError(
                "Docling is not installed.\n"
                "Install with: pip install docling"
            )

        self.keep_markdown = keep_markdown
        self.ocr_enabled = ocr_enabled
        self._init_converter()

    def _init_converter(self):
        """Initialize Docling converter."""
        try:
            if self.ocr_enabled:
                from docling.datamodel.pipeline_options import PdfPipelineOptions
                pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = True
                self.converter = DocumentConverter(pipeline_options=pipeline_options)
            else:
                self.converter = DocumentConverter()
        except Exception:
            self.converter = DocumentConverter()

    def convert_file(self, pdf_path: str, output_dir: str = "output") -> Dict[str, Any]:
        """
        Convert a single PDF to JSON.

        Returns dict with:
          - success: bool
          - json_path: str (if successful)
          - error: str (if failed)
        """
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        result = {
            'success': False,
            'source': str(pdf_path),
            'json_path': None,
            'markdown_path': None,
            'error': None
        }

        if not pdf_path.exists():
            result['error'] = f"File not found: {pdf_path}"
            return result

        try:
            print(f"Processing: {pdf_path.name}...", end=" ", flush=True)

            # Step 1: Convert PDF to Markdown
            docling_result = self.converter.convert(str(pdf_path))
            markdown_text = docling_result.document.export_to_markdown()

            # Step 2: Clean markdown
            clean_markdown = MarkdownCleaner.clean(markdown_text)

            # Save markdown if requested
            if self.keep_markdown:
                md_path = output_dir / f"{pdf_path.stem}.md"
                md_path.write_text(clean_markdown, encoding='utf-8')
                result['markdown_path'] = str(md_path)

            # Step 3: Extract structured data
            title = MarkdownCleaner.extract_title(clean_markdown)
            description = MarkdownCleaner.extract_description(clean_markdown)
            tables = MarkdownCleaner.extract_tables(clean_markdown)

            # Step 4: Create structured product data
            product = ProductData(
                id=pdf_path.stem,
                source_file=pdf_path.name,
                title=title,
                description=description,
                content=clean_markdown,
                tables=tables,
                metadata={
                    'file_size': pdf_path.stat().st_size,
                    'file_modified': datetime.fromtimestamp(pdf_path.stat().st_mtime).isoformat(),
                    'ocr_used': self.ocr_enabled,
                    'table_count': len(tables)
                }
            )

            # Step 5: Save as JSON
            json_path = output_dir / f"{pdf_path.stem}.json"
            json_data = asdict(product)
            json_path.write_text(
                json.dumps(json_data, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            result['json_path'] = str(json_path)
            result['success'] = True

            print("✓")

        except Exception as e:
            result['error'] = str(e)
            print(f"✗ ({e})")

        return result

    def convert_batch(self, input_dir: str, output_dir: str = "output",
                     recursive: bool = False) -> List[Dict[str, Any]]:
        """Convert all PDFs in a directory."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        if not input_dir.exists():
            print(f"Error: Directory not found: {input_dir}")
            return []

        # Find PDFs
        if recursive:
            pdf_files = list(input_dir.rglob("*.pdf")) + list(input_dir.rglob("*.PDF"))
        else:
            pdf_files = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF"))

        if not pdf_files:
            print(f"No PDF files found in {input_dir}")
            return []

        output_dir.mkdir(parents=True, exist_ok=True)

        # Header
        print("=" * 70)
        print("PDF → Clean Markdown → JSON Workflow")
        print("=" * 70)
        print(f"Input:  {input_dir} ({len(pdf_files)} files)")
        print(f"Output: {output_dir}")
        print(f"Options: OCR={'on' if self.ocr_enabled else 'off'}, "
              f"Keep MD={'yes' if self.keep_markdown else 'no'}")
        print("-" * 70)

        results = []
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"[{i}/{len(pdf_files)}] ", end="")
            result = self.convert_file(str(pdf_file), str(output_dir))
            results.append(result)

        # Summary
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        print("-" * 70)
        print(f"✓ Successful: {len(successful)}")
        print(f"✗ Failed: {len(failed)}")

        if failed:
            print("\nFailed files:")
            for r in failed:
                print(f"  - {Path(r['source']).name}: {r['error']}")

        # Save processing summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'input_dir': str(input_dir),
            'output_dir': str(output_dir),
            'total_files': len(pdf_files),
            'successful': len(successful),
            'failed': len(failed),
            'results': results
        }

        summary_path = output_dir / '_processing_summary.json'
        summary_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"\nProcessing summary: {summary_path}")

        # Create combined database-ready JSON
        if successful:
            database = {
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'total_records': len(successful),
                    'source': str(input_dir)
                },
                'products': []
            }

            for result in successful:
                json_path = Path(result['json_path'])
                product_data = json.loads(json_path.read_text(encoding='utf-8'))
                database['products'].append(product_data)

            db_path = output_dir / 'database.json'
            db_path.write_text(
                json.dumps(database, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            print(f"Combined database: {db_path}")

        return results


def main():
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        sys.exit(0)

    # Parse arguments
    args = sys.argv[1:]

    batch_mode = '--batch' in args
    ocr_enabled = '--ocr' in args
    keep_md = '--keep-md' in args
    recursive = '--recursive' in args

    # Remove flags
    path_args = [a for a in args if not a.startswith('--')]

    if not path_args:
        print("Error: Please specify input path")
        print("Usage: python pdf_to_clean_json.py [--batch] input [output_dir]")
        sys.exit(1)

    # Initialize converter
    try:
        converter = PDFToJSONConverter(
            keep_markdown=keep_md,
            ocr_enabled=ocr_enabled
        )
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_dir = path_args[1] if len(path_args) > 1 else "output/json"

    # Run conversion
    if batch_mode:
        converter.convert_batch(path_args[0], output_dir, recursive=recursive)
    else:
        result = converter.convert_file(path_args[0], output_dir)
        if result['success']:
            print(f"\nJSON output: {result['json_path']}")
            if result['markdown_path']:
                print(f"Markdown:    {result['markdown_path']}")
        else:
            print(f"\nError: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
