#!/usr/bin/env python3
"""
Add an image to a PDF field (typically a character portrait)
"""

import os
import sys
import argparse
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, DictionaryObject, ArrayObject, NumberObject, StreamObject
from PIL import Image
import io


def find_image_field(reader):
    """
    Auto-detect the image field in a PDF

    Looks for fields commonly used for character portraits

    Returns:
        tuple: (field_name, page_num, annot_obj) or (None, None, None)
    """

    common_names = [
        'CharacterImage',
        'Character Image',
        'Portrait',
        'PORTRAIT',
        'Image',
        'CHARACTER IMAGE',
        'Char Image'
    ]

    # Search through all pages for widget annotations
    for page_num, page in enumerate(reader.pages):
        if "/Annots" not in page:
            continue

        for annot in page["/Annots"]:
            annot_obj = annot.get_object()

            if annot_obj.get("/Subtype") != "/Widget":
                continue

            # Check if this is a likely image field
            field_name = annot_obj.get("/T")
            if field_name:
                field_name_str = str(field_name)
                for common in common_names:
                    if common.lower() in field_name_str.lower():
                        return field_name_str, page_num, annot_obj

    return None, None, None


def get_field_rect(annot_obj):
    """
    Get the rectangle coordinates for a field

    Returns:
        tuple: (x, y, width, height)
    """
    if "/Rect" not in annot_obj:
        return None

    rect = annot_obj["/Rect"]
    x1, y1, x2, y2 = float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])

    return (x1, y1, x2 - x1, y2 - y1)


def add_image_to_pdf(input_pdf, output_pdf, image_path, field_name=None):
    """
    Add an image to a PDF field

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path for output PDF
        image_path: Path to image file (PNG/JPG)
        field_name: Optional field name (auto-detects if None)
    """

    print("=" * 80)
    print("PDF IMAGE INSERTER")
    print("=" * 80)
    print(f"\n📄 Input PDF: {input_pdf}")
    print(f"🖼️  Image: {image_path}")

    # Validate inputs
    if not os.path.exists(input_pdf):
        print(f"❌ Error: Input PDF not found: {input_pdf}")
        sys.exit(1)

    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found: {image_path}")
        sys.exit(1)

    # Read the PDF
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    writer.append(reader)

    # Find the image field
    if field_name:
        print(f"🔍 Looking for field: {field_name}")
        target_field = None
        target_page_num = None

        for page_num, page in enumerate(reader.pages):
            if "/Annots" not in page:
                continue
            for annot in page["/Annots"]:
                annot_obj = annot.get_object()
                if annot_obj.get("/T") == field_name:
                    target_field = annot_obj
                    target_page_num = page_num
                    break
            if target_field:
                break

        if not target_field:
            print(f"❌ Error: Field '{field_name}' not found")
            sys.exit(1)
    else:
        print("🔍 Auto-detecting image field...")
        field_name, target_page_num, target_field = find_image_field(reader)

        if not target_field:
            print("❌ Error: No image field found. Try specifying --field-name")
            sys.exit(1)

        print(f"✅ Found image field: {field_name} on page {target_page_num + 1}")

    # Get field dimensions
    rect_info = get_field_rect(target_field)
    if not rect_info:
        print("❌ Error: Could not determine field dimensions")
        sys.exit(1)

    x, y, width, height = rect_info
    print(f"📐 Field size: {width:.1f} x {height:.1f} pts")

    # Load and resize image
    print(f"\n📷 Processing image...")
    img = Image.open(image_path)

    # Convert to RGB if needed
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    # Calculate scaling to fit field while maintaining aspect ratio
    img_width, img_height = img.size
    scale = min(width / img_width, height / img_height)

    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    print(f"  Original: {img_width} x {img_height} px")
    print(f"  Resized: {new_width} x {new_height} px")

    # Resize image
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Convert to bytes
    img_bytes = io.BytesIO()
    img_resized.save(img_bytes, format='JPEG', quality=85)
    img_bytes.seek(0)

    # Create XObject for the image
    img_obj = StreamObject()
    img_obj._data = img_bytes.read()
    img_obj.update({
        NameObject("/Type"): NameObject("/XObject"),
        NameObject("/Subtype"): NameObject("/Image"),
        NameObject("/Width"): NumberObject(new_width),
        NameObject("/Height"): NumberObject(new_height),
        NameObject("/ColorSpace"): NameObject("/DeviceRGB"),
        NameObject("/BitsPerComponent"): NumberObject(8),
        NameObject("/Filter"): NameObject("/DCTDecode"),
    })

    # Add image to PDF resources
    page = writer.pages[target_page_num]
    if "/Resources" not in page:
        page[NameObject("/Resources")] = DictionaryObject()

    if "/XObject" not in page["/Resources"]:
        page["/Resources"][NameObject("/XObject")] = DictionaryObject()

    img_name = NameObject("/CharImage")
    page["/Resources"]["/XObject"][img_name] = img_obj

    # Create appearance stream for the widget
    # Center the image in the field
    x_offset = (width - new_width) / 2
    y_offset = (height - new_height) / 2

    appearance_stream = f"""q
{new_width} 0 0 {new_height} {x + x_offset} {y + y_offset} cm
/CharImage Do
Q"""

    ap_stream = StreamObject()
    ap_stream._data = appearance_stream.encode()
    ap_stream.update({
        NameObject("/Type"): NameObject("/XObject"),
        NameObject("/Subtype"): NameObject("/Form"),
        NameObject("/BBox"): ArrayObject([
            NumberObject(x), NumberObject(y),
            NumberObject(x + width), NumberObject(y + height)
        ]),
        NameObject("/Resources"): DictionaryObject({
            NameObject("/XObject"): DictionaryObject({
                img_name: img_obj
            })
        })
    })

    # Update the widget annotation with the appearance
    # Find the annotation in the writer
    writer_page = writer.pages[target_page_num]
    if "/Annots" in writer_page:
        for annot in writer_page["/Annots"]:
            annot_obj = annot.get_object()
            if annot_obj.get("/T") == field_name:
                # Set the appearance
                if "/AP" not in annot_obj:
                    annot_obj[NameObject("/AP")] = DictionaryObject()

                annot_obj["/AP"][NameObject("/N")] = ap_stream
                print("✅ Image embedded in field")
                break

    # Save output
    os.makedirs(os.path.dirname(output_pdf) if os.path.dirname(output_pdf) else '.', exist_ok=True)
    with open(output_pdf, 'wb') as f:
        writer.write(f)

    print(f"\n💾 Saved to: {output_pdf}")
    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Add an image to a PDF field (character portrait)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect image field
  python scripts/add_image_to_pdf.py \\
    --input data/source_pdfs/generic/background_regular.pdf \\
    --image path/to/portrait.png \\
    --output output/background_with_portrait.pdf

  # Specify field name
  python scripts/add_image_to_pdf.py \\
    --input data/source_pdfs/generic/background_regular.pdf \\
    --image path/to/portrait.png \\
    --output output/background_with_portrait.pdf \\
    --field "CharacterImage"
        """
    )

    parser.add_argument('--input', '-i', required=True,
                        help='Path to input PDF file')
    parser.add_argument('--image', '-m', required=True,
                        help='Path to image file (PNG/JPG)')
    parser.add_argument('--output', '-o', required=True,
                        help='Path for output PDF file')
    parser.add_argument('--field', '-f',
                        help='Field name for the image (auto-detects if not specified)')

    args = parser.parse_args()

    add_image_to_pdf(args.input, args.output, args.image, args.field)


if __name__ == '__main__':
    main()
