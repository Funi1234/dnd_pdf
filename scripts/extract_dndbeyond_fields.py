#!/usr/bin/env python3
"""
Extract form fields from D&D Beyond PDFs
D&D Beyond uses Widget annotations instead of standard AcroForm fields
"""

import json
import os
import sys
from pypdf import PdfReader

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def extract_dndbeyond_fields(pdf_path):
    """Extract all form field values from D&D Beyond PDF, organized by page"""

    reader = PdfReader(pdf_path)
    pages_data = {}

    print(f"\n📄 Extracting from: {os.path.basename(pdf_path)}")
    print(f"  Pages: {len(reader.pages)}")

    # Extract fields from page annotations
    for page_num, page in enumerate(reader.pages, 1):
        if '/Annots' not in page:
            continue

        annotations = page['/Annots']
        page_fields = {}

        for annot_ref in annotations:
            try:
                annot = annot_ref.get_object()

                # Check if it's a widget (form field)
                if annot.get('/Subtype') == '/Widget' and '/T' in annot:
                    field_name = str(annot['/T'])
                    field_value = str(annot.get('/V', ''))
                    field_type = str(annot.get('/FT', 'Unknown'))

                    # Store field data
                    page_fields[field_name] = {
                        'value': field_value,
                        'field_type': field_type
                    }

            except Exception as e:
                pass  # Skip problematic annotations

        if page_fields:
            pages_data[f"page_{page_num}"] = {
                'page_number': page_num,
                'field_count': len(page_fields),
                'fields': page_fields
            }
            print(f"    Page {page_num}: {len(page_fields)} fields")

    return pages_data

def main():
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(description='Extract D&D Beyond PDF fields and convert to clean format')
    parser.add_argument('pdf', help='Path to D&D Beyond PDF')
    parser.add_argument('--output', '-o', help='Output JSON file (raw extraction)')
    parser.add_argument('--no-clean', action='store_true', help='Skip automatic conversion to clean format')

    args = parser.parse_args()

    # Determine PDF path
    pdf_path = args.pdf

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    print("=" * 70)
    print("D&D BEYOND FIELD EXTRACTION")
    print("=" * 70)

    # Extract fields
    pages_data = extract_dndbeyond_fields(pdf_path)

    # Count total fields
    total_fields = sum(page_data['field_count'] for page_data in pages_data.values())
    print(f"\n✅ Total fields extracted: {total_fields}")

    # Show sample fields from page 1
    print(f"\n📋 Sample fields from Page 1:")
    if 'page_1' in pages_data:
        sample_fields = ['CharacterName', 'CLASS  LEVEL', 'RACE', 'spellSaveDC0', 'spellAtkBonus0']
        for field_name in sample_fields:
            if field_name in pages_data['page_1']['fields']:
                value = pages_data['page_1']['fields'][field_name]['value']
                print(f"  {field_name}: '{value}'")

    # Save to file
    if args.output:
        output_path = args.output
    else:
        filename = os.path.basename(pdf_path).replace('.pdf', '_extracted.json')
        output_path = os.path.join(project_root, 'data', filename)

    output_data = {
        'metadata': {
            'source_pdf': os.path.basename(pdf_path),
            'total_pages': len(pages_data),
            'total_fields': total_fields
        },
        'pages': pages_data
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Saved raw extraction to: {output_path}")

    # Automatically convert to clean format
    if not args.no_clean:
        clean_output_path = output_path.replace('_raw.json', '_clean.json')
        if clean_output_path == output_path:  # Didn't have _raw suffix
            clean_output_path = output_path.replace('.json', '_clean.json')

        print(f"\n🔄 Converting to clean format...")

        converter_script = os.path.join(project_root, 'scripts', 'convert_raw_to_clean.py')
        result = subprocess.run(
            [sys.executable, converter_script, '--input', output_path, '--output', clean_output_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Show converter output
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"  {line}")
        else:
            print(f"⚠️  Conversion failed: {result.stderr}")

    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
