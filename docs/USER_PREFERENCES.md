# User Preferences & Configuration Options

All configurable options for the character sheet converter.

## Configuration File

**Location**: `config/conversion_settings.yaml`

```yaml
# Character Sheet Layout Preferences
layout:
  # Which character sheet front page layout to use
  character_front: "combined"  # Options: "combined" | "separate"
  
spell_organization:
  # How to organize spells in the PDF
  layout: "by_level"  # Options: "single_page" | "by_level" | "auto"
  
  # Threshold for auto-decision (if layout: "auto")
  auto_split_threshold: 15  # If >15 spells, force by_level
  
  # Where to place cantrips when using by_level
  cantrip_placement: "dedicated"  # Options: "dedicated" | "with_first_level"

output:
  # Output directory for generated PDFs
  directory: "output/characters"
  
  # Naming pattern for output files
  filename_pattern: "{character_name}_{class}_{date}.pdf"
  
  # Keep temporary files for debugging?
  keep_temp_files: false

conversion:
  # Font size for spell descriptions
  spell_description_font_size: 8
  
  # Enable multiline for spell descriptions
  spell_description_multiline: true
  
  # Spell description max length before truncation
  spell_description_max_chars: 500  # 0 = no limit

debug:
  # Enable debug output
  verbose: false
  
  # Log file location
  log_file: "output/conversion.log"
```

---

## User Preferences

### 1. Character Sheet Layout

**Preference**: Which layout for the character sheet front page?

**Options**:

#### Combined (Default)
- **Page**: 1
- **Fields**: `Front_Character Name`, `Front_Str Score`, etc.
- **Style**: Skills in combined/compact layout
- **Best for**: Most users

#### Separate
- **Page**: 2  
- **Fields**: `Front_Character Name-Alt`, `Front_Str Score-Alt`, etc.
- **Style**: Skills in separate/expanded layout
- **Best for**: Users who prefer more visual space for skills

**CLI Flag**:
```bash
python convert_character.py character.json --layout combined
python convert_character.py character.json --layout separate
```

**Config**:
```yaml
layout:
  character_front: "combined"
```

---

### 2. Spell Organization

**Preference**: How to organize spells across pages?

**Options**:

#### Single Page
- **All spells on page 7** (spell metadata + entries combined)
- **When to use**: ≤15 total spells
- **Pros**: Compact, all visible at once
- **Cons**: Mixed levels, less room to grow

**Example**:
```
Page 7: Metadata + all spells
  - 3 cantrips
  - 5 level-1 spells
  - 4 level-2 spells
```

#### By Level (Default)
- **Each spell level gets its own page(s)**
- **When to use**: Any character (especially >15 spells)
- **Pros**: Organized, scalable, professional
- **Cons**: More pages (even if mostly empty)

**Example**:
```
Page 7: Spell metadata (DC, attack, slots)
Page 8: Cantrips (7 spells)
Pages 9-10: 1st level (24 spells across 2 pages)
Pages 11-12: 2nd level (28 spells across 2 pages)
```

#### Auto
- **Let converter decide** based on spell count
- **Logic**: 
  - If ≤10 spells → single_page
  - If >10 spells → by_level
  - If >15 spells → by_level (forced)

**CLI Flag**:
```bash
python convert_character.py character.json --spell-layout single-page
python convert_character.py character.json --spell-layout by-level
python convert_character.py character.json --spell-layout auto
```

**Config**:
```yaml
spell_organization:
  layout: "by_level"
  auto_split_threshold: 15
```

---

### 3. Cantrip Placement (when using By-Level)

**Preference**: Where to put cantrips when using by-level organization?

**Options**:

#### Dedicated Page (Default)
- Cantrips get their own page (page 8)
- Clean separation from leveled spells

#### With First Level
- Cantrips combined with 1st level spells on same page
- Saves a page for characters with few cantrips

**CLI Flag**:
```bash
python convert_character.py character.json --cantrip-placement dedicated
python convert_character.py character.json --cantrip-placement with-first
```

**Config**:
```yaml
spell_organization:
  cantrip_placement: "dedicated"
```

---

### 4. Output Options

**Filename Pattern**:
```yaml
output:
  filename_pattern: "{character_name}_{class}_{date}.pdf"
```

**Available Variables**:
- `{character_name}` - Character's name
- `{class}` - Character's class
- `{level}` - Character's level
- `{date}` - Current date (YYYY-MM-DD)
- `{timestamp}` - Full timestamp

**Examples**:
- `Neez_Artificer_2026-05-31.pdf`
- `Gandalf_Wizard_Level5.pdf`

---

### 5. Font & Formatting

**Spell Description Font Size**:
```yaml
conversion:
  spell_description_font_size: 8  # Range: 6-12
```

**Multiline Support**:
```yaml
conversion:
  spell_description_multiline: true
```

**Character Limit**:
```yaml
conversion:
  spell_description_max_chars: 500  # 0 = no limit
```

---

## CLI Override Priority

Command-line flags override config file settings:

1. **CLI flags** (highest priority)
2. **Config file** (`config/conversion_settings.yaml`)
3. **Defaults** (lowest priority)

**Example**:
```bash
# Config says "combined", CLI says "separate"
# Result: Uses "separate" (CLI wins)
python convert_character.py character.json --layout separate
```

---

## Recommended Presets

### Low-Level Character (Levels 1-4)
```yaml
layout:
  character_front: "combined"
spell_organization:
  layout: "auto"  # Will likely choose single_page
  auto_split_threshold: 10
```

### High-Level Character (Levels 5+)
```yaml
layout:
  character_front: "combined"
spell_organization:
  layout: "by_level"
  cantrip_placement: "dedicated"
```

### Compact/Minimal Pages
```yaml
layout:
  character_front: "combined"
spell_organization:
  layout: "single_page"
  cantrip_placement: "with_first_level"
```

### Maximum Organization
```yaml
layout:
  character_front: "separate"
spell_organization:
  layout: "by_level"
  cantrip_placement: "dedicated"
```

---

## Quick Reference

| Preference | Options | Default | CLI Flag |
|------------|---------|---------|----------|
| Character Layout | combined, separate | combined | `--layout` |
| Spell Organization | single-page, by-level, auto | by-level | `--spell-layout` |
| Cantrip Placement | dedicated, with-first | dedicated | `--cantrip-placement` |
| Output Directory | any path | output/characters | `--output` |
| Font Size | 6-12 | 8 | `--font-size` |

---

## Future Preferences (Planned)

- **Page size**: US Letter vs A4
- **Color scheme**: Color vs grayscale
- **Include spell descriptions**: Full vs abbreviated vs reference only
- **Equipment organization**: By category vs by weight
- **Feature formatting**: Compact vs detailed
- **Proficiency style**: Bubbles vs checkboxes

---

**See Also**:
- `docs/SPELL_LAYOUT_OPTIONS.md` - Detailed spell layout guide
- `IMPORTANT_DISCOVERIES.md` - Why these options exist
- `config/conversion_settings.yaml` - Example configuration
