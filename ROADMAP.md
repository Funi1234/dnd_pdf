# Development Roadmap

## Current Status: Proof of Concept Complete ✅

We've successfully demonstrated the **end goal** by manually creating Neez's Artificer sheet. Now we're building the automation to make this repeatable for any character.

---

## Phase 1: Field Extraction (NEXT)

**Goal**: Parse D&D Beyond sheets into structured JSON

### Tasks

#### 1.1 Create Character JSON Schema
- [ ] Define standard character data structure
- [ ] Document all required fields
- [ ] Create example: `schemas/character_data.json`

**Output**: JSON schema documentation

#### 1.2 Expand Field Export Tool
- [ ] Enhance `inspect_pdf_fields.py` to export values
- [ ] Add JSON/YAML output format
- [ ] Support flattened PDFs (read visual data)

**Output**: `scripts/export_pdf_data.py`

#### 1.3 Parse Neez-1.pdf
- [ ] Extract all character data from Neez-1.pdf
- [ ] Create `data/source_characters/neez_dndbeyond.json`
- [ ] Validate against schema

**Options**:
- Manual data entry (fastest for POC)
- OCR parsing (more complex)
- D&D Beyond API (if available)

**Output**: Complete neez_dndbeyond.json

**Acceptance Criteria**:
- ✅ All character data in JSON
- ✅ Matches schema
- ✅ Ready for mapping

---

## Phase 2: Mapping System

**Goal**: Define D&D Beyond → Artificer transformation rules

### Tasks

#### 2.1 Design Mapping Format
- [ ] Choose YAML vs JSON
- [ ] Define mapping syntax
- [ ] Document transformation types
- [ ] Create examples

**Output**: `docs/MAPPING_FORMAT.md`

#### 2.2 Map Character Basics
- [ ] Name, race, class, level
- [ ] Ability scores and modifiers
- [ ] AC, HP, speed, initiative
- [ ] Proficiency bonus

**Output**: `mappings/artificer.yaml` (basic section)

#### 2.3 Map Combat & Skills
- [ ] Attack bonuses
- [ ] Saving throws
- [ ] Skill proficiencies
- [ ] Languages and proficiencies

**Output**: `mappings/artificer.yaml` (combat section)

#### 2.4 Map Spells
- [ ] Spell counts (already done!)
- [ ] Cantrip entries
- [ ] Leveled spell entries
- [ ] Spell descriptions from markdown

**Output**: `mappings/artificer.yaml` (spells section)

#### 2.5 Map Equipment & Features
- [ ] Equipment lists
- [ ] Features and traits
- [ ] Personality traits
- [ ] Background

**Output**: Complete `mappings/artificer.yaml`

**Acceptance Criteria**:
- ✅ All 865 Artificer fields mapped
- ✅ All transformations documented
- ✅ Edge cases handled

---

## Phase 3: Conversion Engine

**Goal**: Automated conversion using mappings

### Tasks

#### 3.1 Build Mapper Module
- [ ] Create `src/mapper.py`
- [ ] Implement JSONPath parsing
- [ ] Implement transformation functions
- [ ] Support array iteration
- [ ] Handle conditionals

**Output**: Working mapper module

#### 3.2 Build Transformation Library
- [ ] Create `src/transforms.py`
- [ ] Implement common transforms:
  - strip_plus: "+5" → "5"
  - calculate_modifier
  - format_components
  - clean_duration (already have!)
- [ ] Document each function

**Output**: Reusable transformation library

#### 3.3 Build Converter Module
- [ ] Create `src/converter.py`
- [ ] Orchestrate: JSON + Mapping + Template → PDF
- [ ] Handle spell sections specially
- [ ] Merge pages with form preservation
- [ ] Error handling and logging

**Output**: Working converter module

#### 3.4 Create CLI Script
- [ ] Create `scripts/convert_character.py`
- [ ] Accept input JSON and template name
- [ ] Validate inputs
- [ ] Call converter
- [ ] Output filled PDF

**Output**: User-friendly conversion script

#### 3.5 Integration Testing
- [ ] Test with Neez's data end-to-end
- [ ] Compare output vs manually-generated PDF
- [ ] Fix discrepancies
- [ ] Validate all 865 fields filled correctly

**Output**: Verified working system

**Acceptance Criteria**:
- ✅ Single command converts Neez
- ✅ Output matches manual PDF
- ✅ All fields correct
- ✅ Conversion takes < 30 seconds

---

## Phase 4: Generalization (Future)

**Goal**: Support multiple classes

### Tasks

