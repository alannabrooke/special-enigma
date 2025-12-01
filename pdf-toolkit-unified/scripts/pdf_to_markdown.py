#!/usr/bin/env python3
"""
pdf_to_markdown.py - Convert PDFs to structured Markdown using Docling

This is the PRIMARY conversion tool. It uses Docling to convert PDFs while
preserving document structure (headings, tables, lists, formatting).

USAGE:
  Single file:   python pdf_to_markdown.py input.pdf [output_dir]
  Batch:         python pdf_to_markdown.py --batch input_dir/ [output_dir]
  
OPTIONS:
  --batch        Process all PDFs in a directory
  --ocr          Enable OCR for scanned documents
  --json         Also save JSON structure
  --tables       Extract tables to CSV files
  --all          Enable all output options
  --recursive    Include subdirectories (with --batch)

EXAMPLES:
  python pdf_to_markdown.py product.pdf
  python pdf_to_markdown.py --batch ./products/ ./output/
  python pdf_to_markdown.py --batch ./scanned/ --ocr --all
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

# Check for docling
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False


@dataclass
class ConversionResult:
    """Result of a single PDF conversion."""
    source: str
    success: bool
    markdown_path: Optional[str] = None
    json_path: Optional[str] = None
    tables_dir: Optional[str] = None
    error: Optional[str] = None
    elements_count: int = 0
    tables_count: int = 0


@dataclass
class ConversionOptions:
    """Options for PDF conversion."""
    output_dir: str = "output"
    ocr_enabled: bool = False
    save_json: bool = False
    extract_tables: bool = False
    recursive: bool = False


class PDFToMarkdownConverter:
    """
    Convert PDFs to Markdown using Docling.
    
    This class wraps Docling's DocumentConverter and provides:
    - Single file and batch conversion
    - Optional OCR for scanned documents
    - JSON structure export
    - Table extraction to CSV
    - Progress reporting
    """
    
    def __init__(self, options: ConversionOptions = None):
        if not DOCLING_AVAILABLE:
            raise ImportError(
                "Docling is not installed.\n"
                "Install with: pip install docling"
            )
        
        self.options = options or ConversionOptions()
        self._init_converter()
    
    def _init_converter(self):
        """Initialize the Docling converter with options."""
        try:
            if self.options.ocr_enabled:
                from docling.datamodel.pipeline_options import PdfPipelineOptions
                pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = True
                self.converter = DocumentConverter(pipeline_options=pipeline_options)
            else:
                self.converter = DocumentConverter()
        except Exception:
            # Fallback to default
            self.converter = DocumentConverter()
    
    def convert_file(self, pdf_path: str, output_dir: str = None) -> ConversionResult:
        """
        Convert a single PDF to Markdown.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory (uses self.options.output_dir if None)
        
        Returns:
            ConversionResult with paths to generated files
        """
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir or self.options.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result = ConversionResult(source=str(pdf_path), success=False)
        
        if not pdf_path.exists():
            result.error = f"File not found: {pdf_path}"
            return result
        
        try:
            # Convert with Docling
            print(f"Converting: {pdf_path.name}...", end=" ", flush=True)
            docling_result = self.converter.convert(pdf_path)
            
            base_name = pdf_path.stem
            
            # Export Markdown
            md_content = docling_result.document.export_to_markdown()
            md_path = output_dir / f"{base_name}.md"
            md_path.write_text(md_content, encoding='utf-8')
            result.markdown_path = str(md_path)
            
            # Count elements for reporting
            try:
                elements = list(docling_result.document.iterate_items())
                result.elements_count = len(elements)
            except:
                pass
            
            # Optional: Export JSON
            if self.options.save_json:
                try:
                    json_content = docling_result.document.export_to_dict()
                    json_path = output_dir / f"{base_name}.json"
                    json_path.write_text(
                        json.dumps(json_content, indent=2, ensure_ascii=False, default=str),
                        encoding='utf-8'
                    )
                    result.json_path = str(json_path)
                except Exception as e:
                    print(f"(JSON export failed: {e})", end=" ")
            
            # Optional: Extract tables
            if self.options.extract_tables:
                tables = self._extract_tables(docling_result)
                if tables:
                    tables_dir = output_dir / "tables"
                    tables_dir.mkdir(exist_ok=True)
                    for i, table in enumerate(tables):
                        table_path = tables_dir / f"{base_name}_table_{i+1}.csv"
                        self._save_table_csv(table, table_path)
                    result.tables_dir = str(tables_dir)
                    result.tables_count = len(tables)
            
            result.success = True
            print("✓")
            
        except Exception as e:
            result.error = str(e)
            print(f"✗ ({e})")
        
        return result
    
    def _extract_tables(self, docling_result) -> List[Dict]:
        """Extract tables from Docling result."""
        tables = []
        try:
            for element in docling_result.document.iterate_items():
                elem_type = type(element).__name__.lower()
                if 'table' in elem_type:
                    tables.append({
                        'type': elem_type,
                        'content': str(element)
                    })
        except:
            pass
        return tables
    
    def _save_table_csv(self, table: Dict, path: Path):
        """Save table data to CSV."""
        try:
            content = table.get('content', '')
            # Simple parsing - split by newlines and tabs/pipes
            lines = content.strip().split('\n')
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for line in lines:
                    # Split by pipe or tab
                    if '|' in line:
                        cells = [c.strip() for c in line.split('|') if c.strip()]
                    else:
                        cells = [c.strip() for c in line.split('\t') if c.strip()]
                    if cells:
                        writer.writerow(cells)
        except:
            # Just save raw content
            path.with_suffix('.txt').write_text(table.get('content', ''), encoding='utf-8')
    
    def convert_batch(self, input_dir: str, output_dir: str = None) -> List[ConversionResult]:
        """
        Convert all PDFs in a directory.
        
        Args:
            input_dir: Directory containing PDFs
            output_dir: Output directory
        
        Returns:
            List of ConversionResult for each file
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir or self.options.output_dir)
        
        if not input_dir.exists():
            print(f"Error: Directory not found: {input_dir}")
            return []
        
        # Find PDFs
        if self.options.recursive:
            pdf_files = list(input_dir.rglob("*.pdf")) + list(input_dir.rglob("*.PDF"))
        else:
            pdf_files = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF"))
        
        if not pdf_files:
            print(f"No PDF files found in {input_dir}")
            return []
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Header
        print("=" * 60)
        print(f"PDF to Markdown Batch Conversion")
        print("=" * 60)
        print(f"Input:  {input_dir} ({len(pdf_files)} files)")
        print(f"Output: {output_dir}")
        print(f"Options: OCR={'on' if self.options.ocr_enabled else 'off'}, "
              f"JSON={'on' if self.options.save_json else 'off'}, "
              f"Tables={'on' if self.options.extract_tables else 'off'}")
        print("-" * 60)
        
        results = []
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"[{i}/{len(pdf_files)}] ", end="")
            result = self.convert_file(str(pdf_file), str(output_dir))
            results.append(result)
        
        # Summary
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        print("-" * 60)
        print(f"✓ Successful: {len(successful)}")
        print(f"✗ Failed: {len(failed)}")
        
        if failed:
            print("\nFailed files:")
            for r in failed:
                print(f"  - {Path(r.source).name}: {r.error}")
        
        # Save summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'input_dir': str(input_dir),
            'output_dir': str(output_dir),
            'total': len(pdf_files),
            'successful': len(successful),
            'failed': len(failed),
            'results': [
                {
                    'source': r.source,
                    'success': r.success,
                    'markdown': r.markdown_path,
                    'error': r.error
                }
                for r in results
            ]
        }
        summary_path = output_dir / '_conversion_summary.json'
        summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print(f"\nSummary saved: {summary_path}")
        
        return results


