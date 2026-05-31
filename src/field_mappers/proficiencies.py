"""
Proficiencies field mapper
Handles: Languages, Tools, Armor, Weapons, Other Proficiencies
"""


def map_proficiencies(char_data, fields, layout='combined'):
    """
    Map proficiency fields (languages, tools, armor, weapons)

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
        layout: 'combined' for page 1, 'separate' for page 2
    """

    # Determine field suffix based on layout
    suffix = '' if layout == 'combined' else '-Alt'

    # Get proficiency data from raw fields if available
    # D&D Beyond stores all proficiencies in one big text field
    prof_text = get_proficiency_text(char_data)

    # Parse out the different sections
    languages = extract_section(prof_text, 'LANGUAGES')
    tools = extract_section(prof_text, 'TOOLS')

    # Armor and weapons are typically implicit for the class
    # but we could extract them too if needed
    armor = extract_section(prof_text, 'ARMOR')
    weapons = extract_section(prof_text, 'WEAPONS')

    # Fill the fields
    fields[f'Front_Languages{suffix}'] = languages
    fields[f'Front_Tools{suffix}'] = tools

    # Armor proficiency checkboxes
    if 'light armor' in armor.lower():
        fields[f'Front_Light Armour{suffix}'] = '/Yes'
    if 'medium armor' in armor.lower():
        fields[f'Front_Medium Armour{suffix}'] = '/Yes'
    if 'heavy armor' in armor.lower():
        fields[f'Front_Heavy Armour{suffix}'] = '/Yes'

    # Weapon proficiency checkboxes
    if 'simple weapon' in weapons.lower():
        fields[f'Front_Simple Weapons{suffix}'] = '/Yes'
    if 'martial weapon' in weapons.lower():
        fields[f'Front_Martial Weapons{suffix}'] = '/Yes'

    # Shield proficiency checkbox
    if 'shield' in armor.lower():
        fields[f'Front_Shields{suffix}'] = '/Yes'

    return fields


def get_proficiency_text(char_data):
    """
    Get the proficiency text from character data

    Args:
        char_data: Character data dictionary

    Returns:
        str: Proficiency text or empty string
    """
    # Check if we have proficiencies in the character data
    # This might be in different places depending on extraction
    if 'proficiencies' in char_data:
        return char_data['proficiencies']

    # For now, return a placeholder - we'll need to get this from raw data
    # TODO: Add proficiencies to the clean character data extraction
    return ""


def extract_section(text, section_name):
    """
    Extract a specific section from the proficiency text

    Example text format:
    === ARMOR ===
    Light Armor, Medium Armor, Shields

    === WEAPONS ===
    Simple Weapons

    === TOOLS ===
    Thieves' Tools, Tinker's Tools

    === LANGUAGES ===
    Common, Gnomish

    Args:
        text: Full proficiency text
        section_name: Section to extract (e.g., 'LANGUAGES', 'TOOLS')

    Returns:
        str: Comma-separated items from that section
    """
    if not text:
        return ''

    # Find the section header
    section_marker = f'=== {section_name.upper()} ==='

    if section_marker not in text:
        return ''

    # Split by sections
    parts = text.split('===')

    # Find our section
    for i, part in enumerate(parts):
        if section_name.upper() in part:
            # Get the content after this header (next part)
            if i + 1 < len(parts):
                # Content is between this header and the next
                content = parts[i + 1].strip()
                # Remove any newlines and extra spaces
                content = ' '.join(content.split())
                return content
            break

    return ''
