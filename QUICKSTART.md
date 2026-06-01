# Quick Start Guide

## Setup (one-time)

```bash
cd ~/coding/dnd_pdf
python3 -m venv venv
source venv/bin/activate
pip install pypdf
```

## Generate Character Sheet

```bash
cd ~/coding/dnd_pdf
source venv/bin/activate
python3 scripts/generate_character_sheet.py
```

Output: `output/Neez-Artificer_COMPLETE.pdf`

## Project Structure

```
~/coding/dnd_pdf/
├── config/
│   └── paths.json           # Configure file paths
├── src/
│   ├── pdf_utils.py         # PDF manipulation utilities
│   └── spell_extractor.py   # Spell description extraction
├── scripts/
│   └── generate_character_sheet.py  # Main script
├── output/
│   └── Neez-Artificer_COMPLETE.pdf  # Generated PDF
└── venv/                    # Python virtual environment
```

## Next Steps

1. ✅ Spell data extraction - DONE
2. ✅ Spell sheet generation - DONE
3. ⏳ Character data filling - TODO

Create `scripts/fill_character_data.py` to fill:
- Character name
- Ability scores
- AC, HP, speed
- Skills, saves
- Equipment
- Features
