# System Architecture

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    D&D BEYOND SOURCE                         │
├─────────────────────────────────────────────────────────────┤
│  • PDF Export (flattened)                                   │
│  • JSON Export (from API)                                   │
│  • Manual data entry                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              PHASE 1: EXTRACTION                             │
├─────────────────────────────────────────────────────────────┤
│  Tools:                                                      │
│  • extract_dnd_beyond.py                                    │
│  • src/extractors/pdf_extractor.py                          │
│  • src/extractors/dndbeyond_parser.py                       │
│                                                              │
│  Output Format (JSON):                                       │
│  {                                                           │
│    "character": {                                            │
│      "name": "...",                                          │
│      "class": "...",                                         │
│      "level": 5                                              │
│    },                                                        │
│    "abilities": {...},                                       │
│    "spells": [...],                                          │
│    "equipment": [...]                                        │
│  }                                                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              PHASE 2: MAPPING DEFINITION                     │
├─────────────────────────────────────────────────────────────┤
│  Files: mappings/<class>.yaml                                │
│                                                              │
│  Example (artificer.yaml):                                   │
│  ─────────────────────────                                  │
│  character:                                                  │
│    name:                                                     │
│      source: "character.name"                                │
│      target: "Front_Character Name"                          │
│                                                              │
│  abilities:                                                  │
│    strength:                                                 │
│      score:                                                  │
│        source: "abilities.strength.score"                    │
│        target: "Front_Str Score"                             │
│      modifier:                                               │
│        source: "abilities.strength.modifier"                 │
│        target: "Front_Str Mod"                               │
│        transform: strip_plus  # "+5" → "5"                   │
│                                                              │
│  spells:                                                     │
│    cantrips:                                                 │
│      source: "spells[level=Cantrip]"                         │
│      target: "SpellSheet1_Spell Name {index:02d}-Alt"        │
│      max_count: 15                                           │
│      fields:                                                 │
│        name: "name"                                          │
│        school: "school"                                      │
│        # ...                                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────┐
                 │                 │
                 ▼                 ▼
┌──────────────────────┐  ┌───────────────────────┐
│  CHARACTER DATA      │  │  CLASS TEMPLATE       │
│  (JSON)              │  │  (PDF)                │
├──────────────────────┤  ├───────────────────────┤
│  From extraction     │  │  Artificer template   │
│  phase               │  │  with 865 fields      │
└──────────┬───────────┘  └──────────┬────────────┘
           │                         │
           │                         │
           └────────┬────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              PHASE 3: CONVERSION ENGINE                      │
├─────────────────────────────────────────────────────────────┤
│  Components:                                                 │
│                                                              │
│  1. src/mapper.py                                            │
│     • Loads mapping YAML                                     │
│     • Parses source paths (JSONPath)                         │
│     • Applies transformations                                │
│     • Returns field → value dictionary                       │
│                                                              │
│  2. src/converter.py                                         │
│     • Orchestrates conversion                                │
│     • Loads character JSON                                   │
│     • Loads template PDF                                     │
│     • Calls mapper for field values                          │
│     • Fills PDF using pdf_utils                              │
│     • Handles special cases (spells, arrays)                 │
│                                                              │
│  3. scripts/convert_character.py                             │
│     • CLI interface                                          │
│     • Validates inputs                                       │
│     • Calls converter                                        │
│     • Generates output                                       │
│                                                              │
│  Process Flow:                                               │
│  ──────────────                                              │
│  1. Load character JSON                                      │
│  2. Detect character class                                   │
│  3. Load class mapping (artificer.yaml)                      │
│  4. Load class template (Artificer PDF)                      │
│  5. For each mapping rule:                                   │
│     a. Extract value from JSON (JSONPath)                    │
│     b. Apply transformation (if any)                         │
│     c. Write to PDF field                                    │
│  6. Handle special sections:                                 │
│     • Spells → multiple spell sheets                         │
│     • Equipment → item lists                                 │
│     • Features → text blocks                                 │
│  7. Merge all pages                                          │
│  8. Write output PDF                                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                 FILLED CLASS-SPECIFIC PDF                    │
├─────────────────────────────────────────────────────────────┤
│  • All character data filled                                 │
│  • All spells with descriptions                              │
│  • Class-specific layout                                     │
│  • Ready for play!                                           │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Extractors
**Purpose**: Get data out of various sources into standard JSON

