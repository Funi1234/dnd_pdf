# Spell Layout Options

Guide to organizing spells in the generated character sheet.

## The Question

When generating a character sheet, how should spells be organized on the pages?

This matters especially for characters with **fewer than 15 total spells** (which would fit on a single spell page).

---

## Two Layout Options

### Option A: Single Page Layout

**All spells together on page 7**

```
Page 7: Spell Page
├── Spell metadata (DC, attack bonus, slots)
├── Cantrips (3 entries)
├── 1st level spells (5 entries)
└── 2nd level spells (4 entries)
Total: 12 spells on one page
```

**When to use**:
- Low-level characters (1-4)
- Classes with few spells known (Rangers, Paladins)
- Prefer compact reference
- Won't learn many more spells

**Pros**:
✅ All spells visible at once
✅ Simpler PDF (fewer pages)
✅ Quick reference
✅ Less page flipping

**Cons**:
❌ Mixed spell levels on one page
❌ Less room to grow
❌ Can look cluttered

**Example Characters**:
- Level 2 Wizard (6 spells)
- Level 3 Paladin (3 spells)
- Level 4 Ranger (5 spells)

---

### Option B: By-Level Layout (Default)

**Each spell level gets its own page**

```
Page 7: Spell Metadata
├── Spellcasting ability
├── Spell save DC
├── Spell attack bonus
└── Spell slots by level

Page 8: Cantrips
├── Guidance
├── Mending
└── (3 more cantrips)

Page 9: 1st Level Spells
├── Cure Wounds
├── Shield
└── (3 more spells)

Page 10: 2nd Level Spells
├── Aid
├── Invisibility
└── (2 more spells)
```

**When to use** (DEFAULT):
- Characters that will level up
- Organized spell reference
- Many spells (>15 total)
- Room to add spells later

**Pros**:
✅ Clear level separation
✅ Room to grow
✅ Scales with leveling
✅ Professional organization

**Cons**:
❌ More pages (even if empty)
❌ More page flipping
❌ Slightly larger PDF

**Example Characters**:
- Level 5 Artificer (59 spells) - REQUIRED
- Level 3 Wizard (8 spells) - still works well
- Any character expected to level up

---

## When Each Layout is Required

### Must Use Single Page
- Total spells ≤ 15 AND user explicitly requests it
- Character will NEVER learn more spells

### Must Use By-Level
- **Total spells > 15** (doesn't fit on one page)
- Character has 3+ spell levels
- User explicitly requests organization

### Can Use Either
- Total spells ≤ 15
- User hasn't specified preference
- **Default: By-Level** for consistency

---

## Configuration

### In Config File

```yaml
# config/conversion_settings.yaml
spell_organization:
  # How to organize spells
  layout: "by_level"  # Options: "single_page" | "by_level"
  
  # Auto-decide based on spell count
  auto_split_threshold: 15  # If >15 spells, force by_level
  
  # Where to put cantrips when splitting
  cantrip_page: "dedicated"  # Options: "dedicated" | "with_first_level"
```

### Via CLI Flag

```bash
# Default (by-level)
python convert_character.py character.json

# Explicit by-level
python convert_character.py character.json --spell-layout by-level

# Single page
python convert_character.py character.json --spell-layout single-page

# Auto-decide based on spell count
python convert_character.py character.json --spell-layout auto
```

---

## Implementation Details

### Single Page Layout

**Process**:
1. Count total spells
2. Verify ≤ 15 (fits on one page)
3. Fill page 7 directly:
   - Spell metadata fields
   - Spell slot 01-Alt through 15-Alt
   - Mix all levels together
4. Done! No page insertion needed

**Code Path**: Simple
```python
def fill_single_page_spells(spells, pdf_writer):
    all_spells = flatten_by_level(spells)  # Combine all levels
    fill_page_7_fields(all_spells[:15])     # Max 15 slots
    return pdf_writer  # No extra pages
```

### By-Level Layout

**Process**:
1. Count spells by level
2. For each level with spells:
   - Create filled spell sheet (temp PDF)
   - One sheet per 15 spells
3. Merge structure:
   - Pages 1-6: Character data
   - Page 7: Spell metadata (DC, attack, slots)
   - Page 8+: Filled spell sheets by level
4. Insert into final PDF

**Code Path**: Complex (already implemented!)
```python
def fill_by_level_spells(spells, pdf_writer):
    cantrip_sheet = create_spell_sheet(spells['cantrip'])
    level1_sheets = create_spell_sheets(spells['level_1'], per_page=15)
    level2_sheets = create_spell_sheets(spells['level_2'], per_page=15)
    
    merge_all([
        base_pages,
        page_7_metadata,
        cantrip_sheet,
        *level1_sheets,
        *level2_sheets
    ])
```

---

## Decision Tree

```
How many total spells?
│
├─> ≤ 15 spells
│   │
│   ├─> User preference set?
│   │   ├─> "single_page" → Use Single Page Layout
│   │   ├─> "by_level" → Use By-Level Layout
│   │   └─> Not set → Use By-Level (default)
│   │
│   └─> Will character level up soon?
│       ├─> Yes → Recommend By-Level
│       └─> No → Either works
│
└─> > 15 spells
    └─> MUST use By-Level Layout (doesn't fit on one page)
```

---

## Examples

### Example 1: Level 2 Cleric (6 spells)

**Spell Count**:
- 3 cantrips
- 3 level-1 spells
- **Total: 6 spells**

**Option A - Single Page**:
```
Page 7: All 6 spells + metadata
Pages: 7 total (character + one spell page)
```

**Option B - By Level** (Default):
```
Page 7: Metadata only
Page 8: 3 cantrips
Page 9: 3 level-1 spells
Pages: 9 total (character + metadata + 2 spell pages)
```

**Recommendation**: Either works, default to By-Level

---

### Example 2: Level 5 Artificer (59 spells)

**Spell Count**:
- 7 cantrips
- 24 level-1 spells
- 28 level-2 spells
- **Total: 59 spells**

**Only Option - By Level**:
```
Page 7: Metadata
Page 8: 7 cantrips
Pages 9-10: Level-1 spells (15 + 9)
Pages 11-12: Level-2 spells (15 + 13)
Pages: 12 total
```

**Why**: Doesn't fit on one page (59 > 15)

---

### Example 3: Level 3 Paladin (3 spells)

**Spell Count**:
- 0 cantrips
- 3 level-1 spells
- **Total: 3 spells**

**Option A - Single Page**:
```
Page 7: 3 spells + metadata
Very clean, lots of empty space
```

**Option B - By Level**:
```
Page 7: Metadata
Page 8: 3 level-1 spells
Mostly empty page
```

**Recommendation**: Single page for simplicity

---

## User Guide Summary

**Default Behavior**: By-Level layout for all characters
- Consistent across all character types
- Scales as characters level up
- Professional organization

**Override to Single Page**:
- Use `--spell-layout single-page` flag
- Best for low-level characters
- Best for classes with few spells
- Prefer compact reference

**Let Converter Decide**:
- Use `--spell-layout auto`
- Single page if ≤ 10 spells
- By-level if > 10 spells

---

## Files Affected by This Feature

- ✅ `IMPORTANT_DISCOVERIES.md` - Documented
- ⏳ `config/conversion_settings.yaml` - Config options
- ⏳ `src/converter.py` - Layout decision logic
- ⏳ `scripts/convert_character.py` - CLI flag
- ⏳ `docs/USER_GUIDE.md` - User documentation

---

**Recommendation**: Default to **By-Level** for consistency, allow **Single Page** as opt-in for simplicity.
