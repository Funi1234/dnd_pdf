#!/usr/bin/env python3
"""
Generic character sheet generator
Converts character data JSON to filled class-specific PDF
"""

import json
import os
import sys
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pypdf import PdfReader, PdfWriter
from src.pdf_utils import modify_field_font_size
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
    """
    Extract proficient saving throws from character data
    
    Looks for {ability}_proficient markers in saving_throws
    
    Returns:
        list: Proficient ability names (e.g., ['constitution', 'intelligence'])
    """
    proficient = []
    
    if 'saving_throws' in char_data:
        for key, value in char_data['saving_throws'].items():
            if key.endswith('_proficient') and value:
                ability = key.replace('_proficient', '')
                proficient.append(ability)
    
    return proficient


def interactive_weapon_selection(weapons):
    """
    Interactively select up to 3 weapons
    
    Args:
        weapons: List of weapon dicts
    
    Returns:
        list: Selected weapon names
    """
    if len(weapons) <= 3:
        # Auto-select all if 3 or fewer
        return [w['name'] for w in weapons]
    
    print("\n" + "=" * 80)
    print("WEAPON SELECTION (max 3)")
    print("=" * 80)
    print(f"\nYou have {len(weapons)} weapons available:")
    for i, wpn in enumerate(weapons, 1):
        print(f"  {i}. {wpn['name']}: {wpn['attack_bonus']} to hit, {wpn['damage']}")
    
    print("\nEnter weapon numbers to include (e.g., '1 3 4' or '2,3,5'):")
    print("Press Enter to use first 3")
    
    selection = input("> ").strip()
    
    if not selection:
        # Default to first 3
        return [w['name'] for w in weapons[:3]]
    
    # Parse selection
    try:
        # Handle both space and comma separated
        indices = [int(x.strip()) for x in selection.replace(',', ' ').split()]
        selected = []
        for idx in indices[:3]:  # Max 3
            if 1 <= idx <= len(weapons):
                selected.append(weapons[idx - 1]['name'])
        
        if selected:
            print(f"\nSelected: {', '.join(selected)}")
            return selected
        else:
            print("\nInvalid selection, using first 3")
            return [w['name'] for w in weapons[:3]]
    except ValueError:
        print("\nInvalid input, using first 3")
        return [w['name'] for w in weapons[:3]]


def create_field_mappings(char_data, layout='combined', background_page='regular', interactive=False):
    """
    Build field mapping dictionary using modular mappers

    Args:
        char_data: Character data dictionary
        layout: 'combined' for page 1, 'separate' for page 2
        background_page: 'regular' for standard background page, 'sidekick' for sidekick page
        interactive: If True, prompt for weapon selection

    Returns:
        dict: Field name -> value mappings
    """

    fields = {}

    # Extract level for calculations
    class_level = char_data['character_info']['class_and_level']
    level = int(class_level.rsplit(' ', 1)[1]) if ' ' in class_level else 5

    # Extract proficient saves from data
    proficient_abilities = extract_proficient_saves(char_data)

    # Handle weapon selection
    selected_weapons = char_data.get('selected_weapons')
    
    if interactive and 'weapons' in char_data and len(char_data['weapons']) > 3:
        # Interactive mode: ask user
        selected_weapons = interactive_weapon_selection(char_data['weapons'])
    elif not selected_weapons and 'weapons' in char_data:
        # No selection specified: use first 3
        selected_weapons = [w['name'] for w in char_data['weapons'][:3]]
    
    # Filter weapons if selection is available
    if selected_weapons and 'weapons' in char_data:
        char_data = filter_weapons(char_data, selected_weapons)

    # Apply core fields first (layout-independent: spell DC/Attack, spell slots, cantrips)
    map_core_fields(char_data, fields)

    # Apply layout-specific mappers
    map_character_info(char_data, fields, layout=layout)
    map_abilities(char_data, fields, layout=layout)
    map_skills(char_data, fields, layout=layout)
    map_saving_throws(char_data, fields, layout=layout, proficient_abilities=proficient_abilities)
    map_combat(char_data, fields, layout=layout, level=level)
    map_proficiencies(char_data, fields, layout=layout)
    map_weapons(char_data, fields, layout=layout)
    map_background(char_data, fields, background_page=background_page)
    map_spells(char_data, fields, layout=layout)

    return fields


def filter_weapons(char_data, selected_weapon_names):
    """
    Filter character weapons to only include selected ones

    Args:
        char_data: Character data dictionary
        selected_weapon_names: List of weapon names to keep

    Returns:
        Modified char_data with filtered weapons
    """
    import copy
    char_data = copy.deepcopy(char_data)

    all_weapons = char_data['weapons']

    # Build selected weapons list in the order specified
    selected = []
    for name in selected_weapon_names:
        # Find weapon by name (case-insensitive)
        for weapon in all_weapons:
            if weapon['name'].lower() == name.lower():
                selected.append(weapon)
                break

    char_data['weapons'] = selected[:3]  # Max 3

    return char_data


