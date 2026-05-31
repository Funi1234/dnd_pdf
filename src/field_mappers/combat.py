"""
Combat Stats field mapper
Handles: AC, HP, Initiative, Speed, Proficiency Bonus, Passive scores, Hit Dice
"""


def map_combat(char_data, fields, layout='combined', level=5):
    """
    Map combat-related fields

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
        layout: 'combined' for page 1, 'separate' for page 2
        level: Character level (for calculating proficiency bonus and hit dice)
    """

    # Determine field suffix based on layout
    suffix = '' if layout == 'combined' else '-Alt'

    # Basic combat stats
    fields[f'Front_AC{suffix}'] = char_data['combat']['armor_class']
    fields[f'Front_Initiative{suffix}'] = char_data['combat']['initiative']
    fields[f'Front_Speed{suffix}'] = char_data['combat']['speed']

    # Proficiency bonus (calculated from level)
    proficiency_bonus = calculate_proficiency_bonus(level)
    fields[f'Front_Proficiency{suffix}'] = f'+{proficiency_bonus}'

    # Passive scores
    fields[f'Front_Passive Perception{suffix}'] = char_data['combat']['passive_perception']
    fields[f'Front_Passive Insight{suffix}'] = char_data['combat']['passive_insight']

    # Hit Points
    fields[f'Front_Max HP{suffix}'] = '40'  # TODO: Get from char_data when available
    # Current HP and Temp HP - leave blank for user to fill at the table

    # Hit Dice - Just the count, not the die type
    fields[f'Front_Total Hit Dice{suffix}'] = str(level)
    # Used Hit Dice - leave blank for user to fill

    # Try to fill spell attack/DC on page 1 (different field names per class)
    # Standard classes (Cleric/Wizard/etc): Front_Spell DC, Front_Spell Atk
    # Artificer has weird names: Front_Spells Known (DC), Front_Cantrips Known (atk)
    # BUT: Don't fill Front_Cantrips Known - it means different things per class!

    # Standard spell DC/Attack fields
    fields[f'Front_Spell DC{suffix}'] = char_data['spellcasting']['spell_save_dc']
    fields[f'Front_Spell Atk{suffix}'] = char_data['spellcasting']['spell_attack_bonus']

    # Artificer-specific weird names (only fill Spells Known, not Cantrips Known)
    fields[f'Front_Spells Known{suffix}'] = char_data['spellcasting']['spell_save_dc']
    # NOT filling Front_Cantrips Known - means different things for different classes

    return fields


def calculate_proficiency_bonus(level):
    """Calculate proficiency bonus from character level"""
    if level <= 4:
        return 2
    elif level <= 8:
        return 3
    elif level <= 12:
        return 4
    elif level <= 16:
        return 5
    else:
        return 6
