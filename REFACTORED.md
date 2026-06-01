# Code Refactored - Modular Structure

**Date**: 2026-05-31

## What Changed

Refactored monolithic `create_field_mappings()` function into modular mapper modules.

## New Structure

```
src/field_mappers/
├── __init__.py              # Exports all mappers
├── character_info.py        # Name, race, class, level, background, alignment
├── abilities.py             # STR, DEX, CON, INT, WIS, CHA
├── skills.py                # 18 skills + proficiency markers
├── saving_throws.py         # 6 saving throws + proficiency
├── combat.py                # AC, HP, Initiative, Speed, Proficiency, Hit Dice
└── spells.py                # Spell DC, Attack, Slots, Cantrips
```

## Benefits

### 1. **Clean Separation of Concerns**
Each module handles one specific section:
- `character_info.py` - Basic character data
- `abilities.py` - Just ability scores
- `skills.py` - Just skills
- etc.

### 2. **Supports Both Layouts**
Every mapper accepts `layout='combined'` or `layout='separate'`:
```python
map_skills(char_data, fields, layout='combined')   # Page 1
map_skills(char_data, fields, layout='separate')   # Page 2
```

The mapper automatically adds `-Alt` suffix for separate layout.

### 3. **Easy to Test**
Each mapper is a pure function - easy to unit test:
```python
def test_map_skills():
    char_data = {...}
    fields = {}
    map_skills(char_data, fields, layout='combined')
    assert fields['Front_Skill Arcana'] == '+8'
```

### 4. **Easy to Extend**
Want to add equipment? Just create `equipment.py`:
```python
# src/field_mappers/equipment.py
def map_equipment(char_data, fields, layout='combined'):
    # Implementation here
    pass
```

Then import and use it:
```python
from src.field_mappers import map_equipment
map_equipment(char_data, fields, layout='combined')
```

### 5. **Reusable Across Classes**
Most mappers work for ANY class:
- `character_info.py` - Same for all classes ✅
- `abilities.py` - Same for all classes ✅
- `skills.py` - Same for all classes ✅
- `saving_throws.py` - Just pass different proficient abilities ✅
- `combat.py` - Mostly same (just hit dice type varies) ✅
- `spells.py` - Spell structure similar across casters ✅

### 6. **Configuration-Driven**
Mappers accept parameters for class-specific differences:
```python
# Artificer has CON/INT proficiency
map_saving_throws(char_data, fields, 
                  proficient_abilities=['constitution', 'intelligence'])

# Wizard has INT/WIS proficiency  
map_saving_throws(char_data, fields,
                  proficient_abilities=['intelligence', 'wisdom'])
```

## Usage

### Old Way (Monolithic)
```python
def create_field_mappings(char_data):
    fields = {}
    # 200+ lines of code all in one function
    fields['Front_Character Name'] = ...
    fields['Front_Str Score'] = ...
    fields['Front_Skill Arcana'] = ...
    # ... etc ...
    return fields
```

### New Way (Modular)
```python
from src.field_mappers import (
    map_character_info,
    map_abilities,
    map_skills,
    map_saving_throws,
    map_combat,
    map_spells
)

def create_field_mappings(char_data, layout='combined'):
    fields = {}
    
    map_character_info(char_data, fields, layout=layout)
    map_abilities(char_data, fields, layout=layout)
    map_skills(char_data, fields, layout=layout)
    map_saving_throws(char_data, fields, layout=layout, 
                      proficient_abilities=['constitution', 'intelligence'])
    map_combat(char_data, fields, layout=layout, level=5)
    map_spells(char_data, fields, layout=layout)
    
    return fields
```

## Files

**Old Script**: `scripts/generate_neez_artificer.py` (monolithic, still works)
**New Script**: `scripts/generate_neez_artificer_v2.py` (modular, recommended)

Both generate the same output, but v2 is:
- ✅ Easier to maintain
- ✅ Easier to extend
- ✅ Easier to test
- ✅ Easier to reuse for other classes

## Output

Both scripts produce identical PDFs:
- Old: `output/Neez_Artificer_Test_v1.pdf`
- New: `output/Neez_Artificer_combined.pdf`

## Next Steps

### To Generate Separate Layout
Edit `generate_neez_artificer_v2.py`:
```python
layout = 'separate'  # Change from 'combined'
```

Or create a CLI flag:
```bash
python scripts/generate_neez_artificer_v2.py --layout separate
```

### To Add More Fields
1. Create new mapper in `src/field_mappers/equipment.py`
2. Import in `__init__.py`
3. Call in `create_field_mappings()`

### To Support Another Class
The mappers are already 90% reusable! Just:
1. Change proficient abilities for saving throws
2. Change hit dice type (d8 → d6/d10/d12)
3. Add class-specific spell handling if needed

## Summary

✅ **Refactored successfully**
✅ **All 64 fields still map correctly**
✅ **Code is now modular and maintainable**
✅ **Easy to support both page layouts**
✅ **Ready to extend for other classes**

---

**Migration**: The old script still works, but use `generate_neez_artificer_v2.py` going forward for cleaner, more maintainable code.
