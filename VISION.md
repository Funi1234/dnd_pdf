# Project Vision - D&D Beyond to Class-Specific Sheet Converter

## Ultimate Goal

**Convert D&D Beyond-generated character sheets into class-specific fillable PDFs**

D&D Beyond provides generic character sheets that work for all classes. However, class-specific sheets (like the Artificer template) have specialized layouts, spell tracking, and class features that are much more useful at the table.

This tool automates the conversion process.

## System Overview

```
┌─────────────────────┐
│  D&D Beyond PDF     │
│  (Generic Sheet)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│  1. FIELD EXTRACTOR             │
│  Extract all fields → JSON      │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  2. FIELD MAPPER                │
│  Apply class-specific mapping   │
│  DNDBeyond → Artificer          │
│  DNDBeyond → Wizard             │
│  DNDBeyond → etc.               │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  3. CONVERTER                   │
│  Generate filled class PDF      │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Artificer PDF      │
│  (Fully Filled)     │
└─────────────────────┘
```

## Three-Phase Implementation

### Phase 1: Field Extraction ⏳ NEXT
**Goal**: Export any PDF's fillable fields to structured JSON/YAML

**Input**: 
- Neez-1.pdf (D&D Beyond character sheet - flattened)
- OR any fillable PDF

**Output**: 
```json
{
  "Character Name": "Ebenezer 'Neez' Tivonhoop",
  "Race": "Gnome",
  "Class & Level": "Artificer 5",
  "STR": "8",
  "STR Modifier": "-1",
  ...
}
```

**Challenges**:
- D&D Beyond PDFs are **flattened** (no form fields)
- Need OCR or visual parsing to extract data
- Alternative: Use D&D Beyond API or manual JSON export

**Tools to build**:
- `scripts/extract_dnd_beyond.py` - Parse flattened D&D Beyond PDF
- `scripts/export_pdf_fields.py` - Extract fields from any fillable PDF
- Structured output format (JSON/YAML)

### Phase 2: Field Mapping ⏳
**Goal**: Create reusable mappings between D&D Beyond and class templates

**Structure**:
```yaml
# mappings/artificer.yaml
character:
  source: "Character Name"
  target: "Front_Character Name"
  
ability_scores:
  strength:
    score:
      source: "STR"
      target: "Front_Str Score"
    modifier:
      source: "STR Modifier"
      target: "Front_Str Mod"
      
spells:
  cantrips:
    source: "Cantrips[]"
    target: "SpellSheet1_Spell Name {n:02d}-Alt"
    fields:
      name: "name"
      level: "level"
      school: "school"
      # ... etc
```

**Features**:
- **One-to-one mapping**: Simple field copy
- **Transform mapping**: Apply function (e.g., "+2" → "2")
- **Array mapping**: Spells, equipment lists
- **Conditional mapping**: Only if class matches
- **Default values**: Fill if source missing

**Tools to build**:
- `mappings/artificer.yaml` - Artificer-specific mapping
- `mappings/wizard.yaml` - Wizard-specific mapping (future)
- `src/mapper.py` - Mapping engine

### Phase 3: Converter ⏳
**Goal**: Automated conversion using mappings

**Usage**:
```bash
python3 scripts/convert_character.py \
  --input neez_dndbeyond.json \
  --template artificer \
  --output neez_artificer_filled.pdf
```

**Process**:
1. Load D&D Beyond data (JSON)
2. Load class template PDF
3. Load mapping for character's class
4. Apply mappings to fill PDF
5. Generate output PDF

**Tools to build**:
- `scripts/convert_character.py` - Main conversion script
- `src/converter.py` - Conversion engine
- Template system for extensibility

## Current Progress

### ✅ Completed (Context for Artificer)
1. **Artificer template understood**
   - All 865 fields documented
   - Field naming quirks identified
   - Spell sheet structure mapped

2. **Spell system working**
   - Markdown extraction (59/59 spells)
   - Proper formatting (8pt font, multiline)
   - Component handling
   - Duration cleanup

3. **PDF manipulation utilities**
   - Form field filling
   - PDF merging with field preservation
   - Font size modification

4. **Proof of concept**
   - Successfully filled Neez's Artificer sheet
   - All spells with descriptions
   - Spell counts correct

### ⏳ Next Steps (In Order)

