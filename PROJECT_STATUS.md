# Project Status - D&D Beyond to Class-Specific Sheet Converter

**Last Updated**: 2026-05-31

## 🎯 Big Picture Goal

**Convert D&D Beyond character sheets into class-specific fillable PDFs**

Three-phase system:
1. **Extract** - Parse D&D Beyond PDF → structured JSON
2. **Map** - Define D&D Beyond → Artificer field mappings (YAML)
3. **Convert** - Apply mappings → generate filled Artificer PDF

See **VISION.md** for complete architectural overview.

## ✅ Completed (Proof of Concept)

### Project Infrastructure
- ✅ Organized project structure at `~/coding/dnd_pdf/`
- ✅ Virtual environment with pypdf installed
- ✅ Configuration system (paths.json)
- ✅ Source files moved to project
- ✅ Comprehensive documentation (CLAUDE.md, README.md, QUICKSTART.md)

### Spell System
- ✅ **59/59 spells extracted** from markdown files
- ✅ **Spell description parser** handles markdown formatting
- ✅ **Special case handling** (Homunculus Servant, Enlarge/Reduce)
- ✅ **Font sizing** (8pt multiline for descriptions)
- ✅ **Component cleanup** (material text only, checkboxes for V/S/M)
- ✅ **Duration cleanup** (removed redundant "Concentration, up to")

### PDF Generation
- ✅ **12-page character sheet** generated successfully
  - Pages 1-6: Character data (ready for filling)
  - Page 7: Spell metadata (with counts filled: 7 cantrips, 52 spells)
  - Page 8: Cantrips (7 spells with descriptions)
  - Pages 9-10: 1st level spells (24 spells with descriptions)
  - Pages 11-12: 2nd level spells (28 spells with descriptions)
- ✅ **Form field preservation** during PDF merging
- ✅ **All spell data fields filled** correctly

### Utilities
- ✅ **PDF field inspector** (`inspect_pdf_fields.py`)
- ✅ **Modular code structure** (pdf_utils.py, spell_extractor.py)

## ⏳ Next Steps (Three-Phase Plan)

### Phase 1: Field Extraction 🔜 NEXT
**Goal**: Extract D&D Beyond character data to JSON

Tasks:
- [ ] Export PDF fields to JSON (expand inspect_pdf_fields.py)
- [ ] Parse Neez-1.pdf (flattened D&D Beyond sheet)
- [ ] Create standardized character data schema
- [ ] Document D&D Beyond field structure

**Blocker**: Neez-1.pdf is flattened (no form fields)
**Options**: Manual JSON creation, OCR, or D&D Beyond API

### Phase 2: Field Mapping
**Goal**: Create D&D Beyond → Artificer mapping file (YAML)

Tasks:
- [ ] Define mapping schema format
- [ ] Create `mappings/artificer.yaml`
- [ ] Map all character fields
- [ ] Map spell fields (already partially done)
- [ ] Map equipment, features, skills
- [ ] Document transformation rules

### Phase 3: Conversion Engine
**Goal**: Automated conversion from D&D Beyond JSON → Artificer PDF

Tasks:
- [ ] Build mapping engine (src/mapper.py)
- [ ] Build converter (src/converter.py)
- [ ] Create conversion script (scripts/convert_character.py)
- [ ] Test end-to-end with Neez
- [ ] Handle edge cases and errors

### Phase 4: Generalization (Future)
- [ ] Support multiple classes (wizard, cleric, etc.)
- [ ] Create base mappings for common fields
- [ ] Documentation for adding new classes

## 📁 File Locations

### Source Data
- **PDFs**: `~/coding/dnd_pdf/data/source_pdfs/`
- **Character Data**: `~/coding/dnd_pdf/data/character_data/`
- **Spell Markdown**: `~/Library/.../DnD/2. Mechanics/Spells/` (stays in Obsidian)

### Generated Output
- **Complete PDF**: `~/coding/dnd_pdf/output/Neez-Artificer_COMPLETE.pdf`

### Original Files (iCloud)
- **Original Location**: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/DnD/1. The Party/`
- **Files Copied**: 
  - ✅ Neez-Artificer_EU A4.pdf
  - ✅ Spell Sheet-2_EU A4.pdf
  - ✅ neez_character_data.json
  - ✅ neez_spells_converted.json
  - ✅ neez_spells_with_descriptions.json

## 🔧 Quick Commands

```bash
# Activate environment
cd ~/coding/dnd_pdf && source venv/bin/activate

# Generate character sheet
python3 scripts/generate_character_sheet.py

# Inspect PDF fields
python3 scripts/inspect_pdf_fields.py --base
python3 scripts/inspect_pdf_fields.py --spell
python3 scripts/inspect_pdf_fields.py --base --filter "Str"
python3 scripts/inspect_pdf_fields.py --base --values

# Export all fields to JSON
python3 scripts/inspect_pdf_fields.py --base --export fields.json
```

## 📊 Statistics

- **Total Spells**: 59
- **Cantrips**: 7
- **1st Level**: 24
- **2nd Level**: 28
- **PDF Pages**: 12
- **Form Fields (Base)**: 865
- **Form Fields (Spell Sheet)**: 225
- **Project Files**: 15+
- **Lines of Code**: ~500

## 🎯 Success Criteria

- [x] All 59 spells visible with descriptions
- [x] Spell counts correct (7 cantrips, 52 spells)
- [x] Font sizes readable
- [x] Components shown correctly
- [x] Form fields editable
- [ ] Character data filled (name, stats, etc.)
- [ ] All pages complete and accurate
- [ ] Works in multiple PDF viewers

## 🐛 Known Issues

**None currently!** All previous gotchas have been documented and resolved in CLAUDE.md.

## 📚 Documentation

- **CLAUDE.md** - Comprehensive context, gotchas, field reference
- **README.md** - Project overview and features
- **QUICKSTART.md** - Basic usage instructions
- **CHANGELOG.md** - Version history and changes
- **PROJECT_STATUS.md** - This file (current status)

---

**Ready for next step**: Filling character data on pages 1-6!