- `pdf_extractor.py` - Generic PDF field extraction
- `dndbeyond_parser.py` - Parse D&D Beyond specific formats
- `ocr_extractor.py` - OCR for flattened PDFs (future)

**Input**: PDF, API response, manual data
**Output**: Standardized character JSON

### Mapper
**Purpose**: Transform source data to target PDF fields

- Reads YAML mapping definitions
- Supports JSONPath for source queries
- Applies transformation functions
- Handles arrays and iteration
- Returns `{field_name: value}` dictionary

**Input**: Character JSON + Mapping YAML
**Output**: Field mapping dictionary

### Converter
**Purpose**: Orchestrate the conversion process

- Loads all required files
- Coordinates mapper and PDF utils
- Handles complex sections (spells, equipment)
- Manages page merging
- Error handling and validation

**Input**: Character JSON + Template PDF + Mapping
**Output**: Filled PDF

### PDF Utils
**Purpose**: Low-level PDF manipulation

- Fill form fields
- Modify field properties (font, multiline)
- Merge PDFs while preserving forms
- Clone pages
- Already implemented!

## Mapping Schema

### Basic Mapping
```yaml
field_name:
  source: "path.to.field"  # JSONPath
  target: "PDF_Field_Name"
  transform: function_name  # Optional
  default: "value"          # If source missing
```

### Array Mapping
```yaml
spells:
  cantrips:
    source: "spells[?level=='Cantrip']"  # JSONPath filter
    target: "SpellSheet1_Spell Name {index:02d}-Alt"
    max_count: 15
    fields:
      name: "name"
      school: "school"
      range: "range"
```

### Conditional Mapping
```yaml
class_feature:
  condition: "character.class == 'Artificer'"
  source: "features.artificer_specific"
  target: "Front_Class Feature"
```

### Transform Functions
```python
# src/transforms.py
def strip_plus(value):
    """Remove + from modifier: '+5' → '5'"""
    return value.lstrip('+')

def calculate_modifier(score):
    """Calculate ability modifier from score"""
    return str((int(score) - 10) // 2)

def format_spell_components(components):
    """Extract material components only"""
    # "V,S,M (copper wire)" → "copper wire"
    pass
```

## Extensibility

### Adding a New Class
1. Get class-specific PDF template
2. Create `mappings/<class>.yaml`
3. Map all fields using mapping schema
4. Test with character data

**No code changes required!**

### Adding a New Source
1. Create extractor in `src/extractors/`
2. Output same JSON schema
3. Works with existing mapper/converter

## Error Handling

### Missing Fields
- Log warning
- Use default value if specified
- Skip field if no default

### Invalid Transformations
- Log error with context
- Show source value and target field
- Skip field or use raw value

### Validation
- Check required fields exist
- Verify data types match
- Ensure array indices don't exceed limits

## Performance Considerations

- **Caching**: Cache spell descriptions (shared across characters)
- **Lazy Loading**: Only load needed mapping sections
- **Batch Processing**: Support converting multiple characters
- **Parallel**: Process independent sections (spells, equipment) in parallel

## Testing Strategy

### Unit Tests
- Test each extractor independently
- Test mapper with sample data
- Test PDF utils with mock PDFs

### Integration Tests
- End-to-end with Neez's data
- Test all transformation functions
- Verify output PDF correctness

### Validation Tests
- Compare output with manual fill
- Check all fields populated
- Verify no data loss
