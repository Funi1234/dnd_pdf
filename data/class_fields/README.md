# Class Field Definitions

Canonical field definitions for all D&D 5e class templates.

## Overview

Each file contains the complete field structure for one class template:
- Field names and types
- Default values
- Page organization
- Metadata

## Files

| Class | Fields | Pages | File |
|-------|--------|-------|------|
| Monk | 865 | 6 | `monk_fields.json` |
| Barbarian | 879 | 6 | `barbarian_fields.json` |
| Artificer | 1,334 | 8 | `artificer_fields.json` |
| Paladin | 1,501 | 8 | `paladin_fields.json` |
| Cleric | 1,572 | 8 | `cleric_fields.json` |
| Bard | 1,600 | 8 | `bard_fields.json` |
| Warlock | 1,644 | 9 | `warlock_fields.json` |
| Sorcerer | 1,670 | 9 | `sorcerer_fields.json` |
| Rogue | 1,742 | 10 | `rogue_fields.json` |
| Wizard | 1,756 | 9 | `wizard_fields.json` |
| Druid | 1,824 | 9 | `druid_fields.json` |
| Ranger | 1,922 | 11 | `ranger_fields.json` |
| Fighter | 2,034 | 12 | `fighter_fields.json` |

**Total**: 20,343 fields across 13 classes

## File Structure

Each JSON file follows this page-organized format:

```json
{
  "metadata": {
    "class_name": "Monk",
    "template_name": "Monk EU A4",
    "source_pdf": "Monk_EU A4.pdf",
    "total_fields": 865,
    "total_pages": 6,
    "pages_with_fields": 4,
    "extraction_note": "Fields organized by page and category"
  },
  "pages": {
    "page_1": {
      "page_number": 1,
      "field_count": 130,
      "categories": {
        "abilities": {
          "count": 15,
          "fields": [
            {
              "name": "Front_Str Score",
              "type": "/Tx",
              "default_value": ""
            },
            {
              "name": "Front_Dex Score",
              "type": "/Tx",
              "default_value": ""
            }
          ]
        },
        "combat": {
          "count": 10,
          "fields": [...]
        },
        "skills": {
          "count": 53,
          "fields": [...]
        }
      }
    },
    "page_2": {...}
  }
}
```

**Categories**:
- `abilities` - Ability scores and modifiers
- `saving_throws` - Saving throw bonuses
- `skills` - Skill proficiencies and bonuses
- `combat` - AC, HP, initiative, attacks
- `spells` - Spell slots, DC, attack bonus, known spells
- `equipment` - Weapons, armor, gear, currency
- `features` - Class features, racial traits, proficiencies
- `character_info` - Name, class, level, race, background
- `personality` - Personality traits, ideals, bonds, flaws
- `other` - Uncategorized fields

## Field Types

- `/Tx` - Text field
- `/Btn` - Button/checkbox field
- `/Ch` - Choice field (dropdown)

## Observations

### Page Count Patterns

**Non-spellcasters** (fewer pages):
- Barbarian: 6 pages
- Monk: 6 pages

**Half-casters** (medium pages):
- Artificer: 8 pages
- Paladin: 8 pages
- Ranger: 11 pages (more spell slots)

**Full-casters** (more pages):
- Bard: 8 pages
- Cleric: 8 pages
- Druid: 9 pages
- Sorcerer: 9 pages
- Warlock: 9 pages
- Wizard: 9 pages

**Martial with subclasses**:
- Fighter: 12 pages (most pages - many subclass variants)
- Rogue: 10 pages

### Field Count Patterns

More spell slots = more fields:
- Monk (no spells): 865 fields
- Barbarian (no spells): 879 fields
- Artificer (half-caster): 1,334 fields
- Full casters: 1,500-1,800 fields
- Fighter (many subclass options): 2,034 fields

## Usage

### Load field definitions

```python
import json

# Load Monk fields
with open('data/class_fields/monk_fields.json') as f:
    monk = json.load(f)

# Get total field count
field_count = monk['metadata']['total_fields']

# Get page 1 data
page_1 = monk['pages']['page_1']
print(f"Page 1 has {page_1['field_count']} fields")

# Get abilities on page 1
abilities = page_1['categories']['abilities']['fields']
for field in abilities:
    print(f"{field['name']}: {field['type']}")
```

### Find specific fields

```python
# Find all AC-related fields across all pages
ac_fields = []
for page_key, page_data in monk['pages'].items():
    for category, cat_data in page_data['categories'].items():
        for field in cat_data['fields']:
            if 'AC' in field['name'].upper():
                ac_fields.append({
                    'page': page_data['page_number'],
                    'name': field['name'],
                    'category': category
                })

# Get all spell fields
spell_fields = []
for page_key, page_data in monk['pages'].items():
    if 'spells' in page_data['categories']:
        spell_fields.extend(page_data['categories']['spells']['fields'])
```

## Extraction Process

Fields extracted using:
```bash
python scripts/extract_all_class_fields.py
```

This script:
1. Reads each class PDF from `data/source_pdfs/`
2. Extracts fields using pypdf's `get_fields()`
3. Maps fields to pages via annotations
4. Saves to structured JSON format

## Next Steps

These field definitions enable:
1. **Field mapping** - Map D&D Beyond → class-specific fields
2. **Validation** - Ensure all required fields are populated
3. **Multi-class support** - Understand differences between class templates
4. **Automated conversion** - Transform character data to any class sheet

## See Also

- `../dndbeyond_field_definitions.json` - Source template (D&D Beyond)
- `../../ARCHITECTURE.md` - System design
- `../../ROADMAP.md` - Development plan
