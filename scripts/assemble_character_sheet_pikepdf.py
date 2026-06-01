#!/usr/bin/env python3
"""
Assemble a custom character sheet from multiple page templates using pikepdf
"""

import json
import os
import sys
import argparse
import pikepdf

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.field_mappers import (
    map_core_fields,
    map_character_info,
    map_abilities,
    map_skills,
    map_saving_throws,
    map_combat,
    map_spells,
    map_proficiencies,
    map_weapons,
    map_background
)
from src.field_mappers.spells import calculate_spell_pages_needed
from src.field_mappers.equipment import map_equipment, calculate_equipment_pages_needed


def load_character_data(file_path):
    """Load character data from JSON file"""
    with open(file_path) as f:
        data = json.load(f)
        if 'character' in data:
            return data['character']
        return data


def extract_proficient_saves(char_data):
    """Extract proficient saving throws from character data"""
    proficient = []
    if 'saving_throws' in char_data:
        for key, value in char_data['saving_throws'].items():
            if key.endswith('_proficient') and value:
                ability = key.replace('_proficient', '')
                proficient.append(ability)
    return proficient


def create_field_mappings(char_data, section, layout='separate', level_filter=None, page_offset=0, template_type='main'):
    """Create field mappings for a specific section"""
    fields = {}
    class_level = char_data['character_info']['class_and_level']
    level = int(class_level.rsplit(' ', 1)[1]) if ' ' in class_level else 5
    proficient_abilities = extract_proficient_saves(char_data)

    if section == 'front':
        map_core_fields(char_data, fields)
        map_character_info(char_data, fields, layout=layout)
        map_abilities(char_data, fields, layout=layout)
        map_skills(char_data, fields, layout=layout)
        map_saving_throws(char_data, fields, layout=layout, proficient_abilities=proficient_abilities)
        map_combat(char_data, fields, layout=layout, level=level)
        map_proficiencies(char_data, fields, layout=layout)
        map_weapons(char_data, fields, layout=layout)
    elif section == 'background':
        # Use generic template type for D&D Beyond background pages
        map_background(char_data, fields, background_page='regular', template_type='generic')
    elif section == 'spells':
        map_spells(char_data, fields, layout=layout, level_filter=level_filter, page_offset=page_offset, template_type=template_type)
    elif section == 'equipment':
        map_equipment(char_data, fields, page_offset=page_offset)

    return fields


def fill_pdf_fields(pdf, field_mappings):
    """Fill fields in a pikepdf PDF object"""
    filled_count = 0

    # Fields that need smaller font for long text
    small_font_fields = ['Backstory', 'AdditionalNotes1', 'AdditionalNotes2', 'Appearance']

    for page in pdf.pages:
        if '/Annots' in page:
            for annot in page.Annots:
                if annot.Subtype == '/Widget' and '/T' in annot:
                    field_name = str(annot.T)
                    if field_name in field_mappings:
                        value = str(field_mappings[field_name])

                        # Set smaller font for long text fields
                        if field_name in small_font_fields and '/DA' in annot:
                            # Set to 6pt font for long backstory text
                            annot.DA = pikepdf.String('/Helv 6 Tf 0 g')

                        # Handle checkboxes (values like /Yes, /Off)
                        if value.startswith('/'):
                            annot.V = pikepdf.Name(value)
                            # Also set appearance state for checkboxes
                            if '/AS' in annot or annot.get('/FT') == pikepdf.Name('/Btn'):
                                annot.AS = pikepdf.Name(value)
                        else:
                            # Regular text field
                            annot.V = pikepdf.String(value)

                        filled_count += 1
    return filled_count


