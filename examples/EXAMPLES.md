# Example Character Sheets

This directory contains working examples of the D&D PDF converter workflow.

## Directory Structure

```
examples/
├── EXAMPLES.md              # This file
├── input_sheets/            # D&D Beyond character sheets (input)
│   ├── Dwarf_Cleric_1.pdf
│   └── Human_Wizard_1.pdf
├── character_data/          # Extracted character data (JSON)
│   ├── dwarf_cleric_raw.json
│   ├── dwarf_cleric_clean.json
│   ├── human_wizard_raw.json
│   └── human_wizard_clean.json
└── output_sheets/           # Generated class-specific PDFs (output)
    ├── Dwarf_Cleric_1.pdf
    └── Human_Wizard_1.pdf
```

## Workflow

### Step 1: Extract Character Data from D&D Beyond PDF

Start with a D&D Beyond character sheet PDF and extract all field data:

```bash
python scripts/extract_dndbeyond_fields.py \
  "examples/input_sheets/Dwarf_Cleric_1.pdf" \
  --output examples/character_data/dwarf_cleric_raw.json
```

This creates a JSON file with all raw field data from the D&D Beyond PDF, organized by page.

**Example output structure:**
```json
{
  "metadata": {
    "source_pdf": "Dwarf_Cleric_1.pdf",
    "total_pages": 4,
    "total_fields": 775
  },
  "pages": {
    "page_1": {
      "page_number": 1,
      "field_count": 146,
      "fields": {
        "CharacterName": {"value": "Dwarf Cleric", "field_type": "/Tx"},
        "CLASS  LEVEL": {"value": "Cleric 1", "field_type": "/Tx"},
        ...
      }
    },
    ...
  }
}
```

### Step 2: Automatic Conversion to Clean Format

The extraction script **automatically converts** raw data to clean format:

**This happens automatically in Step 1!** The script creates both:
- `dwarf_cleric_raw.json` - All 775 fields from D&D Beyond
- `dwarf_cleric_clean.json` - Clean, standardized format for the generator

To skip auto-conversion and only extract raw data:
```bash
python scripts/extract_dndbeyond_fields.py \
  "examples/input_sheets/Dwarf_Cleric_1.pdf" \
  --output examples/character_data/dwarf_cleric_raw.json \
  --no-clean
```

**Clean data structure:**

```json
{
  "character": {
    "character_info": {
      "name": "Character Name",
      "class_and_level": "Warlock 1",
      "race": "Tiefling",
      "background": "Background Name",
      "alignment": "Chaotic Good"
    },
    "ability_scores": {
      "strength": {"score": "10", "modifier": "+0"},
      "dexterity": {"score": "14", "modifier": "+2"},
      ...
    },
    "skills": {
      "acrobatics": {"bonus": "+2", "proficiency": ""},
      "arcana": {"bonus": "+5", "proficiency": "P"},
      ...
    },
    "saving_throws": {
      "strength": "+0",
      "wisdom": "+3",
      "wisdom_proficient": "•",
      "charisma": "+5",
      "charisma_proficient": "•",
      ...
    },
    "combat": {
      "armor_class": "13",
      "initiative": "+2",
      "speed": "30",
      "max_hp": "9"
    },
    "proficiencies": "=== LANGUAGES ===\nCommon, Infernal\n\n=== ARMOR ===\nLight Armor\n\n=== WEAPONS ===\nSimple Weapons",
    "spellcasting": {
      "spell_save_dc": "13",
      "spell_attack_bonus": "+5"
    },
    "spells": [...],
    "weapons": [
      {"name": "Dagger", "attack_bonus": "+4", "damage": "1d4+2 Piercing"}
    ],
    "selected_weapons": ["Dagger", "Eldritch Blast"],
    "proficient_saves": ["wisdom", "charisma"]
  }
}
```

### Step 3: Generate Class-Specific PDF

Use the clean character data to generate a filled class-specific PDF:

```bash
python dnd_pdf.py \
  --data examples/character_data/dwarf_cleric_clean.json \
  --template data/source_pdfs/Cleric_EU\ A4.pdf \
  --output examples/output_sheets/Dwarf_Cleric_1.pdf \
  --layout separate
```

For interactive weapon selection (if character has >3 weapons):

```bash
python dnd_pdf.py \
  --data examples/character_data/dwarf_cleric_clean.json \
  --template data/source_pdfs/Cleric_EU\ A4.pdf \
  --output examples/output_sheets/Dwarf_Cleric_1.pdf \
  --layout separate \
  --interactive
```

## Complete Workflow Example

Here's the full end-to-end workflow for the Dwarf Cleric:

```bash
# Step 1: Extract from D&D Beyond PDF (creates both raw and clean JSONs)
python scripts/extract_dndbeyond_fields.py \
  "examples/input_sheets/Dwarf_Cleric_1.pdf" \
  --output examples/character_data/dwarf_cleric_raw.json

# Step 2: Generate class-specific PDF
python dnd_pdf.py \
  --data examples/character_data/dwarf_cleric_clean.json \
  --template data/source_pdfs/Cleric_EU\ A4.pdf \
  --output examples/output_sheets/Dwarf_Cleric_1.pdf \
  --layout separate
```

That's it! Two commands to go from D&D Beyond PDF to filled class-specific sheet.

## Example Characters

### Dwarf Cleric (Level 1) - "Dwarf Cleric"
- **D&D Beyond PDF:** `input_sheets/Dwarf_Cleric_1.pdf` (4 pages)
- **Extracted Data:** `character_data/dwarf_cleric_raw.json` (775 fields)
- **Clean Data:** `character_data/dwarf_cleric_clean.json` (auto-generated)
- **Class Template:** `data/source_pdfs/Cleric_EU A4.pdf`
- **Generated PDF:** `output_sheets/Dwarf_Cleric_1.pdf` ✅ **78 fields filled**

**Mapped fields:** Character info, abilities, skills, saves, combat stats, proficiencies, weapons, spell DC/attack, cantrips

### Human Wizard (Level 1) - "Presto"
- **D&D Beyond PDF:** `input_sheets/Human_Wizard_1.pdf` (5 pages)
- **Extracted Data:** `character_data/human_wizard_raw.json` (874 fields)
- **Clean Data:** `character_data/human_wizard_clean.json` (auto-generated)
- **Class Template:** `data/source_pdfs/Wizard_EU A4.pdf`
- **Generated PDF:** `output_sheets/Human_Wizard_1.pdf` ✅ **81 fields filled**

**Mapped fields:** Character info, abilities, skills (with proficiencies), saves, combat stats, proficiencies, weapons, spell DC/attack, cantrips

## Notes

- **Automatic conversion:** Raw → Clean conversion happens automatically
- **Output PDFs:** Gitignored (generated files, not source)
- **Layouts:** Use `--layout combined` (page 1) or `--layout separate` (page 2)
- **View PDFs:** Use Brave browser for best form field rendering
- **Known limitations:** Channel Divinity and class-specific resources not auto-filled (requires manual entry)
