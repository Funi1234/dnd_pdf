# Important Discoveries

Key insights discovered during development that affect the conversion system.

## 1. Pages 1 & 2 Are Alternative Layouts (Not Duplicates!)

**Discovery Date**: 2026-05-31

### The Confusion
When extracting fields, we found:
- Page 1: 147 fields
- Page 2: 147 fields with identical structure
- Field names only differ by `-Alt` suffix

Initial assumption: "They must be duplicates or some PDF quirk"

### The Reality
**Pages 1 and 2 are ALTERNATIVE LAYOUTS for the same content!**

- **Page 1**: "Skills Combined" layout
  - Fields: `Front_Character Name`, `Front_Str Score`, etc.
  - Skills section uses a combined/compact layout
  
- **Page 2**: "Skills Separate" layout  
  - Fields: `Front_Character Name-Alt`, `Front_Str Score-Alt`, etc.
  - Skills section uses a separate/expanded layout

### User's Choice
The user can choose which layout they prefer and fill ONLY that page:
- Prefer compact skills? Use page 1 (no `-Alt`)
- Prefer expanded skills? Use page 2 (`-Alt` suffix)
- **Don't fill both!** They represent the same data.

### Impact on Converter

**Configuration Option Needed**:
```yaml
# config.yaml
layout_preference: "combined"  # or "separate"
```

**Mapping Logic**:
```python
if layout_preference == "combined":
    target_field = "Front_Character Name"  # Page 1
else:
    target_field = "Front_Character Name-Alt"  # Page 2
```

**Field Mapping Example**:
```yaml
# mappings/artificer.yaml
character:
  name:
    source: "character.name"
    target: "Front_Character Name"
    target_alt: "Front_Character Name-Alt"  # Alternative layout
    default_layout: "combined"
```

### Validation
When filling PDF:
- ✅ Fill all page 1 fields (no `-Alt`)
- ✅ Fill all page 2 fields (`-Alt` suffix)
- ❌ **DON'T** fill both pages with the same data
- ❌ **DON'T** mix page 1 and page 2 fields

### Implementation Notes

**Recommended Approach**:
1. Default to page 1 (Skills Combined) for simplicity
2. Add `--layout` CLI flag for users who prefer page 2
3. Document both options clearly
4. Mapping file should include both targets

**Example CLI**:
```bash
# Use default (Skills Combined - Page 1)
python convert_character.py neez.json

# Use alternative (Skills Separate - Page 2)  
python convert_character.py neez.json --layout separate
```

### Files Affected
- ✅ `data/artificer_page_guide.md` - Updated to explain layouts
- ✅ `CLAUDE.md` - Added as Gotcha #0
- ⏳ `mappings/artificer.yaml` - Will need both field targets
- ⏳ `src/converter.py` - Will need layout selection logic

---

## 2. Spell Sheet Field Naming Has Space Inconsistency

**Discovery**: Already documented in CLAUDE.md Gotcha #1

**Summary**: 
- `SpellSheet1_Spell Name 01-Alt` (no space before "Spell")
- `SpellSheet 1_Spells Level 01-Alt` (SPACE before "1"!)

---

## 3. Flattened D&D Beyond PDFs Have No Form Fields

**Discovery**: When trying to extract Neez-1.pdf

**Reality**: D&D Beyond exports are flattened - form data is baked into the visual layer, not extractable via form field APIs.

**Impact**: Can't use standard PDF form extraction for source data

**Solution**: Manual JSON creation, OCR, or D&D Beyond API

---

## 4. Spell Layout Preferences - Two Valid Approaches

**Discovery Date**: 2026-05-31

### The Question
For characters with ≤15 total spells (fits on one page), how should we organize them?

### Two Valid Approaches

**Option A: All Spells on Page 7** ✨ SIMPLER
- Use the original page 7 spell sheet (15 slots)
- All cantrips + leveled spells together
- No additional pages needed
- Compact, single-page reference

**Pros**:
- Simpler PDF (no page insertion)
- All spells visible at once
- Fewer pages to flip through

**Cons**:
- Mixed spell levels on one page
- Less organized for characters who will gain more spells

**Example**: Level 2 Wizard with 6 spells total

---

**Option B: Spells Split by Level Across Pages** ✨ MORE ORGANIZED
- Page 7: Spell metadata (DC, attack bonus, slots)
- Page 8: Cantrips only (or first spell level)
- Page 9+: Additional spell levels (if needed)
- Each level gets its own dedicated page

**Pros**:
- Organized by spell level
- Scales as character levels up
- Clear separation
- Room to grow

**Cons**:
- More pages (even if mostly empty)
- Requires page insertion (like we did for Neez)
- More complex PDF generation

**Example**: Same Level 2 Wizard
- Page 7: Spell metadata
- Page 8: 3 cantrips
- Page 9: 3 level-1 spells

---

### Configuration Option Needed

Add to converter config:

```yaml
# config/conversion_settings.yaml
spell_organization:
  # How to organize spells when they fit on one page (≤15 total)
  layout: "by_level"  # or "single_page"
  
  # Threshold for automatic decision
  auto_split_threshold: 15  # If >15 spells, always split by level
  
  # When splitting by level, where to put cantrips
  cantrip_page: "dedicated"  # or "with_level_1"
```

### CLI Flag

```bash
# Use single page for all spells
python convert_character.py neez.json --spell-layout single-page

# Split spells by level (default)
python convert_character.py neez.json --spell-layout by-level
```

### Conversion Logic

```python
def determine_spell_layout(spell_counts, user_preference):
    total_spells = sum(spell_counts.values())
    
    if total_spells > 15:
        # Must split - doesn't fit on one page
        return "by_level"
    
    if user_preference == "single_page":
        # User wants all on page 7
        return "single_page"
    
    # Default: split by level for organization
    return "by_level"
```

### Implementation Impact

**Single Page Layout**:
- Fill page 7 spell entries directly
- No page insertion needed
- Simpler code path
- Use existing page 7 fields

**By-Level Layout**:
- Page 7 = metadata only
- Create temp spell sheets (one per level)
- Fill each sheet
- Insert after page 7
- Merge into final PDF
- More complex but scalable

### Recommendation

**Default Behavior**:
- **Always split by level** for consistency
- Scales as character levels up
- Clearer organization
- Same approach for all characters

**But Offer Option**:
- Let users choose `--spell-layout single-page` for simplicity
- Document both approaches
- Make it configurable

### Files Affected
- ⏳ `config/conversion_settings.yaml` - Add spell_organization section
- ⏳ `src/converter.py` - Implement layout decision logic
- ⏳ `scripts/convert_character.py` - Add CLI flag
- ⏳ `mappings/artificer.yaml` - Document both mapping approaches
- ⏳ `docs/SPELL_LAYOUT_OPTIONS.md` - User guide

---

## Future Discoveries

Document any other surprising findings here to help future development and avoid repeated mistakes.

### Template for New Discoveries

```markdown
## N. Discovery Title

**Discovery Date**: YYYY-MM-DD

### The Confusion
What we initially thought...

### The Reality
What's actually happening...

### Impact on Converter
How this affects our system...

### Solution
How we're handling it...
```
