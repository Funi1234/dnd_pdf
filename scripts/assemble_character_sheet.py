#!/usr/bin/env python3
"""
Assemble a custom character sheet from multiple page templates
"""

import json
import os
import sys
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pypdf import PdfReader, PdfWriter
from src.pdf_utils import modify_field_font_size, fill_widget_fields
from src.image_utils import embed_image_in_page
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


def load_character_data(file_path):
    """Load character data from JSON file"""
    with open(file_path) as f:
        data = json.load(f)
        # Handle both formats: {'character': {...}} or direct {...}
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


def create_field_mappings(char_data, section, layout='separate'):
    """
    Create field mappings for a specific section

    Args:
        char_data: Character data dictionary
        section: Section to map ('front', 'background', 'spells', etc.)
        layout: Layout type ('combined' or 'separate')

    Returns:
        dict: Field mappings for this section
    """

    fields = {}

    # Extract level for calculations
    class_level = char_data['character_info']['class_and_level']
    level = int(class_level.rsplit(' ', 1)[1]) if ' ' in class_level else 5

    # Extract proficient saves
    proficient_abilities = extract_proficient_saves(char_data)

    if section == 'front':
        # Front page: character info, abilities, skills, saves, combat
        map_core_fields(char_data, fields)
        map_character_info(char_data, fields, layout=layout)
        map_abilities(char_data, fields, layout=layout)
        map_skills(char_data, fields, layout=layout)
        map_saving_throws(char_data, fields, layout=layout, proficient_abilities=proficient_abilities)
        map_combat(char_data, fields, layout=layout, level=level)
        map_proficiencies(char_data, fields, layout=layout)
        map_weapons(char_data, fields, layout=layout)

    elif section == 'background':
        # Background page: personality, physical traits
        map_background(char_data, fields, background_page='regular')

    elif section == 'spells':
        # Spell pages
        map_spells(char_data, fields, layout=layout)

    return fields


def main():
    parser = argparse.ArgumentParser(
        description='Assemble custom character sheet from multiple page templates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Custom Neez sheet: Artificer front + Background with portrait + Spell pages
  python scripts/assemble_character_sheet.py \\
    --data data/neez_character_data_clean.json \\
    --output output/neez_custom.pdf \\
    --pages \\
      "class_specific/artificer/artificer_front_separate.pdf:front" \\
      "generic/background_regular.pdf:background" \\
      "generic/spells_main.pdf:spells"
        """
    )

    parser.add_argument('--data', '-d', required=True,
                        help='Path to character data JSON file')
    parser.add_argument('--output', '-o', required=True,
                        help='Path for output PDF file')
    parser.add_argument('--pages', '-p', nargs='+', required=True,
                        help='Page templates in format: "path/to/template.pdf:section"')
    parser.add_argument('--layout', '-l', choices=['combined', 'separate'], default='separate',
                        help='Layout type for front pages. Default: separate')

    args = parser.parse_args()

    print("=" * 80)
    print("CHARACTER SHEET ASSEMBLER")
    print("=" * 80)

    # Load character data
    print(f"\n📖 Loading character data: {args.data}")
    char_data = load_character_data(args.data)
    print(f"  Character: {char_data['character_info']['name']}")
    print(f"  Class: {char_data['character_info']['class_and_level']}")

    # Parse page specifications and collect all mappings
    print(f"\n📄 Loading {len(args.pages)} page templates...")
    writer = PdfWriter()
    all_field_mappings = {}
    background_page_index = None

    base_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'source_pdfs')

    for page_spec in args.pages:
        parts = page_spec.split(':')
        if len(parts) != 2:
            print(f"❌ Error: Invalid page spec '{page_spec}'. Expected 'path:section'")
            sys.exit(1)

        template_rel_path, section = parts

        # Resolve template path
        template_path = os.path.join(base_path, template_rel_path)
        if not os.path.exists(template_path):
            print(f"❌ Error: Template not found: {template_path}")
            sys.exit(1)

        print(f"  📄 {os.path.basename(template_path)} ({section})")

        # Load template page
        reader = PdfReader(template_path)

        # Add each page individually to preserve content
        for page in reader.pages:
            writer.add_page(page)

        # Track background page for portrait insertion
        if section == 'background':
            background_page_index = len(writer.pages) - 1

        # Get field mappings for this section
        field_mappings = create_field_mappings(char_data, section, layout=args.layout)
        all_field_mappings.update(field_mappings)
        print(f"     Added {len(field_mappings)} field mappings")

    # Now fill all fields at once (both AcroForm and Widget annotations)
    print(f"\n✍️  Filling {len(all_field_mappings)} fields...")

    # Try AcroForm fields first
    acro_filled = 0
    for field_name, value in all_field_mappings.items():
        try:
            writer.update_page_form_field_values(
                None,  # Apply to all pages
                {field_name: str(value)}
            )
            acro_filled += 1
        except Exception as e:
            pass

    # Fill Widget annotations
    widget_filled = fill_widget_fields(writer, all_field_mappings)

    total_filled = acro_filled + widget_filled
    print(f"  ✅ Filled {total_filled} fields (AcroForm: {acro_filled}, Widgets: {widget_filled})")

    # Insert portrait if background page exists
    if background_page_index is not None:
        portrait_path = char_data['character_info'].get('portrait_image')
        if portrait_path:
            print(f"\n🖼️  Embedding character portrait...")
            embed_image_in_page(writer, background_page_index, portrait_path, verbose=True)

    # Save output
    print(f"\n💾 Saving assembled sheet...")
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)

    with open(args.output, 'wb') as f:
        writer.write(f)

    print(f"  Saved to: {args.output}")
    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)
    print(f"\nAssembled {len(args.pages)} pages")
    print("View in Brave browser for best results")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
