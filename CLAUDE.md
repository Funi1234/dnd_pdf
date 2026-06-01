# D&D PDF Character Sheet Generator - Claude Context

## Project Goal

Automatically generate a complete, filled D&D 5e character sheet PDF for "Ebenezer 'Neez' Tivonhoop", a level 5 Gnome Artificer, including:

1. **All character data**: Name, ability scores, AC, HP, skills, proficiencies, equipment, features
2. **All 59 spells**: 7 cantrips + 52 leveled spells (24 × 1st level, 28 × 2nd level)
3. **Full spell descriptions**: Extracted from markdown files (Player's Handbook content owned by user)
4. **Proper formatting**: Readable font sizes, correct field names, component toggles, spell counts

## Project Structure

```
~/coding/dnd_pdf/
├── config/
│   └── paths.json                    # File path configuration
├── data/
│   ├── source_pdfs/                  # Original fillable PDF templates
│   │   ├── Neez-Artificer_EU A4.pdf # Base character sheet (13 MB, 8 pages)
│   │   └── Spell Sheet-2_EU A4.pdf  # Additional spell sheet (2.9 MB, 1 page)
│   └── character_data/               # Character & spell JSON data
│       ├── neez_character_data.json
│       ├── neez_spells_converted.json
│       └── neez_spells_with_descriptions.json
├── src/
│   ├── pdf_utils.py                  # PDF manipulation utilities
│   └── spell_extractor.py            # Markdown spell extraction
├── scripts/
│   └── generate_character_sheet.py   # Main generation script
├── output/
│   └── Neez-Artificer_COMPLETE.pdf  # Final generated PDF
└── venv/                             # Python virtual environment
```

## Source Data

### Spell Markdown Files
- **Location**: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/DnD/2. Mechanics/Spells/`
- **Format**: Markdown files with YAML frontmatter
- **Content**: Spell descriptions from Player's Handbook 2024
- **Special cases**:
  - "Homunculus Servant" → `Create Homunculus.md`
  - "Enlarge/Reduce" → `EnlargeReduce.md`

### Character Data
- **Source**: D&D Beyond character sheet (flattened PDF - no form fields)
- **Stats**: Level 5, AC 19, INT 20 (+5), Spell Save DC 17, Spell Attack +9

## Critical Gotchas & Solutions

### 0. D&D Beyond PDFs Are NOT Standardized! ⚠️

**Critical Discovery**: D&D Beyond character sheet exports are **NOT consistent** across characters.

**Why This Matters**:
- Different characters may have different field layouts
- Different export dates may use different templates
- Different D&D Beyond features (homebrew, sources) may add/remove fields
- Field names, structure, and organization can vary

**Impact on Architecture**:
- ❌ **DON'T**: Assume all D&D Beyond PDFs have identical field structures
- ✅ **DO**: Build flexible field mapping that can handle variations
- ✅ **DO**: Validate field presence before attempting conversion
- ✅ **DO**: Log missing fields as warnings, not errors
- ✅ **DO**: Use field name pattern matching (fuzzy matching) when possible

**Current Approach**:
- We've extracted Neez's D&D Beyond PDF structure (1,374 fields)
- This is **ONE EXAMPLE** of what D&D Beyond might export
- Future characters may have different structures
- Mapping system must be resilient to missing/extra fields

**Examples of Potential Variations**:
- Optional features enabled/disabled (feats, multiclass)
- Different source books (Xanathar's, Tasha's adds fields)
- Homebrew content (custom fields)
- Character level (higher levels = more spell slots)
- Template version changes over time

**Design Principles**:
1. **Graceful degradation** - Missing fields → skip, don't crash
2. **Field matching** - Try exact match first, then fuzzy/pattern match
3. **Validation reports** - Show what mapped, what didn't
4. **Manual overrides** - Allow user to specify field mappings
5. **Version tracking** - Note which D&D Beyond template version we support

**See Also**: ARCHITECTURE.md for mapping strategy details

---

### 1. Artificer Template Has TERRIBLE Field Names! 🤦

**Discovery**: Some Artificer template fields are named the **exact opposite** of what they actually represent.

**Examples of Backwards Naming**:

1. **Spell Attack vs Spell Save DC** (Page 1):
   - `Front_Cantrips Known` = Actually **Spell Attack Bonus** (+9)
   - `Front_Spells Known` = Actually **Spell Save DC** (17)
   - These are labeled correctly on the PDF but named backwards in the form fields!

2. **Saving Throws** (Page 1):
   - `Front_Save {Ability}` = Actually the **proficiency checkbox** (/Yes or /Off)
   - `Front_{Ability} Save Throw` = Actually the **value** (+8, -1, etc.)
   - Completely backwards from what you'd expect!

**Impact**: 
- Always verify field names by scanning the PDF, never assume based on labels
- Use test values (like "TESTATTACK") and scan the PDF to find exact field names
- Document these quirks in mapper code with comments

**Solution**: 
```python
# TERRIBLE NAMING: These are backwards!
fields['Front_Cantrips Known'] = spell_attack  # Not cantrips, it's attack bonus
fields['Front_Spells Known'] = spell_save_dc   # Not spells known, it's save DC

# ALSO BACKWARDS: Checkbox vs value swapped
fields['Front_Save Int'] = '/Yes'              # Checkbox, not value
fields['Front_Int Save Throw'] = '+8'          # Value, not checkbox
```

**See Also**: `src/field_mappers/combat.py` and `src/field_mappers/saving_throws.py`

---

### 2. Pages 1 & 2 Are Alternative Layouts (Not Duplicates!)

**Discovery**: The Artificer PDF has 147 fields on page 1 and 147 "duplicate" fields on page 2.

**Reality**: These aren't duplicates - they're **two different layout options** for the character sheet front page!
- **Page 1**: "Skills Combined" layout
- **Page 2**: "Skills Separate" layout (fields end with `-Alt`)

**Impact**: 
- User chooses which layout they prefer
- Fill EITHER page 1 OR page 2, NOT BOTH
- They represent the same data in different visual layouts

**Example**:
```python
# Page 1 (Skills Combined)
"Front_Character Name"

# Page 2 (Skills Separate) 
"Front_Character Name-Alt"
```

**Solution for Converter**:
- Let user choose layout preference in config
- Fill only the chosen page's fields
- Default to page 1 (no `-Alt` suffix)

### 1. PDF Form Field Naming Inconsistencies

**Problem**: The Artificer template has inconsistent field naming with spaces.

**Field Names**:
```python
"SpellSheet1_Spell Name 01-Alt"      # No space before "Spell"
"SpellSheet 1_Spells Level 01-Alt"   # SPACE before "1"!
"SpellSheet1_Range 01-Alt"           # No space
```

**Solution**: Use exact field names as discovered via `get_fields()`. Never assume patterns.

### 2. pypdf Method Names Changed

**Problem**: Old code used non-existent methods.

**WRONG**:
```python
writer.update_page_form_field_with_auto_resize()  # Does NOT exist!
```

**CORRECT**:
```python
writer.update_page_form_field_values(page, {field_name: value})
```

### 3. Merging PDFs Loses Form Fields

**Problem**: Using `add_page()` loses the central `/AcroForm` object.

**WRONG**:
```python
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)  # Loses form fields!
```

**CORRECT**:
```python
writer = PdfWriter()
writer.clone_document_from_reader(reader)  # Preserves /AcroForm
```

### 4. Page 7 Has No Cantrip Spell Fields

**Problem**: Original PDF page 7 only has spell slots/component pouch metadata fields, NOT individual spell entry fields.

**Solution**: 
- Page 7 = spell metadata (slots, DC, attack bonus, cantrips known)
- Page 8 = cantrip spell entries (15 slots using SpellSheet format)

### 5. Font Size in Spell Descriptions

**Problem**: Default font size cuts off spell descriptions.

**Attempted**: PDF auto-sizing (font size 0) - unreliable across viewers.

**Working Solution**: Set fixed 8pt font + multiline flag (4096):
```python
field_obj[NameObject("/DA")] = TextStringObject("/Helv 8 Tf 0 g")
field_obj[NameObject("/Ff")] = NumberObject(flags | 4096)  # Multiline
```

### 6. Component Field Confusion

**Problem**: Components field was showing "V,S,M (materials)" text.

**Correct Behavior**:
- V/S/M **checkboxes** indicate verbal/somatic/material
- Components **text field** only shows actual materials (e.g., "piece of copper wire")

### 7. Duration Field Redundancy

**Problem**: Duration showed "Concentration, up to 1 minute" while concentration checkbox exists.

**Solution**: Strip "Concentration, up to " prefix:
```python
def clean_duration(duration):
    if duration.startswith("Concentration, up to "):
        return duration.replace("Concentration, up to ", "")
    return duration
