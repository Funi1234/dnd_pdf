"""
PDF Image utilities for inserting character portraits
"""

import os
from pypdf.generic import NameObject, DictionaryObject, ArrayObject, NumberObject, StreamObject
from PIL import Image
import io


def find_image_field(page):
    """
    Find the image field annotation on a page

    Args:
        page: PDF page object

    Returns:
        Annotation object or None
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

    if "/Annots" not in page:
        return None

    for annot in page["/Annots"]:
        annot_obj = annot.get_object()

        if annot_obj.get("/Subtype") != "/Widget":
            continue

        field_name = annot_obj.get("/T")
        if field_name:
            field_name_str = str(field_name)
            for common in common_names:
                if common.lower() in field_name_str.lower():
                    return annot_obj

    return None


def get_field_rect(annot_obj):
    """
    Get the rectangle coordinates for a field

    Args:
        annot_obj: Annotation object

    Returns:
        tuple: (x, y, width, height) or None
    """
    if "/Rect" not in annot_obj:
        return None

    rect = annot_obj["/Rect"]
    x1, y1, x2, y2 = float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])

    return (x1, y1, x2 - x1, y2 - y1)


def embed_image_in_page(writer, page_num, image_path, field_name=None, verbose=True):
    """
    Embed an image into a specific page

    Args:
        writer: PdfWriter object
        page_num: Page number (0-indexed)
        image_path: Path to image file
        field_name: Optional field name (auto-detects if None)
        verbose: Print progress messages

    Returns:
        bool: True if successful, False otherwise
    """

    if not os.path.exists(image_path):
        if verbose:
            print(f"  ⚠️  Warning: Image not found: {image_path}")
        return False

    page = writer.pages[page_num]

    # Find the image field
    target_field = None
    if field_name:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                annot_obj = annot.get_object()
                if annot_obj.get("/T") == field_name:
                    target_field = annot_obj
                    break
    else:
        target_field = find_image_field(page)

    if not target_field:
        if verbose:
            print(f"  ⚠️  Warning: No image field found on page {page_num + 1}")
        return False

    # Get field dimensions
    rect_info = get_field_rect(target_field)
    if not rect_info:
        if verbose:
            print(f"  ⚠️  Warning: Could not determine field dimensions")
        return False

    x, y, width, height = rect_info

    # Load and resize image
    try:
        img = Image.open(image_path)

        # Convert to RGB if needed
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        # Calculate scaling to fit field while maintaining aspect ratio
        img_width, img_height = img.size
        scale = min(width / img_width, height / img_height)

        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

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
        target_field[NameObject("/AP")] = DictionaryObject()
        target_field["/AP"][NameObject("/N")] = ap_stream

        if verbose:
            print(f"  🖼️  Embedded portrait: {os.path.basename(image_path)} ({new_width}x{new_height}px)")

        return True

    except Exception as e:
        if verbose:
            print(f"  ⚠️  Warning: Failed to embed image: {e}")
        return False
