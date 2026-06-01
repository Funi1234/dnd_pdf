# Next Steps: Spell Filling Implementation

## Current Status

### ✅ What's Working
- **Page assembly system** using pikepdf (fixes pypdf rendering issues)
- **Page 1 (Front):** All stats, abilities, skills, saves, combat, proficiencies ✅
- **Page 2 (Background):** Physical traits, personality, backstory (3700+ chars split intelligently), portrait ✅
- **Page 3 (Spells):** Template loaded but NOT filled yet ⏳

### 🎯 Goal
Fill the `spells_main.pdf` template with Neez's cantrips and leveled spells from D&D Beyond data.

---

## Spell Data Available

### Location in Raw Data
Neez's spell data is in `data/neez_character_data_extracted.json`:
- **page_5**: 460+ spell fields (cantrips and 1st/2nd level)
- **page_6**: 154 spell fields (continuation)

### Data Structure
```
spellHeader0: === CANTRIPS ===
spellHeader1: === 1st LEVEL ===
spellHeader2: === 2nd LEVEL ===

For each spell (index 00-49+):
- spellName{i:02d}: "Shocking Grasp"
- spellPrepared{i:02d}: "P" (prepared) or "O" (not prepared)
- spellLevel{i:02d}: level number
- spellSchool{i:02d}: "Evocation"
- spellCastingTime{i:02d}: "1 Action"
- spellRange{i:02d}: "Touch"
- spellDuration{i:02d}: "Instantaneous"
- spellComponents{i:02d}: "V, S"
- etc.
```

### Template Fields (spells_main.pdf)
```
SpellSheet 1_Spell DC
SpellSheet 1_Spell Atk
SpellSheet 1_Cantrips Known
SpellSheet 1_Spells Known
SpellSheet1_Spell Name 01
SpellSheet1_Spell Name 02
...
SpellSheet1_Spell Name 12
```

---

## Existing Code to Adapt

### 1. Spell Extraction (needs to be written)
Add to `scripts/convert_raw_to_clean.py`:

```python
def extract_spells(pages_data):
    """Extract cantrips and spells from D&D Beyond data"""
    spells = []
    
    # Spells are on page_5 and page_6
    # Parse spellHeader0, spellHeader1, spellHeader2 to separate by level
    # For each spell index (00-49):
    #   - Check spellName{i:02d} for spell name
    #   - Check spellPrepared{i:02d} for prepared status
    #   - Determine level based on which header section it falls under
    #   - Build spell dict with all fields
    
    return spells
```

**Strategy:**
1. Find `spellHeader0`, `spellHeader1`, `spellHeader2` indices
2. Iterate through spell indices and assign level based on header position
3. Extract all spell fields for each index
4. Return list of spell dicts

### 2. Spell Filling (exists but uses pypdf - needs pikepdf)
File: `src/pdf_utils.py` has `fill_spell_sheet()` function

**Problem:** Uses pypdf which doesn't preserve page content
**Solution:** Adapt the logic to pikepdf in the assembly script

### 3. Field Name Mapping
The existing code uses different field names than the template:
- **Old (different template):** `SpellSheet1_Spell Name 01-Alt`
- **New (spells_main.pdf):** `SpellSheet1_Spell Name 01`

Need to verify exact field names on the template.

---

## Implementation Steps

### Step 1: Extract Spell Data
**File:** `scripts/convert_raw_to_clean.py`

Add `extract_spells()` function that:
1. Searches for `spellHeader0` to find cantrip section start
2. Iterates through `spellName{i:02d}` fields
3. Groups by spell level based on header positions
4. Returns structured spell list

Add to the `convert_raw_to_clean()` function:
```python
'spells': extract_spells(pages_data),
```

### Step 2: Update Spell Mapper
**File:** `src/field_mappers/spells.py`

Currently just a placeholder. Needs to:
```python
def map_spells(char_data, fields, layout='combined', spell_template_type='generic'):
    """Map spell fields to template"""
    
    spells = char_data.get('spells', [])
    
    # Separate cantrips from leveled spells
    cantrips = [s for s in spells if s.get('level') == '0' or s.get('level') == 'Cantrip']
    leveled = [s for s in spells if s.get('level') not in ['0', 'Cantrip', '']]
    
    # Fill spell DC/Attack (already in core, may not need here)
    # fields['SpellSheet 1_Spell DC'] = char_data['spellcasting']['spell_save_dc']
    # fields['SpellSheet 1_Spell Atk'] = char_data['spellcasting']['spell_attack_bonus']
    
    # Fill cantrips known count
    fields['SpellSheet 1_Cantrips Known'] = str(len(cantrips))
    
    # Fill spell names (up to 12 slots)
    # Strategy: Put cantrips first, then leveled spells
    all_spells_to_show = cantrips + leveled
    
    for i, spell in enumerate(all_spells_to_show[:12], 1):
        fields[f'SpellSheet1_Spell Name {i:02d}'] = spell['name']
        # Add other fields: level, school, prepared, etc.
    
    return fields
```