def main():
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        sys.exit(0)
    
    # Parse arguments
    args = sys.argv[1:]
    
    batch_mode = '--batch' in args
    ocr_enabled = '--ocr' in args
    save_json = '--json' in args
    extract_tables = '--tables' in args
    all_options = '--all' in args
    recursive = '--recursive' in args
    
    # Remove flags
    path_args = [a for a in args if not a.startswith('--')]
    
    if not path_args:
        print("Error: Please specify input path")
        print("Usage: python pdf_to_markdown.py [--batch] input [output_dir]")
        sys.exit(1)
    
    # Configure options
    options = ConversionOptions(
        output_dir=path_args[1] if len(path_args) > 1 else "output/markdown",
        ocr_enabled=ocr_enabled or all_options,
        save_json=save_json or all_options,
        extract_tables=extract_tables or all_options,
        recursive=recursive
    )
    
    # Initialize converter
    try:
        converter = PDFToMarkdownConverter(options)
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Run conversion
    if batch_mode:
        converter.convert_batch(path_args[0], options.output_dir)
    else:
        result = converter.convert_file(path_args[0], options.output_dir)
        if result.success:
            print(f"\nOutput: {result.markdown_path}")
            if result.json_path:
                print(f"JSON:   {result.json_path}")
            if result.tables_count:
                print(f"Tables: {result.tables_count} extracted")
        else:
            print(f"\nError: {result.error}")
            sys.exit(1)


if __name__ == "__main__":
    main()
