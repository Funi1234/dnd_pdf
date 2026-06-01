# D&D Beyond PDF Variability

## Critical Context

**D&D Beyond character sheet exports are NOT standardized across all characters.**

This document tracks known and potential variations to inform our mapping strategy.

## Known Facts

### What We Know (From Neez's Sheet)

**Neez-1.pdf**:
- Exported: Unknown date
- Character: Level 5 Artificer
- Fields: 1,374 total
- Pages: 6
- Template: Widget annotations (not standard AcroForm)

**Field Structure**:
- Page 1: 146 fields (character info, abilities, skills)
- Page 2: 104 fields (equipment/features?)
- Page 3: 99 fields (more equipment/features?)
- Page 4: 21 fields (personality?)
- Page 5: 500 fields (spells - 450 spell fields + 50 combat)
- Page 6: 504 fields (more spells + equipment)

## Potential Sources of Variation

### 1. Character Level
**Impact**: Higher levels = more features, spell slots, abilities

**Examples**:
- Level 1: Fewer feature boxes
- Level 5: 2nd level spell slots
- Level 20: 9th level spell slots, more features

**Mapping Impact**: 
- Spell slot fields may not exist for low-level characters
- High-level feature fields may be absent in low-level exports

### 2. Class Choice
**Impact**: Different classes have different features

**Examples**:
- Barbarian: Rage features, no spells
- Wizard: Huge spell list, spellbook features
- Fighter: Fighting styles, Action Surge

**Mapping Impact**:
- Class-specific fields may only appear for that class
- Spell fields absent for non-casters

### 3. Character Options Enabled

#### Feats
- With feats: Additional feature boxes
- Without feats: Fewer feature fields

#### Multiclassing
- Single class: Standard layout
- Multiclass: Multiple class sections, complex spell slot calculations

#### Optional Rules
- Variant Human: Extra feat at level 1
- Custom Origin: Different racial trait layout
- Tasha's Custom Lineage: Alternative structure

### 4. Content Sources Enabled

**Player's Handbook Only**:
- Baseline field set
- Standard races, classes, spells

**With Xanathar's Guide**:
- Additional spells
- Subclass features
- Tool proficiencies

**With Tasha's Cauldron**:
- Optional class features
- Custom origins
- Spell versatility

**With Other Sources**:
- Eberron: Dragonmarks, artificer infusions
- Ravnica: Guild backgrounds
- Theros: Supernatural gifts

### 5. Homebrew Content

**Homebrew Enabled**:
- Custom races with unique traits
- Custom classes/subclasses
- Custom spells/items
- May add entirely new field types

**Homebrew Disabled**:
- Standard fields only

### 6. D&D Beyond Feature Changes

**Over Time**:
- D&D Beyond updates their PDF export templates
- Field names may change
- Layout may reorganize
- New features may be added

**Version Examples**:
- 2020 template vs 2024 template
- 2024 PHB update changed spell descriptions
- Future updates unknown

### 7. Character Choices

#### Spellcasters
- Prepared vs Known: Different spell tracking
- Ritual casters: Additional notation fields
- Pact Magic (Warlock): Different slot structure

#### Background
- Different backgrounds = different feature boxes
- Custom backgrounds = variable fields

#### Equipment
- More items = more equipment fields needed
- Magic items may have special fields

## Architecture Implications

### Field Mapping Strategy

**1. Required vs Optional Fields**

```yaml
# Define which fields are required for conversion
required_fields:
  - CharacterName
  - CLASS
  - RACE
  - STR, DEX, CON, INT, WIS, CHA

optional_fields:
  - Feats
  - Multiclass features
  - High-level spell slots
```

**2. Fuzzy Field Matching**

Don't require exact field names - use pattern matching:

```python
# Instead of:
value = dndbeyond_fields['CharacterName']  # Breaks if named differently

# Use:
value = find_field_fuzzy(dndbeyond_fields, patterns=[
    'CharacterName',
    'Character Name', 
    'Name',
    'PC_Name'
])
```

**3. Graceful Degradation**

```python
# If a field is missing, skip it - don't crash
if 'Feat_1' in dndbeyond_fields:
    convert_feat(dndbeyond_fields['Feat_1'])
else:
    log.warning("No Feat_1 field found - skipping feats")
```

**4. Validation Reports**

Generate a report after conversion:

```
✅ Mapped successfully: 145/150 fields
⚠️  Missing source fields: 5
  - Feat_1 (optional)
  - Feat_2 (optional)
  - MulticlassSpellSlots (optional)
❌ Critical fields missing: 0
```

**5. Manual Override Files**

Allow users to specify custom mappings:

```yaml
# custom_mappings.yaml
field_overrides:
  CharacterName: "PC Name"  # My D&D Beyond uses "PC Name" instead
  CLASS: "Class and Level"  # Combined field in my export
```

## Testing Strategy

### Test Coverage Needed

**Character Variations**:
- Level 1, 5, 10, 20 characters
- Each core class
- Multiclass combinations
- With/without feats
- Different sources enabled

**Export Variations**:
- Recent exports (2024+)
- Older exports (if available)
- Different browsers/devices
- Different D&D Beyond subscription tiers

### Validation Approach

1. **Extract fields from test PDF**
2. **Compare to Neez baseline**
3. **Document differences**
4. **Update mapping rules**
5. **Re-test conversion**

## Current Status

**What We Have**:
- ✅ Neez's field structure documented (1,374 fields)
- ✅ Extraction works for Widget annotation style
- ✅ Page-by-page organization complete

**What We Need**:
- ⏳ Test with other D&D Beyond exports
- ⏳ Document field name variations
- ⏳ Build fuzzy matching system
- ⏳ Create validation reporting
- ⏳ Test graceful degradation

## Recommendations

### For Phase 2 (Mapping)

1. **Start with Neez** - Build mapping for what we have
2. **Mark fields as required/optional** - Be explicit about criticality
3. **Use pattern matching** - Don't hardcode exact field names
4. **Log everything** - Track what mapped, what didn't, why
5. **Build validation first** - Know what we're missing before trying to convert

### For Phase 3 (Conversion)

1. **Validate before converting** - Check required fields exist
2. **Skip gracefully** - Missing optional fields → skip, don't error
3. **Generate reports** - Tell user what worked, what didn't
4. **Allow overrides** - Let users fix our assumptions

### For Phase 4 (Multi-Class Support)

1. **Compare templates** - See what's common, what's unique
2. **Extract common mappings** - Build base mapping for all classes
3. **Class-specific overrides** - Layer class-specific rules on top
4. **Test cross-class** - Ensure flexibility works

## Future Work

### When We Get More Test Data

**Collect**:
- More D&D Beyond exports (volunteers?)
- Different character types
- Different levels
- Different dates

**Document**:
- Field name variations observed
- Missing fields patterns
- New fields discovered
- Structure differences

**Adapt**:
- Update fuzzy matching patterns
- Expand optional field list
- Improve validation logic
- Document workarounds

## See Also

- `CLAUDE.md` - All gotchas and solutions
- `ARCHITECTURE.md` - Mapping system design
- `data/dndbeyond_field_definitions.json` - Neez's structure (our baseline)
- `ROADMAP.md` - Development plan

---

**Last Updated**: 2026-05-31  
**Baseline**: Neez-1.pdf (Level 5 Artificer, 1,374 fields)  
**Status**: Documented assumption - needs real-world validation