```

### 8. Checkbox Values

**Problem**: Wrong checkbox values don't toggle properly.

**WRONG**:
```python
field_value = True  # or 1
```

**CORRECT**:
```python
field_value = '/Yes'  # checked
field_value = '/Off'  # unchecked
```

### 9. Can't Pop from PDF Pages List

**Problem**: Trying to remove a page after cloning.

**WRONG**:
```python
writer.pages.pop(7)  # AttributeError: '_VirtualList' has no 'pop'
```

**Solution**: Build PDF by adding only desired pages, or work around with temp files.

### 10. Spell Counts Not Updating After Merge

**Problem**: Filling fields on merged PDF fails because `/AcroForm` is missing.

**Solution**: Fill base PDF BEFORE merging spell sheets:
```python
# Fill base PDF first
temp_base = PdfWriter()
temp_base.clone_document_from_reader(base_reader)
temp_base.update_page_form_field_values(temp_base.pages[0], spell_counts)

# Save and reload
with open(temp_base_path, 'wb') as f:
    temp_base.write(f)

# Then merge with spell sheets
final_writer = PdfWriter()
filled_base = PdfReader(temp_base_path)
for i in range(7):
    final_writer.add_page(filled_base.pages[i])
```

## PDF Field Reference

### Base PDF (Pages 1-7)
- `Front_Character Name`
- `Front_AC`
- `Front_Str Score`, `Front_Str Mod`
- (Similar for Dex, Con, Int, Wis, Cha)
- `Front_Cantrips Known` / `Front_Cantrips Known-Alt`
- `Front_Spells Known` / `Front_Spells Known-Alt`
- `Front_Spell Slot 1st 1`, `Front_Spell Slot 1st 2`, etc.

### Spell Sheet (Pages 8-12)
Per spell slot (01-Alt through 15-Alt):
- `SpellSheet1_Spell Name {slot}`
- `SpellSheet 1_Spells Level {slot}` ← Note the space!
- `SpellSheet1_Spell School {slot}`
- `SpellSheet1_Range {slot}`
- `SpellSheet1_Casting Time {slot}`
- `SpellSheet1_Save {slot}`
- `SpellSheet1_Duration {slot}`
- `SpellSheet1_Components {slot}` ← Material text only
- `SpellSheet1_Spell Effect {slot}` ← Full description
- Checkboxes (all `SpellSheet1_`):
  - `Verbal {slot}`, `Somatic {slot}`, `Material {slot}`
  - `Ritual {slot}`, `Concentration {slot}`, `Prepared {slot}`

## Current Status

✅ **Completed**:
1. Spell description extraction (59/59 spells from markdown)
2. Spell format conversion (D&D Beyond → Artificer template)
3. Spell sheet generation with 8pt multiline font
4. PDF merging with form field preservation
5. Cantrips on page 8
6. Leveled spells on pages 9-12
7. Spell counts filled (7 cantrips known, 52 spells known)

⏳ **TODO**:
1. Fill character data on pages 1-6:
   - Name, race, class, level
   - Ability scores and modifiers
   - AC, HP, speed, initiative
   - Skills and saves
   - Proficiencies
   - Equipment and features
   - Physical description
   - Personality traits

## Usage

```bash
cd ~/coding/dnd_pdf
source venv/bin/activate
python3 scripts/generate_character_sheet.py
```

Output: `output/Neez-Artificer_COMPLETE.pdf`

## Dependencies

- Python 3.8+
- pypdf library

## Notes for Future Development

1. **Character data script**: Create `scripts/fill_character_data.py` to populate pages 1-6
2. **Field discovery**: Always use `get_fields()` to verify field names before filling
3. **Testing**: Test in multiple PDF viewers (Preview, Adobe Acrobat, Firefox) - font rendering varies
4. **Modularity**: Keep spell extraction, PDF filling, and merging as separate reusable functions
5. **Error handling**: Add validation for missing fields, data type mismatches
6. **Extensibility**: Support other character classes/templates by making field mappings configurable

## Copyright Notice

Spell descriptions are from the Player's Handbook 2024, used under personal use rights as the user owns the physical book. This tool is for personal character sheet generation only, not for distribution of copyrighted content.
