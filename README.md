# D&D Beyond → Class-Specific PDF Converter

Automated tool for converting D&D Beyond character sheets into class-specific fillable PDFs with full character data mapping.

## Status

**Early Development** - Currently supports Artificer class with 82+ fields mapped.

## Features

- ✅ **Modular Architecture**: Separate mappers for each character section (abilities, skills, combat, etc.)
- ✅ **Dual Layout Support**: Works with both 'combined' (page 1) and 'separate' (page 2) character sheet layouts
- ✅ **Smart Font Sizing**: Auto-adjusts font sizes with overflow support
- ✅ **Configurable Weapons**: Select which weapons to display when you have more than 3

## Currently Mapped Fields

- Character Info: Name, Race, Class, Level, Background, Alignment
- Ability Scores: All 6 abilities with modifiers
- Skills: All 18 skills with bonuses and proficiency markers
- Saving Throws: All 6 saves with proficiency indicators
- Combat: AC, HP, Initiative, Speed, Proficiency Bonus, Passive Perception/Insight, Hit Dice
- Proficiencies: Languages, Tools, Armor, Weapons (with checkboxes)
- Weapons: 3 weapon attack slots (Name, Attack Bonus, Damage/Type)
- Spells: Spell DC, Spell Attack, Spell Slots, Cantrips
- Racial Traits: Key racial features

## Requirements

- Python 3.8+
- pypdf library

## Setup

```bash
git clone https://github.com/Funi1234/dnd_pdf.git
cd dnd_pdf

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install pypdf
```

## Known Issues

### Artificer Template Field Names
The Artificer template has confusingly named fields:

- `Front_Cantrips Known` = Spell Attack Bonus (NOT cantrips!)
- `Front_Spells Known` = Spell Save DC (NOT spells known!)
- `Front_Save {Ability}` = Proficiency checkbox
- `Front_{Ability} Save Throw` = Save bonus value (backwards!)

See `CLAUDE.md` for complete documentation.

### PDF Viewing
- **Brave Browser**: Renders form fields correctly ✅
- **macOS Preview**: May not display all fields correctly ⚠️

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Acknowledgments

- Built with [pypdf](https://github.com/py-pdf/pypdf)
- Class-specific character sheet templates from [Class Character Sheets - The Bundle](https://www.dmsguild.com/en/product/232835/class-character-sheets-the-bundle) on DMs Guild
- Character data from D&D Beyond character sheets

## Disclaimer

This tool is for personal use only. D&D Beyond and Dungeons & Dragons are property of Wizards of the Coast. Class character sheet templates are from DMs Guild and retain their original licensing. This project is not affiliated with or endorsed by Wizards of the Coast or DMs Guild.