#### 4.1 Extract Base Mappings
- [ ] Identify common fields (all classes)
- [ ] Create `mappings/_base.yaml`
- [ ] Artificer inherits from base

**Output**: Reusable base mappings

#### 4.2 Add Wizard Support
- [ ] Get wizard template PDF
- [ ] Create `mappings/wizard.yaml`
- [ ] Test with wizard character

**Output**: Wizard support

#### 4.3 Add Cleric Support
- [ ] Get cleric template PDF
- [ ] Create `mappings/cleric.yaml`
- [ ] Test with cleric character

**Output**: Cleric support

#### 4.4 Documentation
- [ ] Write guide: "Adding a New Class"
- [ ] Document mapping patterns
- [ ] Create template mapping file

**Output**: Community can add classes

**Acceptance Criteria**:
- ✅ 3+ classes supported
- ✅ No code changes to add new class
- ✅ Documented process

---

## Milestones

### Milestone 1: Manual POC ✅ COMPLETE
- [x] Extract spell descriptions from markdown (59/59)
- [x] Generate filled Artificer PDF for Neez
- [x] All spells with descriptions
- [x] Spell counts correct
- [x] Project structure organized

**Status**: COMPLETE (2026-05-31)

### Milestone 2: Data Extraction 🔜 NEXT
- [ ] Character JSON schema defined
- [ ] Neez's D&D Beyond data extracted
- [ ] Validated and ready for mapping

**Target**: Week 1

### Milestone 3: Mapping Complete
- [ ] Full artificer.yaml mapping created
- [ ] All fields documented
- [ ] Transformations defined

**Target**: Week 2

### Milestone 4: Automated Conversion
- [ ] Mapper, converter, and CLI complete
- [ ] End-to-end test with Neez passes
- [ ] Single-command conversion working

**Target**: Week 3

### Milestone 5: Multi-Class Support
- [ ] Base mappings extracted
- [ ] 2+ additional classes supported
- [ ] Documentation complete

**Target**: Month 2

---

## Success Metrics

### Technical
- ✅ 100% of Artificer fields mapped
- ✅ Conversion completes in < 30 seconds
- ✅ Output PDF 100% accurate
- ✅ No manual intervention required
- ✅ Works for any Artificer character

### User Experience
- ✅ Single command: `convert_character.py`
- ✅ Clear error messages
- ✅ Debug mode available
- ✅ Documentation complete

### Extensibility
- ✅ New class = new mapping file only
- ✅ No code changes required
- ✅ Community can contribute
- ✅ Well-documented patterns

---

## Risk & Mitigation

### Risk 1: D&D Beyond PDFs are flattened
**Impact**: Can't extract form field values
**Mitigation**: 
- Use D&D Beyond API/export if available
- Manual JSON creation for POC
- Build OCR parser (complex but doable)

### Risk 2: Field naming inconsistencies
**Impact**: Mappings break on edge cases
**Mitigation**:
- Comprehensive field inspection
- Document all quirks in mapping
- Validation tests catch mismatches

### Risk 3: Spell descriptions are copyrighted
**Impact**: Can't distribute with tool
**Mitigation**:
- User provides own spell markdown
- Extract from user-owned books
- Clear documentation on setup

### Risk 4: Template PDFs differ by version
**Impact**: Mappings break on updates
**Mitigation**:
- Version mappings (artificer_v1.yaml)
- Template version detection
- Migration guides

---

## Open Questions

1. **D&D Beyond Data Source**
   - Can we access D&D Beyond API?
   - Is there a fillable D&D Beyond PDF?
   - Should we build OCR for flattened PDFs?
   
   **Decision needed**: Week 1

2. **Mapping Format**
   - YAML vs JSON for mappings?
   - How to handle complex transformations?
   - Support for plugins/custom transforms?
   
   **Decision needed**: Phase 2 start

3. **Spell Description Source**
   - Always use markdown files?
   - Support other formats?
   - Cache/bundle common spells?
   
   **Decision needed**: Phase 3

4. **Distribution**
   - Share as open source?
   - Licensing considerations?
   - Community mappings repository?
   
   **Decision needed**: After MVP

---

## What We've Learned (Gotchas)

See **CLAUDE.md** for complete list. Key learnings:

1. PDF form field naming is inconsistent - always inspect first
2. pypdf method names are critical - use exact API
3. Merging PDFs loses forms unless cloned properly
4. Font sizing requires manual control
5. Spell components need special handling
6. Page ordering matters for form preservation
7. Checkbox values must be '/Yes' or '/Off'
8. Multiline flag is 4096 (bit 12)
9. Duration cleanup prevents redundancy
10. Test in multiple PDF viewers

These inform our mapping and conversion design!
