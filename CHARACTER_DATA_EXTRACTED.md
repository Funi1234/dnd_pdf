# Neez Character Data - Fully Extracted

**Date**: 2026-05-31  
**Status**: Ready for mapping iteration ✅

## Files Created

### 1. `data/neez_character_data_extracted.json` (122 KB)
**Raw extraction** - All 794 non-empty fields from D&D Beyond PDF

**Structure**:
```json
{
  "metadata": {...},
  "raw_fields": {
    "CharacterName": {"value": "Ebenezer 'Neez' Tivonhoop", "type": "/Tx", "page": 1},
    "STR": {"value": "8", "type": "/Tx", "page": 1},
    ...
  },
  "organized": {
    "character_info": {...},
    "abilities": {...},
    "skills": {...},
    "combat": {...},
    "spells": {...}
  }
}
```

### 2. `data/neez_character_data_clean.json` (24 KB)
**Structured data** - Clean, organized character data ready for mapping

**Structure**:
```json
{
  "metadata": {...},
  "character": {
    "character_info": {
      "name": "Ebenezer 'Neez' Tivonhoop",
      "class_and_level": "Artificer 5",
      "race": "Gnome",
      "background": "Sage",
      "alignment": "Chaotic Neutral"
    },
    "ability_scores": {
      "strength": {"score": "8", "modifier": "-1"},
      "dexterity": {"score": "14", "modifier": "+2"},
      "intelligence": {"score": "20", "modifier": "+5"},
      ...
    },
    "combat": {
      "armor_class": "19",
      "initiative": "+2",
      "speed": "30 ft. (Walking)",
      "proficiency_bonus": "...",
      ...
    },
    "spellcasting": {
      "ability": "INT",
      "spell_save_dc": "17",
      "spell_attack_bonus": "+9",
      "spellcasting_class": "Artificer"
    },
    "spells": [
      {
        "index": 0,
        "name": "Guidance",
        "prepared": "O",
        "casting_time": "1A",
        "range": "Touch",
        "components": "V,S",
        "duration": "Concentration, up to 1 minute",
        ...
      },
      ...
    ],
    "skills": {
      "acrobatics": {"bonus": "+2", "modifier": "DEX", "proficiency": ""},
      "arcana": {"bonus": "+8", "modifier": "INT", "proficiency": "P"},
      ...
    }
  }
}
```

## Character Summary

**Basic Info**:
- Name: Ebenezer "Neez" Tivonhoop
- Class: Artificer 5
- Race: Gnome
- Background: Sage
- Alignment: Chaotic Neutral

**Ability Scores**:
- STR: 8 (-1)
- DEX: 14 (+2)
- CON: 13 (+1)
- INT: 20 (+5) ⭐ Primary
- WIS: 13 (+1)
- CHA: 10 (+0)

**Combat**:
- AC: 19
- Initiative: +2
- Speed: 30 ft.
- Proficiency Bonus: (extracted)

**Spellcasting**:
- Ability: INT
- Spell Save DC: 17
- Spell Attack Bonus: +9
- Spells Extracted: 60

**Skills** (18 skills with bonuses, modifiers, and proficiencies)

## D&D Beyond Field Quirks Discovered

### 1. Inconsistent Field Naming

**Spaces in unexpected places**:
```
"DEXmod " - has trailing space!
"CHamod" - lowercase 'a' instead of 'Amod'!
```

**Lesson**: Never assume field name patterns - always extract exact names first.

### 2. Spell Field Structure

**Pattern**: `spellName{index}`, `spellPrepared{index}`, etc.

**Fields per spell**:
- `spellName{i}` - Spell name
- `spellPrepared{i}` - Prepared marker ("O" for prepared)
- `spellSource{i}` - Source (class)
- `spellSaveHit{i}` - Save DC or attack bonus
- `spellCastingTime{i}` - Casting time ("1A" = 1 action)
- `spellRange{i}` - Range
- `spellComponents{i}` - "V,S" or "V,S,M"
- `spellDuration{i}` - Duration text
- `spellPage{i}` - Source book reference
- `spellNotes{i}` - Additional notes

**Total spell fields**: ~610 fields (60 spells × ~10 fields each)

### 3. Skill Field Structure

**Pattern**: `{SkillName}`, `{SkillName}Mod`, `{SkillName}Prof`

**Example**:
- `Arcana` = "+8" (total bonus)
- `ArcanaMod` = "INT" (governing ability)
- `ArcanaProf` = "P" (proficiency marker)

**Total**: 18 skills × 3 fields = 54 skill-related fields (but only 40 extracted with values)

### 4. Saving Throw Fields

**Pattern**: `ST {Ability}`, `{Ability}Prof`

**Example**:
- `ST Intelligence` = "+8" (total bonus)
- `IntProf` = "•" (proficient marker)

## Ready for Mapping Iteration

### Approach

1. **Load clean data** - Use `neez_character_data_clean.json`
2. **Load Artificer template** - `data/class_fields/artificer_fields.json`
3. **Build initial mapping** - Start with simple fields (name, abilities, AC)
4. **Generate test PDF** - Fill Artificer template with Neez's data
5. **Compare results** - Open PDF, see what worked, what didn't
6. **Fix mappings** - Correct any misaligned fields
7. **Iterate** - Repeat steps 4-6 until perfect

### Example First Mapping

```yaml
# mappings/artificer.yaml (initial version)

character_info:
  name:
    source: character.character_info.name
    target: Front_Character Name
    
  class_level:
    source: character.character_info.class_and_level
    target: Front_Class  # Need to verify this field name!
    
abilities:
  strength:
    score:
      source: character.ability_scores.strength.score
      target: Front_Str Score
    modifier:
      source: character.ability_scores.strength.modifier
      target: Front_Str Mod
```

### What We Can Map Immediately

✅ **Simple fields**:
- Character name
- Race
- Background
- Ability scores (all 6)
- AC, Initiative, Speed
- Spell DC, Spell Attack
- Skill bonuses

⏳ **Need investigation**:
- Spell slot mapping (need to understand Artificer template spell structure)
- Features/traits (text fields, need to see target layout)
- Equipment (might be complex arrays)

## Next Steps

1. **Create initial mapping YAML** - Start with basic fields
2. **Build mapping engine** - Code to read YAML and apply mappings
3. **Generate test PDF** - Fill Artificer template
4. **Visual inspection** - Open PDF, check what worked
5. **Iterate on mapping** - Fix issues, add more fields
6. **Repeat until complete**

## Files Summary

| File | Size | Purpose |
|------|------|---------|
| `neez_character_data_extracted.json` | 122 KB | Raw extraction, all 794 fields |
| `neez_character_data_clean.json` | 24 KB | Structured data for mapping |
| `dndbeyond_field_definitions.json` | 195 KB | Field structure reference |
| `class_fields/artificer_fields.json` | (varies) | Target template structure |

## Ready to Build Mapping! ✅

All data extracted, cleaned, and structured. Ready to begin Phase 2 (Field Mapping) with iterative approach.

---

**Extraction Date**: 2026-05-31  
**Character**: Ebenezer "Neez" Tivonhoop, Gnome Artificer 5  
**Fields Extracted**: 794 with values, 60 spells  
**Status**: Ready for mapping iteration
