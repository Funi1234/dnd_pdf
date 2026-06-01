"""
Character Info field mapper
Handles: Name, Race, Class, Level, Background, Alignment
"""


def map_character_info(char_data, fields, layout='combined'):
    """
    Map character information fields

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
        layout: 'combined' for page 1, 'separate' for page 2
    """

    # Determine field suffix based on layout
    suffix = '' if layout == 'combined' else '-Alt'

    # Basic character info
    fields[f'Front_Character Name{suffix}'] = char_data['character_info']['name']
    fields[f'Front_Race{suffix}'] = char_data['character_info']['race']
    fields[f'Front_Background{suffix}'] = char_data['character_info']['background']
    fields[f'Front_Alignment{suffix}'] = char_data['character_info']['alignment']

    # Parse "Artificer 5" into class and level
    class_level = char_data['character_info']['class_and_level']
    if ' ' in class_level:
        class_name, level = class_level.rsplit(' ', 1)
        fields[f'Front_Class{suffix}'] = class_name
        fields[f'Front_Level{suffix}'] = level

    # Specialist/Archetype (subclass)
    specialist = char_data['character_info'].get('specialist', '')
    if specialist:
        fields[f'Front_Archetype{suffix}'] = specialist

    # Racial traits (summary of key racial features)
    racial_traits = get_racial_traits(char_data)
    if racial_traits:
        fields[f'Front_Racial Traits{suffix}'] = racial_traits

    return fields


def get_racial_traits(char_data):
    """
    Get racial traits text based on race

    For now, this uses race-specific hardcoded traits.
    In the future, could extract from D&D Beyond data.

    Args:
        char_data: Character data dictionary

    Returns:
        str: Racial traits text
    """
    race = char_data['character_info']['race'].lower()

    # Gnome traits
    if 'gnome' in race:
        return "Darkvision 60 ft.\nGnome Cunning (Adv. on INT/WIS/CHA saves vs magic)\nSmall size"

    # Add other races as needed
    # elif 'elf' in race:
    #     return "Darkvision 60 ft.\nFey Ancestry\nTrance"

    # Default: return empty, user can fill manually
    return ""
