# Data Directory

This directory contains all source data and extracted field definitions.

## Files

### Source PDFs
- **`source_pdfs/Neez-Artificer_EU A4.pdf`** (13 MB)
  - Original fillable Artificer character sheet template
  - 8 pages, 865 form fields
  - EU A4 paper size

- **`source_pdfs/Spell Sheet-2_EU A4.pdf`** (2.9 MB)
  - Additional spell sheet for overflow spells
  - 1 page, 225 form fields (15 spell slots)

### Character Data
- **`character_data/neez_character_data.json`** (1.5 KB)
  - Basic character info for Neez
  - Partial data (was manually created early in project)

- **`character_data/neez_spells_converted.json`** (36 KB)
  - All 59 spells in Artificer template format
  - No descriptions yet

- **`character_data/neez_spells_with_descriptions.json`** (61 KB) ✨
  - All 59 spells WITH descriptions from markdown
  - Ready for PDF filling

### Field Definition Files (Canonical) ⭐

#### `artificer_field_definitions.json` ⭐ **TARGET TEMPLATE**
**Size**: 104 KB  
**Format**: Clean structured JSON with metadata
```json
{
  "metadata": {
    "template_name": "Artificer EU A4",
    "source_pdf": "Neez-Artificer_EU A4.pdf",
    "total_fields": 865,
    "total_pages": 8
  },
  "fields": {
    "Front_Character Name": {
      "type": "/Tx",
      "default_value": ""
    }
  },
  "fields_by_page": {
    "page_1": ["Front_Character Name", "Front_AC", ...],
    "page_2": [...],
    ...
  }
}
```
**Use**: **CANONICAL** reference for Artificer template field definitions

#### `dndbeyond_field_definitions.json` ⭐ **SOURCE TEMPLATE**
**Size**: 172 KB  
**Format**: Clean structured JSON with metadata
```json
{
  "metadata": {
    "template_name": "D&D Beyond Character Sheet",
    "source_pdf": "Neez-1.pdf",
    "total_fields": 1374,
    "total_pages": 8
  },
  "fields": {
    "CharacterName": {
      "type": "/Tx",
      "default_value": "Ebenezer 'Neez' Tivonhoop",
      "page": 1
    }
  },
  "fields_by_page": {
    "page_1": ["CharacterName", "CLASS  LEVEL", "STR", ...],
    ...
  }
}
```
**Use**: **CANONICAL** reference for D&D Beyond source field definitions

#### Legacy Files (Deprecated)

- `pdf_field_definitions.json` (69 KB) - DEPRECATED, use `artificer_field_definitions.json`
- `artificer_fields_structured.json` (154 KB) - DEPRECATED, use `artificer_field_definitions.json`
- `artificer_fields_by_page.json` (125 KB) - DEPRECATED, use `artificer_field_definitions.json`
- `Neez-1_extracted.json` (131 KB) - DEPRECATED, use `dndbeyond_field_definitions.json`

#### `artificer_page_guide.md` ✨ START HERE
**Format**: Human-readable markdown documentation

**Content**:
- What's on each page
- Field counts by category
- Quick reference table
- Field naming patterns explained
- Tips for finding specific fields

**Use**: Understanding the template structure

---

## Field Extraction Summary

### ✅ Artificer Template - COMPLETE
- All 865 fields extracted
- Canonical file: `artificer_field_definitions.json`
- Human-readable guide: `artificer_page_guide.md`
- Clean structured format with metadata
- Ready for mapping

### ✅ D&D Beyond Template - COMPLETE
- All 1,374 fields extracted
- Canonical file: `dndbeyond_field_definitions.json`
- Includes Neez character data as default values
- Clean structured format with metadata
- Ready for mapping

### ⏳ Next: Create Field Mappings
- Define D&D Beyond → Artificer transformations
- Create `mappings/artificer.yaml`
- Handle layout preferences
- Document transformation rules

---

## Page Breakdown (Quick Reference)

| Page | Content | Fields | Status |
|------|---------|--------|--------|
| 1 | Character sheet (left) | 147 | ✅ Extracted |
| 2 | Character sheet (right, duplicate) | 147 | ✅ Extracted |
| 3 | Personality, appearance | 57 | ✅ Extracted |
| 4 | Features, backstory, treasure | 81 | ✅ Extracted |
| 5 | Additional features | 0 | N/A |
| 6 | Equipment notes | 0 | N/A |
| 7 | Spell metadata & slots | 208 | ✅ Extracted |
| 8 | Spell entries (15 slots) | 225 | ✅ Extracted |

**Total**: 865 fields across 6 pages with fields

---

## How to Use

### To understand the Artificer template:
1. Start with `artificer_page_guide.md`
2. Look up specific fields in `artificer_fields_by_page.json`
3. Use `scripts/inspect_pdf_fields.py` for interactive exploration

### To create character data:
1. Read character sheet (Neez-1.pdf or D&D Beyond export)
2. Create JSON in standardized format (see schema - TODO)
3. Save to `source_characters/`

### To build mappings:
1. Compare D&D Beyond field names (source)
2. With Artificer field names (from extracted files)
3. Create mapping file in `mappings/`

---

## Tools to Extract/Inspect

Located in `scripts/`:
- `inspect_pdf_fields.py` - Interactive field inspection
- `analyze_template_fields.py` - Categorized analysis
- `extract_fields_by_page.py` - Page-by-page extraction ✨

**Example usage**:
```bash
# Inspect all fields
python3 scripts/inspect_pdf_fields.py --base

# Filter by category
python3 scripts/inspect_pdf_fields.py --base --filter "Spell"

# Show current values
python3 scripts/inspect_pdf_fields.py --base --values

# Export to JSON
python3 scripts/inspect_pdf_fields.py --base --export fields.json
```

---

## Next Steps

1. ✅ Extract Artificer fields - DONE
2. ⏳ Create character data schema
3. ⏳ Manually extract Neez's D&D Beyond data
4. ⏳ Build D&D Beyond → Artificer mapping
5. ⏳ Create conversion engine