**Step 1**: Extract D&D Beyond data
- Parse Neez-1.pdf (flattened D&D Beyond sheet)
- Create structured JSON of ALL character data
- This becomes our "source of truth"

**Step 2**: Create Artificer mapping
- Map D&D Beyond fields → Artificer fields
- Document transformation rules
- Test with Neez's data

**Step 3**: Build converter
- Implement mapping engine
- Create conversion script
- Test end-to-end conversion

**Step 4**: Generalize for other classes
- Create wizard mapping
- Create cleric mapping
- Make system extensible

## File Structure (Updated)

```
~/coding/dnd_pdf/
├── mappings/                        # Class-specific field mappings
│   ├── artificer.yaml              # D&D Beyond → Artificer
│   ├── wizard.yaml                 # D&D Beyond → Wizard (future)
│   └── _base.yaml                  # Common fields all classes share
├── templates/                       # Class-specific PDF templates
│   ├── artificer/
│   │   ├── template.pdf
│   │   └── spell_sheet.pdf
│   ├── wizard/
│   └── cleric/
├── data/
│   ├── source_characters/           # D&D Beyond exports (JSON/PDF)
│   │   ├── neez_dndbeyond.json     # Extracted from Neez-1.pdf
│   │   └── neez_dndbeyond.pdf      # Original D&D Beyond sheet
│   └── spell_library/               # Shared spell descriptions
│       └── markdown/                # Spell markdown files
├── src/
│   ├── extractors/                  # Data extraction from various sources
│   │   ├── pdf_extractor.py        # Generic PDF field extraction
│   │   ├── dndbeyond_parser.py     # D&D Beyond specific parsing
│   │   └── ocr_extractor.py        # OCR for flattened PDFs
│   ├── mapper.py                    # Mapping engine
│   ├── converter.py                 # Conversion orchestration
│   ├── pdf_utils.py                 # PDF manipulation
│   └── spell_extractor.py           # Spell description extraction
├── scripts/
│   ├── extract_dnd_beyond.py       # Extract data from D&D Beyond PDF
│   ├── create_mapping.py           # Interactive mapping creation
│   ├── convert_character.py        # Main conversion script
│   ├── generate_character_sheet.py # Old proof-of-concept (keep for reference)
│   └── inspect_pdf_fields.py       # Field inspection utility
└── output/
    ├── mappings/                    # Generated mapping analysis
    ├── characters/                  # Generated character sheets
    └── debug/                       # Debug output
```

## Example Workflow

### For Neez (Manual → Automated)

**Current (Manual)**:
1. Manually extract character data from Neez-1.pdf → JSON
2. Manually convert spell format
3. Run generation script
4. Get filled Artificer PDF

**Target (Automated)**:
1. Run: `extract_dnd_beyond.py neez_dndbeyond.pdf`
   - Output: `neez_extracted.json`
2. Run: `convert_character.py --input neez_extracted.json --template artificer`
   - Output: `neez_artificer_complete.pdf`

### For Any Character (Future)

```bash
# One command!
dnd-convert wizard_from_dndbeyond.pdf --class wizard --output wizard_complete.pdf
```

## Key Design Principles

1. **Separation of Concerns**
   - Extraction: Get data from source
   - Mapping: Define transformations
   - Conversion: Apply transformations

2. **Extensibility**
   - New classes = new mapping file
   - No code changes needed
   - Community can contribute mappings

3. **Transparency**
   - Mappings are human-readable YAML
   - Debug mode shows every transformation
   - Easy to fix mapping errors

4. **Reusability**
   - Spell library shared across all characters
   - Base mappings shared across classes
   - PDF utilities work for any PDF

## Success Criteria

- [ ] Can extract D&D Beyond character data automatically
- [ ] Can map any field from D&D Beyond to Artificer
- [ ] Can generate complete Artificer PDF from D&D Beyond data
- [ ] Can add new class templates with just a mapping file
- [ ] Can convert any character in under 30 seconds
- [ ] Generated PDFs are 100% accurate

## Current Blocker

**Neez-1.pdf is flattened (no form fields)**

Options:
1. Find fillable D&D Beyond PDF
2. Use D&D Beyond API/export
3. Manually create neez_dndbeyond.json
4. Build OCR parser for flattened PDFs

**Recommendation**: Start with option 3 (manual JSON) to build and test the mapping system, then tackle extraction later.