### Step 3: Integrate with Assembly
**File:** `scripts/assemble_character_sheet_pikepdf.py`

The `create_field_mappings()` function already calls `map_spells()` for the 'spells' section.

Should work automatically once Step 1 & 2 are done!

### Step 4: Test
```bash
cd ~/coding/dnd_pdf

# Re-extract with spell data
source venv/bin/activate
python scripts/convert_raw_to_clean.py \
  --input data/neez_character_data_extracted.json \
  --output data/neez_character_data_clean.json

# Regenerate sheet
python scripts/assemble_character_sheet_pikepdf.py \
  --data data/neez_character_data_clean.json \
  --output output/Neez_Artificer_Test_v1.pdf \
  --pages \
    "class_specific/artificer/artificer_front_separate.pdf:front" \
    "generic/background_regular.pdf:background" \
    "generic/spells_main.pdf:spells"

# Check page 3 in Brave
```

---

## Key Decisions Needed

1. **Which spells to show?**
   - Only prepared spells? (filter by `prepared == 'P'`)
   - All spells? (would overflow 12 slots)
   - Cantrips + prepared only?

2. **Field mapping complexity:**
   - Just spell names (simple)? ✅ Quick win
   - Full details (level, school, components, etc.)? ⏳ More work

3. **Multiple pages:**
   - Template has 12 spell slots
   - Neez has 30+ spells available
   - Need multiple spell pages or filter to top 12?

---

## Quick Win Approach

For fastest results, just fill spell names:

```python
# In map_spells():
cantrips = [s for s in spells if s.get('level') == '0']
prepared = [s for s in spells if s.get('prepared') == 'P' and s.get('level') != '0']

to_show = (cantrips + prepared)[:12]

for i, spell in enumerate(to_show, 1):
    fields[f'SpellSheet1_Spell Name {i:02d}'] = spell['name']
```

This gets spells visible on page 3 with minimal code!

---

## Files to Edit

1. ✏️ `scripts/convert_raw_to_clean.py` - Add `extract_spells()` function
2. ✏️ `src/field_mappers/spells.py` - Implement actual spell mapping
3. 📖 `data/neez_character_data_clean.json` - Will be updated by step 1
4. ✅ `scripts/assemble_character_sheet_pikepdf.py` - Already calls spell mapper, no changes needed

---

## Testing Commands

```bash
# Check what spell data exists in raw
python3 << 'EOF'
import json
with open('data/neez_character_data_extracted.json') as f:
    raw = json.load(f)
page5 = raw['pages']['page_5']['fields']

# Find spell names
for i in range(0, 30):
    name = page5.get(f'spellName{i:02d}', {}).get('value', '')
    prep = page5.get(f'spellPrepared{i:02d}', {}).get('value', '')
    if name:
        print(f"{i}: {name} (Prep: {prep})")
EOF

# Check template field names
source venv/bin/activate
python3 << 'EOF'
import pikepdf
pdf = pikepdf.open('data/source_pdfs/generic/spells_main.pdf')
for annot in pdf.pages[0].Annots:
    if annot.Subtype == '/Widget' and '/T' in annot:
        name = str(annot.T)
        if 'Spell Name' in name:
            print(name)
EOF
```

---

## Expected Result

After implementation, `output/Neez_Artificer_Test_v1.pdf` page 3 should show:
- Spell DC: 17
- Spell Attack: +9
- Cantrips Known: 4
- Spell Names 01-12: Neez's prepared spells and cantrips

---

## Notes

- **pikepdf vs pypdf:** All new code must use pikepdf (pypdf loses page content)
- **Checkbox handling:** Use `pikepdf.Name('/Yes')` not `pikepdf.String('/Yes')`
- **Field name verification:** Always verify exact field names from template before coding
- **Smart splitting:** Background backstory uses smart paragraph splitting - spells might need similar for descriptions

---

## Current Working Command

```bash
cd ~/coding/dnd_pdf && source venv/bin/activate && \
python scripts/assemble_character_sheet_pikepdf.py \
  --data data/neez_character_data_clean.json \
  --output output/Neez_Artificer_Test_v1.pdf \
  --pages \
    "class_specific/artificer/artificer_front_separate.pdf:front" \
    "generic/background_regular.pdf:background" \
    "generic/spells_main.pdf:spells"
```

Currently generates:
- ✅ 95 fields filled
- ✅ Page 1: All front stats
- ✅ Page 2: Background with portrait
- ⏳ Page 3: Spell template (empty)

Good luck! 🚀
