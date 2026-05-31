"""
Weapons field mapper
Handles: Weapon Name, Attack Bonus, Damage/Type (3 weapon slots)
"""


def map_weapons(char_data, fields, layout='combined'):
    """
    Map weapon attack fields

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
        layout: 'combined' for page 1, 'separate' for page 2
    """

    # Determine field suffix based on layout
    suffix = '' if layout == 'combined' else '-Alt'

    # Get weapon data if available
    weapons = get_weapon_data(char_data)

    # Fill up to 3 weapon slots
    for i, weapon in enumerate(weapons[:3], 1):
        fields[f'Front_Weapon Name {i}{suffix}'] = weapon['name']
        fields[f'Front_Weapon Atk Bonus {i}{suffix}'] = weapon['attack_bonus']
        fields[f'Front_Weapon Damage {i}{suffix}'] = weapon['damage']

    return fields


def get_weapon_data(char_data):
    """
    Get weapon data from character data

    Returns a list of weapon dictionaries with name, attack_bonus, damage

    Args:
        char_data: Character data dictionary

    Returns:
        list: List of weapon dicts
    """
    # Check if we have weapons in the character data
    if 'weapons' in char_data:
        return char_data['weapons']

    # Default: return empty list
    # TODO: Extract weapons from raw data and add to clean character data
    return []