def set_field_fonts(writer, layout='combined'):
    """
    Set font sizes for fields that need adjustment

    Args:
        writer: PdfWriter object
        layout: 'combined' or 'separate'
    """

    suffix = '' if layout == 'combined' else '-Alt'

    # Skills
    skill_names = [
        'Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 'Deception',
        'History', 'Insight', 'Intimidation', 'Investigation', 'Medicine',
        'Nature', 'Perception', 'Performance', 'Persuasion', 'Religion',
        'Sleight of Hand', 'Stealth', 'Survival'
    ]

    font_adjusted = 0
    for skill_name in skill_names:
        if modify_field_font_size(writer, f'Front_Skill {skill_name}{suffix}', font_size=8, allow_overflow=True):
            font_adjusted += 1

    # Saving throws
    saving_throw_abilities = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
    for ability in saving_throw_abilities:
        if modify_field_font_size(writer, f'Front_{ability} Save Throw{suffix}', font_size=8, allow_overflow=True):
            font_adjusted += 1

    return font_adjusted


def main():
    parser = argparse.ArgumentParser(
        description='Generate D&D character sheet PDF from character data JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with Artificer
  python dnd_pdf.py \\
    --data data/character_data_clean.json \\
    --template data/source_pdfs/Artificer_EU A4.pdf \\
    --output output/Character_Sheet.pdf

  # Interactive weapon selection
  python dnd_pdf.py \\
    --data data/character_data_clean.json \\
    --template data/source_pdfs/Artificer_EU A4.pdf \\
    --output output/Character_Sheet.pdf \\
    --interactive
        """
    )

    parser.add_argument('--data', '-d', required=True,
                        help='Path to character data JSON file')
    parser.add_argument('--template', '-t', required=True,
                        help='Path to class-specific PDF template')
    parser.add_argument('--output', '-o', required=True,
                        help='Path for output PDF file')
    parser.add_argument('--layout', '-l', choices=['combined', 'separate'], default='separate',
                        help='Layout type: combined (page 1) or separate (page 2). Default: separate')
    parser.add_argument('--background-page', '-b', choices=['regular', 'sidekick'], default='regular',
                        help='Background page type: regular or sidekick. Default: regular')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Interactive mode: prompt for weapon selection if more than 3 available')

    args = parser.parse_args()

    print("=" * 80)
    print("D&D CHARACTER SHEET GENERATOR")
    print("=" * 80)

    # Load character data
    print(f"\n📖 Loading character data: {args.data}")
    char_data = load_character_data(args.data)
    print(f"  Character: {char_data['character_info']['name']}")
    print(f"  Class: {char_data['character_info']['class_and_level']}")

    # Configuration summary
    print(f"\n⚙️  Configuration:")
    print(f"  Layout: {args.layout}")
    if args.interactive:
        print(f"  Mode: Interactive")

    # Create field mappings
    print("\n🗺️  Creating field mappings...")
    field_values = create_field_mappings(char_data, layout=args.layout, background_page=args.background_page, interactive=args.interactive)
    print(f"  Mapped {len(field_values)} fields")

    # Load template
    print(f"\n📄 Loading template: {args.template}")
    reader = PdfReader(args.template)
    writer = PdfWriter()

    # Clone reader to writer (this copies the AcroForm)
    writer.append(reader)

    # Set font sizes BEFORE filling
    print("\n🔧 Pre-setting font sizes...")
    font_adjusted = set_field_fonts(writer, layout=args.layout)
    print(f"  Adjusted font for {font_adjusted} fields")

    # Fill fields
    print("\n✍️  Filling fields...")
    filled_count = 0
    missing_count = 0
    errors = []

    for field_name, value in field_values.items():
        try:
            writer.update_page_form_field_values(
                None,  # Apply to all pages
                {field_name: str(value)}
            )
            filled_count += 1
        except Exception as e:
            missing_count += 1
            errors.append(f"{field_name}: {str(e)}")

    print(f"  ✅ Filled: {filled_count} fields")
    print(f"  ⚠️  Missing: {missing_count} fields")

    if errors and missing_count < 10:
        print("\n  Errors:")
        for error in errors[:10]:
            print(f"    {error}")

    # Insert portrait if available
    portrait_path = char_data['character_info'].get('portrait_image')
    if portrait_path:
        print("\n🖼️  Embedding character portrait...")
        # Try to find background page (usually page with portrait field)
        # We'll check all pages for an image field
        portrait_added = False
        for page_num in range(len(writer.pages)):
            if embed_image_in_page(writer, page_num, portrait_path, verbose=True):
                portrait_added = True
                break

        if not portrait_added:
            print("  ⚠️  No image field found in template")

    # Save output
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)

    with open(args.output, 'wb') as f:
        writer.write(f)

    print(f"\n💾 Saved to: {args.output}")
    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)
    print(f"\nGenerated {args.layout} layout with {filled_count} fields filled")
    print("View in Brave browser for best results")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
