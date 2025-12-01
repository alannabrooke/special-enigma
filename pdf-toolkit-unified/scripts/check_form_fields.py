#!/usr/bin/env python3
"""
check_form_fields.py - Check and fill PDF form fields

Determines if a PDF has fillable form fields and helps fill them.

USAGE:
  python check_form_fields.py input.pdf              # Check for fields
  python check_form_fields.py input.pdf --list       # List all fields
  python check_form_fields.py input.pdf --extract    # Extract field info to JSON
  python check_form_fields.py input.pdf --fill values.json -o output.pdf

EXAMPLES:
  python check_form_fields.py form.pdf
  python check_form_fields.py form.pdf --extract -o field_info.json
  python check_form_fields.py form.pdf --fill my_values.json -o filled.pdf
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def check_pypdf():
    if not PYPDF_AVAILABLE:
        print("Error: pypdf not installed. Run: pip install pypdf")
        sys.exit(1)


def get_annotation_field_id(annotation) -> Optional[str]:
    """Get full field ID from annotation."""
    components = []
    while annotation:
        field_name = annotation.get('/T')
        if field_name:
            components.append(str(field_name))
        annotation = annotation.get('/Parent')
    return ".".join(reversed(components)) if components else None


def check_fields(pdf_path: str) -> Dict[str, Any]:
    """Check if PDF has fillable form fields."""
    check_pypdf()
    
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    
    result = {
        'path': pdf_path,
        'has_fields': bool(fields),
        'field_count': len(fields) if fields else 0,
        'is_encrypted': reader.is_encrypted,
        'page_count': len(reader.pages)
    }
    
    return result


def list_fields(pdf_path: str) -> List[Dict]:
    """List all form fields in PDF."""
    check_pypdf()
    
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    
    if not fields:
        return []
    
    field_list = []
    
    for field_id, field in fields.items():
        field_type = field.get('/FT', 'Unknown')
        
        # Convert type codes to readable names
        type_map = {
            '/Tx': 'text',
            '/Btn': 'checkbox/radio',
            '/Ch': 'choice/dropdown'
        }
        readable_type = type_map.get(field_type, str(field_type))
        
        field_info = {
            'field_id': field_id,
            'type': readable_type,
            'value': field.get('/V', ''),
        }
        
        # For checkboxes, get possible values
        if field_type == '/Btn':
            states = field.get('/_States_', [])
            if states:
                field_info['options'] = [str(s) for s in states]
        
        # For choice fields, get options
        if field_type == '/Ch':
            opts = field.get('/_States_', [])
            if opts:
                field_info['options'] = opts
        
        field_list.append(field_info)
    
    return field_list


def extract_field_info(pdf_path: str, output_path: str = None) -> List[Dict]:
    """Extract detailed field information with positions."""
    check_pypdf()
    
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    
    if not fields:
        print("No form fields found in this PDF.")
        return []
    
    field_info = {}
    radio_groups = set()
    
    # First pass: identify field types
    for field_id, field in fields.items():
        ft = field.get('/FT')
        
        if field.get('/Kids'):
            if ft == '/Btn':
                radio_groups.add(field_id)
            continue
        
        info = {
            'field_id': field_id,
            'type': 'unknown'
        }
        
        if ft == '/Tx':
            info['type'] = 'text'
        elif ft == '/Btn':
            info['type'] = 'checkbox'
            states = field.get('/_States_', [])
            if len(states) >= 2:
                off_val = '/Off'
                on_val = states[0] if states[0] != '/Off' else states[1]
                info['checked_value'] = str(on_val)
                info['unchecked_value'] = str(off_val)
        elif ft == '/Ch':
            info['type'] = 'choice'
            states = field.get('/_States_', [])
            info['options'] = [str(s) for s in states]
        
        field_info[field_id] = info
    
    # Second pass: get positions from annotations
    for page_idx, page in enumerate(reader.pages):
        annotations = page.get('/Annots', [])
        for ann in annotations:
            field_id = get_annotation_field_id(ann)
            if field_id in field_info:
                field_info[field_id]['page'] = page_idx + 1
                field_info[field_id]['rect'] = ann.get('/Rect')
    
    result = list(field_info.values())
    
    # Sort by page, then position
    result.sort(key=lambda f: (f.get('page', 0), -(f.get('rect', [0,0,0,0])[1] if f.get('rect') else 0)))
    
    if output_path:
        Path(output_path).write_text(json.dumps(result, indent=2, default=str), encoding='utf-8')
        print(f"✓ Extracted {len(result)} fields → {output_path}")
    
    return result


def fill_form(pdf_path: str, values_path: str, output_path: str):
    """Fill form fields with values from JSON file."""
    check_pypdf()
    
    # Load values
    values = json.loads(Path(values_path).read_text(encoding='utf-8'))
    
    # Convert list format to dict if needed
    if isinstance(values, list):
        values_dict = {}
        for item in values:
            if 'field_id' in item and 'value' in item:
                page = item.get('page', 1)
                if page not in values_dict:
                    values_dict[page] = {}
                values_dict[page][item['field_id']] = item['value']
    else:
        # Assume it's already a dict of page -> field -> value
        values_dict = values
    
    # Read PDF
    reader = PdfReader(pdf_path)
    writer = PdfWriter(clone_from=reader)
    
    # Fill each page
    filled_count = 0
    for page_num, page_values in values_dict.items():
        page_idx = int(page_num) - 1
        if 0 <= page_idx < len(writer.pages):
            writer.update_page_form_field_values(
                writer.pages[page_idx],
                page_values,
                auto_regenerate=False
            )
            filled_count += len(page_values)
    
    writer.set_need_appearances_writer(True)
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    print(f"✓ Filled {filled_count} fields → {output_path}")


def main():
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print(__doc__)
        sys.exit(0)
    
    pdf_path = sys.argv[1]
    args = sys.argv[2:]
    
    # Parse output path
    output_path = None
    for i, arg in enumerate(args):
        if arg in ('-o', '--output') and i + 1 < len(args):
            output_path = args[i + 1]
            break
    
    if '--list' in args:
        fields = list_fields(pdf_path)
        if fields:
            print(f"Found {len(fields)} form field(s):\n")
            for f in fields:
                print(f"  {f['field_id']}")
                print(f"    Type: {f['type']}")
                if f.get('value'):
                    print(f"    Value: {f['value']}")
                if f.get('options'):
                    print(f"    Options: {f['options']}")
                print()
        else:
            print("No form fields found.")
    
    elif '--extract' in args:
        output = output_path or f"{Path(pdf_path).stem}_fields.json"
        extract_field_info(pdf_path, output)
    
    elif '--fill' in args:
        values_idx = args.index('--fill') + 1
        if values_idx >= len(args):
            print("Error: --fill requires a JSON file path")
            sys.exit(1)
        values_path = args[values_idx]
        output = output_path or f"{Path(pdf_path).stem}_filled.pdf"
        fill_form(pdf_path, values_path, output)
    
    else:
        # Default: just check
        result = check_fields(pdf_path)
        print(f"File: {result['path']}")
        print(f"Pages: {result['page_count']}")
        print(f"Encrypted: {result['is_encrypted']}")
        print()
        
        if result['has_fields']:
            print(f"✓ This PDF has {result['field_count']} fillable form field(s)")
            print()
            print("Next steps:")
            print(f"  python check_form_fields.py {pdf_path} --list")
            print(f"  python check_form_fields.py {pdf_path} --extract")
        else:
            print("✗ This PDF does not have fillable form fields")
            print()
            print("For non-fillable forms, you'll need to use annotation-based filling.")
            print("See docs/WORKFLOWS.md for instructions.")


if __name__ == "__main__":
    main()
