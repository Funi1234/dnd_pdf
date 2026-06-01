# Quick Status - D&D PDF Converter

**Last Updated**: 2026-05-31

## Current State

✅ **Phase 1: Field Extraction - COMPLETE**

## What We Have

📄 **Source Template (D&D Beyond)**:
- File: `data/dndbeyond_field_definitions.json`
- Fields: 1,374 (from Neez, Level 5 Artificer)
- ⚠️ WARNING: D&D Beyond PDFs vary - this is ONE example

📄 **Target Templates (All 13 Classes)**:
- Directory: `data/class_fields/`
- Total: 20,343 fields across 13 classes
- Range: 865 fields (Monk) → 2,034 fields (Fighter)

## File Structure

```json
{
  "pages": {
    "page_1": {
      "categories": {
        "abilities": {"fields": [...]},
        "combat": {"fields": [...]},
        "skills": {"fields": [...]}
      }
    }
  }
}
```

## Critical Insight 💡

**D&D Beyond PDFs are NOT standardized!**

Different characters = different field structures because of:
- Character level
- Class choice
- Feats/multiclass enabled
- Content sources (PHB vs Xanathar's vs Tasha's)
- Template version updates

**Impact**: Field mapping must be flexible, not rigid.

See: `DNDBEYOND_VARIABILITY.md`

## Next Phase

⏳ **Phase 2: Field Mapping**

Create `mappings/artificer.yaml` to define:
- D&D Beyond field → Artificer field transformations
- Required vs optional fields
- Data transformations ("+5" → "5")
- Array handling (spells, equipment)

## Quick Navigation

**Documentation**:
- `EXTRACTION_COMPLETE.md` - Full extraction summary
- `DNDBEYOND_VARIABILITY.md` - Critical variability context
- `CLAUDE.md` - All gotchas and solutions
- `ARCHITECTURE.md` - System design

**Data Files**:
- `data/dndbeyond_field_definitions.json` - Source
- `data/class_fields/artificer_fields.json` - Target
- `data/class_fields/README.md` - Class reference

**Tools**:
- `scripts/extract_all_class_fields.py` - Re-extract all
- `scripts/inspect_pdf_fields.py` - Interactive inspection

## Statistics

- 📄 14 PDFs analyzed (1 D&D Beyond + 13 classes)
- 🔢 21,717 total fields extracted
- 📑 111 pages with fields
- 🏷️ 10 automatic categories
- 📊 20,343 class template fields
- ✅ 100% extraction complete

## Key Files Summary

| What | File | Fields | Purpose |
|------|------|--------|---------|
| SOURCE | `dndbeyond_field_definitions.json` | 1,374 | Where data comes FROM |
| TARGET | `class_fields/artificer_fields.json` | 1,334 | Where data goes TO |
| Smallest | `class_fields/monk_fields.json` | 865 | Non-spellcaster |
| Largest | `class_fields/fighter_fields.json` | 2,034 | Many options |

---

**Progress**: 25% (Phase 1 of 4 complete)  
**Status**: Ready for Phase 2 (Field Mapping)
