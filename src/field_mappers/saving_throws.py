"""
Saving Throws field mapper
Handles: All 6 saving throws with proficiency markers
Note: Artificer has CON and INT proficiency
"""


def map_saving_throws(char_data, fields, layout='combined', proficient_abilities=None):
    """
    Map saving throw fields

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
        layout: 'combined' for page 1, 'separate' for page 2
        proficient_abilities: List of abilities with proficiency (e.g. ['con', 'int'])
    """

    if proficient_abilities is None:
        proficient_abilities = ['con', 'int']  # Default for Artificer

    # Determine field suffix based on layout
    suffix = '' if layout == 'combined' else '-Alt'

    # IMPORTANT: Artificer template has backwards naming!
    # Front_{Ability} Save Throw = value (text field)
    # Front_Save {Ability} = proficiency checkbox (button)

    abilities = {
        'Str': 'strength',
        'Dex': 'dexterity',
        'Con': 'constitution',
        'Int': 'intelligence',
        'Wis': 'wisdom',
        'Cha': 'charisma'
    }

    for short_name, long_name in abilities.items():
        # Fill the value
        fields[f'Front_{short_name} Save Throw{suffix}'] = char_data['saving_throws'][long_name]

        # Mark proficiency if applicable
        if long_name in proficient_abilities:
            fields[f'Front_Save {short_name}{suffix}'] = '/Yes'

    return fields