def embed_portrait_pikepdf(pdf, page_index, portrait_path):
    """Embed portrait image in background page using pikepdf"""
    from PIL import Image
    import io

    if not os.path.exists(portrait_path):
        return False

    page = pdf.pages[page_index]

    # Find CHARACTER IMAGE field
    target_annot = None
    if '/Annots' in page:
        for annot in page.Annots:
            if annot.Subtype == '/Widget' and '/T' in annot:
                if 'IMAGE' in str(annot.T).upper():
                    target_annot = annot
                    break

    if not target_annot:
        print("  ⚠️  No image field found")
        return False

    # Get field rectangle
    rect = target_annot.Rect
    x, y, x2, y2 = float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])
    width, height = x2 - x, y2 - y

    # Load and resize image
    img = Image.open(portrait_path)
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    # Scale to fit
    img_width, img_height = img.size
    scale = min(width / img_width, height / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Convert to JPEG bytes
    img_bytes = io.BytesIO()
    img_resized.save(img_bytes, format='JPEG', quality=85)
    img_bytes.seek(0)

    # Create image XObject
    img_obj = pikepdf.Stream(pdf, img_bytes.read())
    img_obj.Type = pikepdf.Name('/XObject')
    img_obj.Subtype = pikepdf.Name('/Image')
    img_obj.Width = new_width
    img_obj.Height = new_height
    img_obj.ColorSpace = pikepdf.Name('/DeviceRGB')
    img_obj.BitsPerComponent = 8
    img_obj.Filter = pikepdf.Name('/DCTDecode')

    # Add to page resources
    if '/Resources' not in page:
        page.Resources = pikepdf.Dictionary()
    if '/XObject' not in page.Resources:
        page.Resources.XObject = pikepdf.Dictionary()

    img_name = pikepdf.Name('/CharImage')
    page.Resources.XObject[img_name] = img_obj

    # Create appearance stream
    x_offset = (width - new_width) / 2
    y_offset = (height - new_height) / 2

    appearance_stream = f"""q
{new_width} 0 0 {new_height} {x + x_offset} {y + y_offset} cm
/CharImage Do
Q"""

    ap_stream = pikepdf.Stream(pdf, appearance_stream.encode())
    ap_stream.Type = pikepdf.Name('/XObject')
    ap_stream.Subtype = pikepdf.Name('/Form')
    ap_stream.BBox = pikepdf.Array([x, y, x2, y2])
    xobj_dict = pikepdf.Dictionary()
    xobj_dict[img_name] = img_obj

    res_dict = pikepdf.Dictionary()
    res_dict[pikepdf.Name('/XObject')] = xobj_dict

    ap_stream.Resources = res_dict

    # Set appearance
    if '/AP' not in target_annot:
        target_annot.AP = pikepdf.Dictionary()
    target_annot.AP.N = ap_stream

    print(f"  🖼️  Embedded portrait: {os.path.basename(portrait_path)} ({new_width}x{new_height}px)")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Assemble custom character sheet from multiple page templates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/assemble_character_sheet_pikepdf.py \\
    --data data/neez_character_data_clean.json \\
    --output output/neez_custom.pdf \\
    --pages \\
      "class_specific/artificer/artificer_front_separate.pdf:front" \\
      "generic/background_regular.pdf:background" \\
      "generic/spells_main.pdf:spells"
        """
    )

    parser.add_argument('--data', '-d', required=True, help='Path to character data JSON file')
    parser.add_argument('--output', '-o', required=True, help='Path for output PDF file')
    parser.add_argument('--pages', '-p', nargs='+', required=True,
                        help='Page templates: "path/to/template.pdf:section"')
    parser.add_argument('--layout', '-l', choices=['combined', 'separate'], default='separate',
                        help='Layout type for front pages. Default: separate')

    args = parser.parse_args()

    print("=" * 80)
    print("CHARACTER SHEET ASSEMBLER (pikepdf)")
    print("=" * 80)

    # Load character data
    print(f"\n📖 Loading character data: {args.data}")
    char_data = load_character_data(args.data)
    print(f"  Character: {char_data['character_info']['name']}")
    print(f"  Class: {char_data['character_info']['class_and_level']}")

    # Auto-expand spell pages
    expanded_pages = []
    base_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'source_pdfs')

    for page_spec in args.pages:
        parts = page_spec.split(':')
        if len(parts) != 2:
            print(f"❌ Error: Invalid page spec '{page_spec}'")
            sys.exit(1)

        template_rel_path, section = parts

        # Auto-expand spells into multiple pages
        if section == 'spells':
            spell_pages = calculate_spell_pages_needed(char_data)
            print(f"\n📊 Auto-generating {len(spell_pages)} spell pages:")
            for template, level, page_offset in spell_pages:
                template_path = f"generic/{template}.pdf"
                # Determine template type from template name
                tpl_type = 'main' if template == 'spells_main' else 'additional'
                expanded_pages.append((template_path, 'spells', level, page_offset, tpl_type))
                level_label = 'Cantrips' if level == '0' else f'Level {level}'
                page_num = page_offset + 1
                print(f"   • {template}.pdf - {level_label} (page {page_num})")
        # Auto-expand equipment into multiple pages
        elif section == 'equipment':
            eq_pages = calculate_equipment_pages_needed(char_data)
            print(f"\n📦 Auto-generating {len(eq_pages)} equipment pages:")
            for page_offset in eq_pages:
                if page_offset == 0:
                    template_path = "generic/com_feat_equip.pdf"
                    expanded_pages.append((template_path, 'equipment', None, page_offset, 'main'))
                    print(f"   • com_feat_equip.pdf (main)")
                else:
                    template_path = "generic/com_feat_equip_additional.pdf"
                    expanded_pages.append((template_path, 'equipment', None, page_offset, 'additional'))
                    print(f"   • com_feat_equip_additional.pdf (page {page_offset + 1})")
        else:
            expanded_pages.append((template_rel_path, section, None, 0, 'main'))

    # Create output PDF
    output_pdf = pikepdf.new()

    print(f"\n📄 Assembling {len(expanded_pages)} pages...")
    background_page_index = None
    page_metadata = []  # Track (section, level_filter, page_offset, template_type) for each page

    for template_rel_path, section, level_filter, page_offset, template_type in expanded_pages:
        template_path = os.path.join(base_path, template_rel_path)

        if not os.path.exists(template_path):
            print(f"❌ Error: Template not found: {template_path}")
            sys.exit(1)

        # Open template and copy page
        template_pdf = pikepdf.open(template_path)
        for page in template_pdf.pages:
            output_pdf.pages.append(page)

        # Track background page
        if section == 'background':
            background_page_index = len(output_pdf.pages) - 1

        # Store metadata for field filling
        page_metadata.append((section, level_filter, page_offset, template_type))

        template_pdf.close()

    # Fill all fields
    print(f"\n✍️  Filling fields...")
    total_filled = 0
    for i, (section, level_filter, page_offset, template_type) in enumerate(page_metadata):
        field_mappings = create_field_mappings(char_data, section, layout=args.layout,
                                               level_filter=level_filter, page_offset=page_offset,
                                               template_type=template_type)

        # Fill only the current page
        page = output_pdf.pages[i]
        filled = 0
        if '/Annots' in page:
            for annot in page.Annots:
                if annot.Subtype == '/Widget' and '/T' in annot:
                    field_name = str(annot.T)
                    if field_name in field_mappings:
                        value = str(field_mappings[field_name])

                        # Handle checkboxes
                        if value.startswith('/'):
                            annot.V = pikepdf.Name(value)
                            if '/AS' in annot or annot.get('/FT') == pikepdf.Name('/Btn'):
                                annot.AS = pikepdf.Name(value)
                        else:
                            annot.V = pikepdf.String(value)

                        filled += 1

        total_filled += filled

        # Print fill status for paginated sections
        if section == 'spells':
            level_label = 'Cantrips' if level_filter == '0' else f'Lvl {level_filter}'
            print(f"  Page {i+1}: {level_label} pg {page_offset+1} - {filled} fields")
        elif section == 'equipment':
            print(f"  Page {i+1}: Equipment pg {page_offset+1} - {filled} fields")

    print(f"  ✅ Total filled: {total_filled} fields")

    # Add portrait if background page exists
    if background_page_index is not None:
        portrait_path = char_data['character_info'].get('portrait_image')
        if portrait_path:
            print(f"\n🖼️  Embedding portrait...")
            embed_portrait_pikepdf(output_pdf, background_page_index, portrait_path)

    # Save
    print(f"\n💾 Saving assembled sheet...")
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
    output_pdf.save(args.output)
    output_pdf.close()

    print(f"  Saved to: {args.output}")
    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)
    print(f"\nAssembled {len(expanded_pages)} pages")
    print("View in Brave browser for best results")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
