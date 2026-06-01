# Field Extraction Explained

Understanding the difference between extracting **field definitions** vs **field values**.

## Two Types of Extraction

### 1. Field Definitions (What We Have) ✅

**From**: Empty template PDF
**Extracts**: Field structure and metadata
**Purpose**: Understanding what fields exist and where

**Example Output**:
```json
{
  "Front_Character Name": {
    "type": "/Tx",
    "default_value": "",
    "page": 1
  },
  "Front_AC": {
    "type": "/Tx",
    "default_value": "",
    "page": 1
  },
  "Front_Str Score": {
    "type": "/Tx",
    "default_value": "",
    "page": 1
  }
}
```

**What it tells us**:
- ✅ Field names
- ✅ Field types (/Tx = text, /Btn = checkbox)
- ✅ Default values (usually empty)
- ✅ Which page each field is on

**What it DOESN'T tell us**:
- ❌ Character data
- ❌ Filled values
- ❌ What the character is

---

### 2. Field Values (What We Need for Source Data) ❌

**From**: Filled PDF (like a filled D&D Beyond sheet)
**Extracts**: Actual character data
**Purpose**: Getting character information to convert

**Example Output**:
```json
{
  "Front_Character Name": {
    "type": "/Tx",
    "value": "Ebenezer 'Neez' Tivonhoop"
  },
  "Front_AC": {
    "type": "/Tx", 
    "value": "19"
  },
  "Front_Str Score": {
    "type": "/Tx",
    "value": "8"
  }
}
```

**What it tells us**:
- ✅ Character's name
- ✅ Character's AC
- ✅ Character's ability scores
- ✅ All filled data ready to convert

---

## What We Currently Have

### Artificer Template - Field Definitions ✅

**Files**:
- `data/pdf_field_definitions.json`
- `data/artificer_fields_by_page.json`
- `data/artificer_fields_structured.json`

**Content**:
```json
{
  "metadata": {
    "total_fields": 865
  },
  "pages": {
    "page_1": {
      "categories": {
        "character_info": {
          "fields": [
            {
              "field_name": "Front_Character Name",
              "type": "/Tx",
              "default": ""  ← EMPTY
            }
          ]
        }
      }
    }
  }
}
```

**This is the TARGET** - we know where to PUT data

---

## What We Still Need

### D&D Beyond - Field Values ❌

**Need**: Character data from a filled D&D Beyond sheet

**Want to Extract**:
```json
{
  "character": {
    "name": "Ebenezer 'Neez' Tivonhoop",
    "race": "Gnome",
    "class": "Artificer",
    "level": 5
  },
  "abilities": {
    "strength": {"score": 8, "modifier": -1},
    "dexterity": {"score": 14, "modifier": 2},
    "intelligence": {"score": 20, "modifier": 5}
  },
  "combat": {
    "ac": 19,
    "hp_max": 35,
    "initiative": 2
  }
}
```

**This is the SOURCE** - the data we want to convert

---

## The Extraction Process

### If We Had a FILLABLE D&D Beyond PDF

**Process would be**:
```python
from pypdf import PdfReader

reader = PdfReader("dndbeyond_filled.pdf")
fields = reader.get_fields()

character_data = {}
for field_name, field_obj in fields.items():
    value = field_obj.get('/V', '')  # ← Gets the FILLED value
    character_data[field_name] = value

# Result:
{
  "CharName": "Ebenezer 'Neez' Tivonhoop",
  "AC": "19",
  "STR": "8",
  ...
}
```

**Then we'd have**:
- ✅ Source data (D&D Beyond values)
- ✅ Target structure (Artificer field names)
- ✅ Ready to build mappings!

---

### BUT: D&D Beyond PDFs Are Flattened

**Problem**: Neez-1.pdf has NO form fields

```python
reader = PdfReader("Neez-1.pdf")
fields = reader.get_fields()

print(fields)
# → None or {} (empty!)
```

**Why**: D&D Beyond "flattens" PDFs when exporting
- Form field values are baked into the visual layer
- No extractable `/V` values
- Just images/text on the page

**This is why we're blocked!**

---

## Solutions

### Option 1: Manual JSON Creation (Current Plan)

**Process**:
1. Open Neez-1.pdf
2. Read each field visually
3. Type into JSON manually

**Output**:
```json
{
  "character": {
    "name": "Ebenezer 'Neez' Tivonhoop",  ← Read from PDF, typed manually
    "race": "Gnome",                      ← Read from PDF, typed manually
    "level": 5                            ← Read from PDF, typed manually
  }
}
```

**Pros**: Fast to start, 100% accurate
**Cons**: Manual work, only works for Neez

---

### Option 2: OCR Extraction (Future)

**Process**:
1. OCR the PDF → raw text
2. Parse text for patterns
3. Extract values automatically

**Example**:
```
Text found: "Character Name: Ebenezer 'Neez' Tivonhoop"
Pattern: "Character Name: (.*)"
Extracted: "Ebenezer 'Neez' Tivonhoop"
```

**Pros**: Automated, works for any character
**Cons**: Complex, errors possible, layout-dependent

---

### Option 3: D&D Beyond API (If It Exists)

**Process**:
1. Call D&D Beyond API
2. Get JSON directly
3. Transform to our schema

**Example**:
```bash
curl https://api.dndbeyond.com/character/12345
```

**Response**:
```json
{
  "name": "Ebenezer 'Neez' Tivonhoop",
  "race": {"name": "Gnome"},
  "classes": [{"name": "Artificer", "level": 5}],
  "stats": {"strength": 8}
}
```

**Pros**: Perfect data, automated
**Cons**: Might not exist or be accessible

---

## Running Extraction Scripts

### What Would Happen Right Now

```bash
# On EMPTY Artificer template
python scripts/extract_fields_by_page.py
# Result: Field definitions (what we have) ✅

# On FILLED D&D Beyond PDF
python scripts/extract_dnd_beyond.py neez-1.pdf
# Result: ERROR - no form fields found ❌
```

### What We WANT to Build

```bash
# Extract from any filled PDF (if it has fields)
python scripts/extract_field_values.py filled_character.pdf
# Result: Character data JSON ✅

# Extract from flattened PDF (using OCR)
python scripts/extract_from_flattened.py neez-1.pdf
# Result: Character data JSON (automated) ✅
```

---

## Summary

**Question**: "If we ran field extraction on the Artificer PDF, would we get similar JSON?"

**Answer**: 

**What we have now** (field definitions):
```json
{
  "Front_Character Name": {
    "type": "/Tx",
    "default": ""  ← No data
  }
}
```

**What we'd get from FILLED PDF** (field values):
```json
{
  "Front_Character Name": {
    "type": "/Tx",
    "value": "Ebenezer 'Neez' Tivonhoop"  ← HAS data!
  }
}
```

**The difference**:
- **Empty template** → Field structure (TARGET)
- **Filled PDF** → Character data (SOURCE)

We have the TARGET, we need the SOURCE!

---

**Next Step**: Create `neez_dndbeyond.json` manually by reading Neez-1.pdf visually, then we can start building mappings!
