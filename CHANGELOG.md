# Changelog

## 2026-05-31 - Initial Project Setup

### Created Project Structure
- Organized project at `~/coding/dnd_pdf/`
- Separated source code, scripts, data, and output
- Added configuration system for flexible paths
- Created virtual environment with pypdf dependency

### Implemented Spell System
✅ **Spell Description Extraction**
- Built markdown parser for spell files (59/59 spells extracted)
- Handled special naming cases (Homunculus Servant, Enlarge/Reduce)
- Cleaned dice notation and formatting from markdown

✅ **PDF Generation**
- Created modular spell sheet filling system
- Implemented 8pt font sizing for descriptions
- Added multiline support for long spell descriptions
- Proper component handling (checkboxes vs material text)
- Duration cleanup (removed redundant "Concentration, up to")

✅ **PDF Merging**
- Preserved form fields during merge using `clone_document_from_reader()`
- Filled spell counts before merging to maintain `/AcroForm`
- Created 12-page complete character sheet:
  - Pages 1-6: Character data (blank for now)
  - Page 7: Spell metadata (slots, DC, attack bonus)
  - Page 8: Cantrips (7 spells)
  - Pages 9-10: 1st level spells (24 spells)
  - Pages 11-12: 2nd level spells (28 spells)

### Files Moved to Project
- ✅ Source PDFs (base template + spell sheet)
- ✅ Character data JSON files
- ✅ Spell data with descriptions
- 📁 Spell markdown files remain in Obsidian vault

### Documentation Created
- ✅ README.md - Project overview
- ✅ QUICKSTART.md - Basic usage guide
- ✅ CLAUDE.md - Comprehensive context and gotchas
- ✅ CHANGELOG.md - This file
- ✅ .gitignore - Standard Python/PDF ignores

### Known Issues Solved
1. ✅ Wrong pypdf method names
2. ✅ Form field naming inconsistencies
3. ✅ Font size cutting off descriptions
4. ✅ Merged PDFs losing form fields
5. ✅ Components showing "V,S" instead of materials only
6. ✅ Duration showing redundant "Concentration, up to"
7. ✅ Checkbox values using wrong format
8. ✅ Spell counts not filling after merge
9. ✅ Cantrips not appearing on correct page
10. ✅ Can't modify PDF pages list directly

## Next Steps

### High Priority
1. **Fill Character Data**: Create script to populate pages 1-6
   - Name, race, class, level
   - Ability scores and modifiers
   - AC, HP, speed, initiative
   - Skills and saving throws
   - Proficiencies and languages
   - Equipment and features

### Medium Priority
2. **Field Discovery Tool**: Script to explore PDF field names
3. **Validation**: Verify all fields are filled correctly
4. **Testing**: Test in multiple PDF viewers

### Low Priority
5. **Extensibility**: Support other character classes
6. **CLI Arguments**: Make script configurable from command line
7. **Error Handling**: Better validation and error messages

## Version History

**v0.1.0** (2026-05-31)
- Initial project setup
- Spell system complete
- PDF generation working
- Documentation comprehensive
