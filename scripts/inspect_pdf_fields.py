#!/usr/bin/env python3
"""
Inspect PDF form fields for debugging and discovery
"""

import json
import os
import sys
from pypdf import PdfReader

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def inspect_pdf(pdf_path, filter_str=None, show_values=False):
    """Inspect form fields in a PDF"""

    reader = PdfReader(pdf_path)
    fields = reader.get_fields()

    if not fields:
        print(f"❌ No form fields found in: {os.path.basename(pdf_path)}")
        return

    # Filter if requested
    if filter_str:
        fields = {k: v for k, v in fields.items() if filter_str.lower() in k.lower()}
        print(f"\n📋 Fields containing '{filter_str}': {len(fields)}")
    else:
        print(f"\n📋 Total form fields: {len(fields)}")

    # Group by prefix
    grouped = {}
    for name in fields.keys():
        prefix = name.split('_')[0] if '_' in name else 'Other'
        if prefix not in grouped:
            grouped[prefix] = []
        grouped[prefix].append(name)

    print(f"\n📊 Field groups:")
    for prefix, field_list in sorted(grouped.items()):
        print(f"  {prefix}: {len(field_list)} fields")

    # Show field details
    print(f"\n📝 Field details:")
    for name, field in sorted(fields.items()):
        field_type = field.get('/FT', 'Unknown')

        if show_values:
            value = field.get('/V', '')
            print(f"  {name}")
            print(f"    Type: {field_type}")
            if value:
                print(f"    Value: {value}")
        else:
            print(f"  {name}: {field_type}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Inspect PDF form fields')
    parser.add_argument('pdf', nargs='?', help='Path to PDF file (or use --base/--spell)')
    parser.add_argument('--base', action='store_true', help='Inspect base character sheet')
    parser.add_argument('--spell', action='store_true', help='Inspect spell sheet template')
    parser.add_argument('--filter', '-f', help='Filter fields containing this string')
    parser.add_argument('--values', '-v', action='store_true', help='Show current field values')
    parser.add_argument('--export', '-e', help='Export fields to JSON file')

    args = parser.parse_args()

    # Determine which PDF to inspect
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    if args.base:
        pdf_path = os.path.join(project_root, 'data/source_pdfs/Neez-Artificer_EU A4.pdf')
    elif args.spell:
        pdf_path = os.path.join(project_root, 'data/source_pdfs/Spell Sheet-2_EU A4.pdf')
    elif args.pdf:
        pdf_path = args.pdf
    else:
        parser.print_help()
        return

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    print("=" * 70)
    print(f"🔍 INSPECTING: {os.path.basename(pdf_path)}")
    print("=" * 70)

    inspect_pdf(pdf_path, args.filter, args.values)

    # Export if requested
    if args.export:
        reader = PdfReader(pdf_path)
        fields = reader.get_fields()

        export_data = {}
        for name, field in fields.items():
            export_data[name] = {
                'type': str(field.get('/FT', 'Unknown')),
                'value': str(field.get('/V', ''))
            }

        with open(args.export, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\n✅ Exported {len(export_data)} fields to: {args.export}")


if __name__ == '__main__':
    main()
