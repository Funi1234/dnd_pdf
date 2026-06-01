#!/usr/bin/env python3
"""
Extract field definitions from all class template PDFs
Creates canonical field definition files for each class
"""

import json
import os
from pypdf import PdfReader
from collections import defaultdict

# Project paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'data', 'source_pdfs')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'class_fields')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

CLASSES = [
    "Artificer", "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
    "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
]


def categorize_field(field_name):
    """Categorize a field based on its name"""
    name_lower = field_name.lower()

    # Character info
    if any(x in name_lower for x in ['character name', 'player name', 'race', 'background', 'alignment', 'experience', 'level', 'class']):
        return 'character_info'

    # Abilities
    if any(x in name_lower for x in ['str', 'dex', 'con', 'int', 'wis', 'cha', 'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']):
        if 'save' in name_lower or 'saving' in name_lower:
            return 'saving_throws'
        return 'abilities'

    # Skills
    if any(x in name_lower for x in ['acrobat', 'animal', 'arcana', 'athletic', 'deception', 'history', 'insight', 'intimidat', 'investigat', 'medicine', 'nature', 'perception', 'perform', 'persuasion', 'religion', 'sleight', 'stealth', 'survival']):
        return 'skills'

    # Combat
    if any(x in name_lower for x in [' ac', 'armor class', 'initiative', 'speed', 'hp', 'hit points', 'hit dice', 'death save', 'attack', 'damage']):
        return 'combat'

    # Spells
    if any(x in name_lower for x in ['spell', 'cantrip', 'spellcasting']):
        return 'spells'

    # Equipment
    if any(x in name_lower for x in ['equipment', 'weapon', 'armor', 'gear', 'treasure', 'cp', 'sp', 'ep', 'gp', 'pp']):
        return 'equipment'

    # Features & Traits
    if any(x in name_lower for x in ['feature', 'trait', 'proficien', 'language']):
        return 'features'

    # Personality
    if any(x in name_lower for x in ['personality', 'ideal', 'bond', 'flaw', 'appearance', 'backstory', 'allies', 'organizations']):
        return 'personality'

    return 'other'


def extract_class_fields(class_name):
    """Extract field definitions from a class template PDF"""

    pdf_path = os.path.join(TEMPLATES_DIR, f"{class_name}_EU A4.pdf")

    if not os.path.exists(pdf_path):
        print(f"  ❌ PDF not found: {pdf_path}")
        return None

    reader = PdfReader(pdf_path)

    # Get fields from AcroForm
    acro_fields = reader.get_fields()
    if not acro_fields:
        print(f"  ⚠️  No AcroForm fields found")
        return None

    # Build field data with page association
    field_data = {}
    for field_name, field_obj in acro_fields.items():
        field_data[field_name] = {
            'type': str(field_obj.get('/FT', 'Unknown')),
            'default_value': str(field_obj.get('/V', '')),
            'category': categorize_field(field_name),
            'page': None  # Will be filled in below
        }

    # Map fields to pages via annotations
    for page_num, page in enumerate(reader.pages, 1):
        if '/Annots' not in page:
            continue

        annotations = page['/Annots']

        for annot_ref in annotations:
            try:
                annot = annot_ref.get_object()
                if '/T' in annot:
                    field_name = str(annot['/T'])
                    if field_name in field_data:
                        field_data[field_name]['page'] = page_num
            except:
                pass

    # Organize by page
    pages = {}
    for page_num in range(1, len(reader.pages) + 1):
        # Get fields on this page
        page_fields = {
            name: data for name, data in field_data.items()
            if data['page'] == page_num
        }

        if not page_fields:
            continue

        # Group by category
        categories = defaultdict(list)
        for field_name, field_info in page_fields.items():
            category = field_info['category']
            categories[category].append({
                'name': field_name,
                'type': field_info['type'],
                'default_value': field_info['default_value']
            })

        pages[f'page_{page_num}'] = {
            'page_number': page_num,
            'field_count': len(page_fields),
            'categories': {
                cat: {
                    'count': len(fields),
                    'fields': fields
                }
                for cat, fields in sorted(categories.items())
            }
        }

    # Build output structure
    output = {
        'metadata': {
            'class_name': class_name,
            'template_name': f'{class_name} EU A4',
            'source_pdf': f'{class_name}_EU A4.pdf',
            'total_fields': len(acro_fields),
            'total_pages': len(reader.pages),
            'pages_with_fields': len(pages),
            'extraction_note': 'Fields organized by page and category'
        },
        'pages': pages
    }

    return output


def main():
    print("=" * 80)
    print("EXTRACTING FIELD DEFINITIONS FROM ALL CLASS TEMPLATES")
    print("=" * 80)

    results = []

    for class_name in CLASSES:
        print(f"\n📄 {class_name}...")

        field_data = extract_class_fields(class_name)

        if field_data:
            # Save to file
            output_file = os.path.join(OUTPUT_DIR, f'{class_name.lower()}_fields.json')
            with open(output_file, 'w') as f:
                json.dump(field_data, f, indent=2)

            field_count = field_data['metadata']['total_fields']
            page_count = field_data['metadata']['total_pages']

            print(f"  ✅ {field_count:4} fields, {page_count:2} pages")
            print(f"  💾 Saved to: {os.path.basename(output_file)}")

            results.append({
                'class': class_name,
                'fields': field_count,
                'pages': page_count,
                'file': output_file
            })

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total_fields = sum(r['fields'] for r in results)
    print(f"\n  Classes extracted: {len(results)}")
    print(f"  Total fields: {total_fields:,}")
    print(f"  Average fields: {total_fields / len(results):.0f}")

    print(f"\n  📂 Output directory: {OUTPUT_DIR}")
    print(f"\n  Field count by class:")
    for r in sorted(results, key=lambda x: x['fields']):
        print(f"    {r['class']:12} - {r['fields']:4} fields ({r['pages']:2} pages)")

    print("\n" + "=" * 80)
    print("✅ All class field definitions extracted!")
    print("=" * 80)


if __name__ == '__main__':
    main()
