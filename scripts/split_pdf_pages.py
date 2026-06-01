#!/usr/bin/env python3
"""
Split a PDF into individual page files
"""

import os
import sys
import argparse
from pypdf import PdfReader, PdfWriter


def split_pdf(input_path, output_dir):
    """
    Split a PDF into individual pages

    Args:
        input_path: Path to input PDF
        output_dir: Directory to save individual pages
    """

    # Read the PDF
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    print("=" * 80)
    print("PDF PAGE SPLITTER")
    print("=" * 80)
    print(f"\n📄 Input: {input_path}")
    print(f"📊 Total pages: {total_pages}")
    print(f"📁 Output directory: {output_dir}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Split each page
    print(f"\n✂️  Splitting pages...")
    for page_num in range(total_pages):
        # Create a new PDF writer for this page
        writer = PdfWriter()
        writer.add_page(reader.pages[page_num])

        # Output filename
        output_filename = f"page_{page_num + 1}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        # Write the page
        with open(output_path, 'wb') as f:
            writer.write(f)

        print(f"  ✅ Page {page_num + 1}/{total_pages} -> {output_filename}")

    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)
    print(f"\nSplit {total_pages} pages into {output_dir}/")
    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Split a PDF into individual page files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split Artificer template
  python scripts/split_pdf_pages.py \\
    --input "data/source_pdfs/class_specific/artificer/Artificer_EU A4.pdf" \\
    --output data/source_pdfs/class_specific/artificer/pages

  # Split D&D Beyond PDF
  python scripts/split_pdf_pages.py \\
    --input "examples/input_sheets/Dwarf_Cleric_1.pdf" \\
    --output temp/dwarf_cleric_pages
        """
    )

    parser.add_argument('--input', '-i', required=True,
                        help='Path to input PDF file')
    parser.add_argument('--output', '-o', required=True,
                        help='Directory to save individual page PDFs')

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)

    # Split the PDF
    split_pdf(args.input, args.output)


if __name__ == '__main__':
    main()
