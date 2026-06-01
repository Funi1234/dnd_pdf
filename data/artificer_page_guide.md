# Artificer Template - Page Guide

Human-readable guide to what's on each page of the Artificer character sheet.

## Overview

- **Total Pages**: 8
- **Total Fields**: 865
- **Pages with Fields**: 6 (pages 5 & 6 have no form fields)

---

## Page 1: Character Sheet Front - "Skills Combined" Layout

**Field Count**: 147 fields

**Layout Style**: Skills Combined

### What's on this page:
- **Character Identity**
  - Name, Race, Class, Background, Alignment
  - Level, XP, Proficiency Bonus
  
- **Ability Scores** (Left column)
  - STR, DEX, CON, INT, WIS, CHA
  - Scores, Modifiers, Saving Throws
  
- **Skills** (Combined layout)
  - All 18 skills with proficiency/expertise checkboxes
  - Skill bonuses in one section
  
- **Combat Stats** (Center)
  - AC, Initiative, Speed
  - HP (Max, Current, Temp)
  - Hit Dice
  
- **Inspiration & Proficiency**
  
- **Saving Throw Proficiencies**

### Categories:
- Abilities: 28 fields
- Skills & Saves: 17 fields
- Combat: 6 fields
- Spells: 22 fields (spell slots, DC, attack bonus)
- Attacks: 11 fields
- Character Info: 4 fields
- Proficiencies: 19 fields
- Features: 4 fields
- Other: 36 fields

---

## Page 2: Character Sheet Front - "Skills Separate" Layout

**Field Count**: 147 fields

**Layout Style**: Skills Separate (Alternative Layout)

### What's on this page:
Same content as Page 1, but with a different visual layout for skills.

**Field Names**: All field names end with `-Alt` suffix

**Purpose**: This is an alternative layout of the character sheet front page. Users can choose which layout they prefer (combined or separate skills) and fill only that page.

**Example Field Names**:
- Page 1: `Front_Character Name`
- Page 2: `Front_Character Name-Alt`

**Note**: When filling the PDF, you should fill EITHER page 1 OR page 2, not both (they represent the same data in different layouts).

---

## Page 3: Character Sheet - Back (Left Side)

**Field Count**: 57 fields

### What's on this page:
- **Personality & Appearance**
  - Personality Traits
  - Ideals
  - Bonds
  - Flaws
  
- **Physical Description**
  - Age, Height, Weight
  - Eyes, Skin, Hair
  
- **Equipment** (partial list)

### Categories:
- Equipment: 15 fields
- Character Info: 1 field
- Features: 2 fields
- Abilities: 2 fields
- Other: 37 fields

---

## Page 4: Character Sheet - Back (Right Side)

**Field Count**: 81 fields

### What's on this page:
- **Features & Traits**
  - Class Features
  - Racial Traits
  - Feats
  
- **Additional Equipment**
  - Weapons
  - Armor
  - Gear
  
- **Backstory**
  - Character backstory text
  - Allies & Organizations
  
- **Treasure**
  - Coins (CP, SP, EP, GP, PP)

### Categories:
- Equipment: 15 fields
- Features: 2 fields
- Abilities: 14 fields
- Attacks: 4 fields
- Combat: 4 fields
- Skills & Saves: 1 field
- Character Info: 1 field
- Other: 40 fields

---

## Page 5: Additional Features

**Field Count**: 0 fields (no form fields - free text area)

This page appears to be for writing additional notes, features, or backstory.

---

## Page 6: Equipment & Notes

**Field Count**: 0 fields (no form fields - free text area)

Additional space for equipment lists, treasure, notes.

---

## Page 7: Spellcasting Page 1

**Field Count**: 208 fields

### What's on this page:
- **Spellcasting Info**
  - Spellcasting Class
  - Spellcasting Ability
  - Spell Save DC
  - Spell Attack Bonus
  
- **Spell Slots**
  - 1st through 9th level slots
  - Total slots and expended slots
  
- **Cantrips Known**
- **Spells Known/Prepared**

- **Component Pouch** (checkboxes for prepared components)

### Categories:
- Spells: 196 fields
- Abilities: 12 fields

**Primary Purpose**: Spell metadata and slot tracking

---

## Page 8: Spell List

**Field Count**: 225 fields (15 spell entries × 15 fields each)

### What's on this page:
- **15 Spell Slots** with full details per spell:
  - Spell Name
  - Level
  - School
  - Casting Time
  - Range
  - Components (V/S/M checkboxes + material text)
  - Duration
  - Save
  - Spell Effect (description)
  - Concentration checkbox
  - Ritual checkbox
  - Prepared checkbox

### Categories:
- Spells: 210 fields
- Abilities: 15 fields

**Primary Purpose**: Detailed spell entries

**Note**: For characters with more than 15 spells, additional copies of "Spell Sheet-2" can be inserted.

---

## Field Naming Patterns

### Prefixes by Page:
- **Front_**: Pages 1-2 (character sheet front)
- **Back_**: Pages 3-4 (character sheet back)
- **SpellSheet 1_**: Page 7 (spell metadata) - Note the SPACE
- **SpellSheet1_**: Page 8 (spell entries) - Note NO space
- **Attune_**: Appears on equipment pages

### Common Suffixes:
- **-Alt**: Alternative version of the same field (for compatibility)
- **-SK**: Unknown purpose (possibly "skill"?)
- **01-Alt**, **02-Alt**, etc.: Array indices for repeated fields (spells, equipment)

### Field Type Codes:
- **/Tx**: Text field (single or multi-line)
- **/Btn**: Button/Checkbox field

---

## Tips for Using This Guide

1. **Finding a specific field**: Use the category breakdown
2. **Understanding duplicates**: Fields ending in "-Alt" are duplicates for compatibility
3. **Spell fields**: Pages 7-8 have different naming (watch for the space!)
4. **Array fields**: Look for numbered suffixes like "01-Alt", "02-Alt"
5. **Equipment**: Scattered across pages 3-4, look for "Attune_" and "Equipment" prefixes

---

## Quick Reference

| Page | Primary Content | Field Count | Key Categories | Notes |
|------|----------------|-------------|----------------|-------|
| 1 | Character Front - Skills Combined | 147 | Abilities, Skills, Combat | Use page 1 OR 2 |
| 2 | Character Front - Skills Separate | 147 | Same as Page 1 | Alternative layout |
| 3 | Personality, Appearance | 57 | Equipment, Features | |
| 4 | Features, Backstory, Treasure | 81 | Equipment, Features | |
| 5 | Notes (no fields) | 0 | - | Free text area |
| 6 | Notes (no fields) | 0 | - | Free text area |
| 7 | Spell Metadata & Slots | 208 | Spells (metadata) | |
| 8 | Spell Details (15 slots) | 225 | Spells (entries) | Can add more sheets |

**Total Unique Fields**: ~432 (pages 1 and 2 are alternatives of the same 147 fields)
**Total Fields with Alternatives**: 865

**Important**: Pages 1 and 2 represent the SAME data in different layouts. When filling, use:
- Page 1 fields (no suffix) for "Skills Combined" layout
- Page 2 fields (`-Alt` suffix) for "Skills Separate" layout
- **NOT BOTH** - they're alternatives, not additive
