#!/usr/bin/env python3
"""
extract_content.py - Extract text and tables from PDFs using pdfplumber

This tool provides precise text and table extraction with layout awareness.
Use this when you need:
- Exact text positioning
- Clean table extraction to Excel/CSV
- Page-by-page processing
- Text within specific regions

For structured Markdown conversion, use pdf_to_markdown.py instead.

USAGE:
  python extract_content.py input.pdf [options]
  python extract_content.py --batch input_dir/ [options]

OPTIONS:
  --text         Extract text only
  --tables       Extract tables only
  --all          Extract everything (default)
  --format       Output format: txt, csv, xlsx, json (default: all)
  --output, -o   Output directory

EXAMPLES:
  python extract_content.py document.pdf
  python extract_content.py invoice.pdf --tables --format xlsx
  python extract_content.py --batch ./invoices/ --tables -o ./extracted/
"""

import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ContentExtractor:
    """Extract text and tables from PDFs using pdfplumber."""
    
    def __init__(self, output_dir: str = "output"):
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text(self, pdf_path: str, preserve_layout: bool = True) -> str:
        """
        Extract all text from PDF.
        
        Args:
            pdf_path: Path to PDF
            preserve_layout: If True, attempt to preserve spatial layout
        
        Returns:
            Extracted text as string
        """
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text(layout=preserve_layout) or ""
                if page_text.strip():
                    text_parts.append(f"--- Page {i} ---\n{page_text}")
        
        return "\n\n".join(text_parts)
    
    def extract_tables(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract all tables from PDF.
        
        Returns:
            List of tables with page number and data
        """
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()
                
                for table_num, table_data in enumerate(page_tables, 1):
                    if table_data and len(table_data) > 0:
                        # Try to identify header row
                        header = table_data[0] if table_data else []
                        rows = table_data[1:] if len(table_data) > 1 else []
                        
                        tables.append({
                            'page': page_num,
                            'table_num': table_num,
                            'header': header,
                            'rows': rows,
                            'raw': table_data
                        })
        
        return tables
    
    def extract_text_by_region(self, pdf_path: str, 
                                bbox: tuple, page_num: int = 1) -> str:
        """
        Extract text from a specific region.
        
        Args:
            pdf_path: Path to PDF
            bbox: Bounding box (x0, top, x1, bottom)
            page_num: Page number (1-indexed)
        
        Returns:
            Text within the region
        """
        with pdfplumber.open(pdf_path) as pdf:
            if page_num > len(pdf.pages):
                return ""
            page = pdf.pages[page_num - 1]
            cropped = page.within_bbox(bbox)
            return cropped.extract_text() or ""
    
    def save_text(self, text: str, output_path: Path):
        """Save extracted text to file."""
        output_path.write_text(text, encoding='utf-8')
        print(f"  ✓ Text saved: {output_path.name}")
    
    def save_tables_csv(self, tables: List[Dict], base_name: str):
        """Save tables as CSV files."""
        for table in tables:
            filename = f"{base_name}_p{table['page']}_t{table['table_num']}.csv"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in table['raw']:
                    if row:
                        writer.writerow(row)
            
            print(f"  ✓ Table saved: {filename}")
    
    def save_tables_xlsx(self, tables: List[Dict], base_name: str):
        """Save all tables to a single Excel file with multiple sheets."""
        if not PANDAS_AVAILABLE:
            print("  ⚠ pandas not available, falling back to CSV")
            return self.save_tables_csv(tables, base_name)
        
        filepath = self.output_dir / f"{base_name}_tables.xlsx"
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for table in tables:
                sheet_name = f"P{table['page']}_T{table['table_num']}"
                
                # Convert to DataFrame
                if table['header'] and table['rows']:
                    df = pd.DataFrame(table['rows'], columns=table['header'])
                else:
                    df = pd.DataFrame(table['raw'])
                
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"  ✓ Tables saved: {filepath.name} ({len(tables)} sheets)")
    
    def save_tables_json(self, tables: List[Dict], base_name: str):
        """Save tables as JSON."""
        filepath = self.output_dir / f"{base_name}_tables.json"
        filepath.write_text(json.dumps(tables, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"  ✓ Tables saved: {filepath.name}")
    
    def process_file(self, pdf_path: str, 
                     extract_text: bool = True,
                     extract_tables: bool = True,
                     output_format: str = "all") -> Dict[str, Any]:
        """
        Process a PDF file and extract content.
        
        Args:
            pdf_path: Path to PDF
            extract_text: Whether to extract text
            extract_tables: Whether to extract tables
            output_format: txt, csv, xlsx, json, or all
        
        Returns:
            Dictionary with extraction results
        """
        pdf_path = Path(pdf_path)
        base_name = pdf_path.stem
        result = {'source': str(pdf_path), 'success': True}
        
        print(f"Processing: {pdf_path.name}")
        
        try:
            # Extract text
            if extract_text:
                text = self.extract_text(str(pdf_path))
                result['text_length'] = len(text)
                
                if output_format in ('txt', 'all'):
                    text_path = self.output_dir / f"{base_name}.txt"
                    self.save_text(text, text_path)
                    result['text_file'] = str(text_path)
            
            # Extract tables
            if extract_tables:
                tables = self.extract_tables(str(pdf_path))
                result['tables_count'] = len(tables)
                
                if tables:
                    if output_format in ('csv', 'all'):
                        self.save_tables_csv(tables, base_name)
                    
                    if output_format in ('xlsx', 'all'):
                        self.save_tables_xlsx(tables, base_name)
                    
                    if output_format in ('json', 'all'):
                        self.save_tables_json(tables, base_name)
                else:
                    print("  ℹ No tables found")
        
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            print(f"  ✗ Error: {e}")
        
        return result
    
    def process_batch(self, input_dir: str, **kwargs) -> List[Dict]:
        """Process all PDFs in a directory."""
        input_dir = Path(input_dir)
        pdf_files = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF"))
        
        if not pdf_files:
            print(f"No PDF files found in {input_dir}")
            return []
        
        print(f"Found {len(pdf_files)} PDF files")
        print("-" * 40)
        
        results = []
        for pdf_file in pdf_files:
            result = self.process_file(str(pdf_file), **kwargs)
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r.get('success'))
        print("-" * 40)
        print(f"Completed: {successful}/{len(results)}")
        
        return results


def main():
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        sys.exit(0)
    
    args = sys.argv[1:]
    
    # Parse flags
    batch_mode = '--batch' in args
    text_only = '--text' in args
    tables_only = '--tables' in args
    
    # Get output format
    output_format = 'all'
    for i, arg in enumerate(args):
        if arg == '--format' and i + 1 < len(args):
            output_format = args[i + 1]
    
    # Get output directory
    output_dir = 'output/extracted'
    for i, arg in enumerate(args):
        if arg in ('--output', '-o') and i + 1 < len(args):
            output_dir = args[i + 1]
    
    # Remove flags to get path
    path_args = [a for a in args if not a.startswith('-') and a != output_format and a != output_dir]
    
    if not path_args:
        print("Error: Please specify input path")
        sys.exit(1)
    
    input_path = path_args[0]
    
    # Determine what to extract
    extract_text = not tables_only
    extract_tables = not text_only
    
    # Run extraction
    extractor = ContentExtractor(output_dir)
    
    if batch_mode:
        extractor.process_batch(
            input_path,
            extract_text=extract_text,
            extract_tables=extract_tables,
            output_format=output_format
        )
    else:
        extractor.process_file(
            input_path,
            extract_text=extract_text,
            extract_tables=extract_tables,
            output_format=output_format
        )


if __name__ == "__main__":
    main()
