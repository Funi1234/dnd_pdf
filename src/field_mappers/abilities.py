"""
Ability Scores field mapper
Handles: STR, DEX, CON, INT, WIS, CHA (scores and modifiers)
"""


def map_abilities(char_data, fields, layout='combined'):
    """
    Map ability score fields

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
        layout: 'combined' for page 1, 'separate' for page 2
    """

    # Determine field suffix based on layout
    suffix = '' if layout == 'combined' else '-Alt'

    # Ability scores and modifiers
    abilities = {
        'Str': 'strength',
        'Dex': 'dexterity',
        'Con': 'constitution',
        'Int': 'intelligence',
        'Wis': 'wisdom',
        'Cha': 'charisma'
    }

    for short_name, long_name in abilities.items():
        ability_data = char_data['ability_scores'][long_name]
        fields[f'Front_{short_name} Score{suffix}'] = ability_data['score']
        fields[f'Front_{short_name} Mod{suffix}'] = ability_data['modifier']

    return fields
