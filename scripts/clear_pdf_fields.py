#!/usr/bin/env python3
"""
Clear all field values from a PDF, leaving only the blank template
"""

import os
import sys
import argparse
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject


def clear_pdf_fields(input_path, output_path):
    """
    Clear all field values from a PDF

    Args:
        input_path: Path to input PDF
        output_path: Path for output PDF with cleared fields
    """

    print("=" * 80)
    print("PDF FIELD CLEARER")
    print("=" * 80)
    print(f"\n📄 Input: {input_path}")
    print(f"📄 Output: {output_path}")

    # Read the PDF
    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Clone reader to writer (copies the structure)
    writer.append(reader)

    cleared_count = 0

    # Try to clear via AcroForm fields first
    if writer._root_object.get("/AcroForm"):
        fields = writer.get_fields()
        print(f"\n🔍 Found {len(fields)} AcroForm fields to clear")

        # Clear all field values by setting them to empty string
        for field_name in fields.keys():
            try:
                writer.update_page_form_field_values(
                    None,  # Apply to all pages
                    {field_name: ""}
                )
                cleared_count += 1
            except Exception as e:
                print(f"  ⚠️  Warning: Could not clear {field_name}: {e}")

        print(f"✅ Cleared {cleared_count} AcroForm fields")

    # Also clear Widget annotations (D&D Beyond style)
    widget_count = 0
    image_count = 0
    for page_num, page in enumerate(writer.pages):
        if "/Annots" in page:
            for annot in page["/Annots"]:
                annot_obj = annot.get_object()
                if annot_obj.get("/Subtype") == "/Widget":
                    # Clear the value
                    if "/V" in annot_obj:
                        annot_obj[NameObject("/V")] = TextStringObject("")
                        widget_count += 1
                    # Also clear appearance state for checkboxes
                    if "/AS" in annot_obj:
                        annot_obj[NameObject("/AS")] = NameObject("/Off")

                    # Remove embedded images from widget appearance
                    if "/AP" in annot_obj:
                        del annot_obj[NameObject("/AP")]
                        image_count += 1

    if widget_count > 0:
        print(f"✅ Cleared {widget_count} Widget annotations")
    if image_count > 0:
        print(f"✅ Removed {image_count} embedded images")

    if cleared_count == 0 and widget_count == 0:
        print("\n⚠️  No form fields or widgets found in PDF")

    # Save output
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    with open(output_path, 'wb') as f:
        writer.write(f)

    print(f"\n💾 Saved to: {output_path}")
    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Clear all field values from a PDF'
    )

    parser.add_argument('--input', '-i', required=True,
                        help='Path to input PDF file')
    parser.add_argument('--output', '-o', required=True,
                        help='Path for output PDF file')

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)

    # Clear the fields
    clear_pdf_fields(args.input, args.output)


if __name__ == '__main__':
    main()
