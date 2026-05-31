"""
Skills field mapper
Handles: All 18 skills with bonuses and proficiency markers
"""


def map_skills(char_data, fields, layout='combined'):
    """
    Map skill fields

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
        layout: 'combined' for page 1, 'separate' for page 2
    """

    # Determine field suffix based on layout
    suffix = '' if layout == 'combined' else '-Alt'

    # Mapping from our data keys to Artificer template field names
    skill_mapping = {
        'acrobatics': 'Acrobatics',
        'animal': 'Animal Handling',
        'arcana': 'Arcana',
        'athletics': 'Athletics',
        'deception': 'Deception',
        'history': 'History',
        'insight': 'Insight',
        'intimidation': 'Intimidation',
        'investigation': 'Investigation',
        'medicine': 'Medicine',
        'nature': 'Nature',
        'perception': 'Perception',
        'performance': 'Performance',
        'persuasion': 'Persuasion',
        'religion': 'Religion',
        'sleight': 'Sleight of Hand',
        'stealth': 'Stealth',
        'survival': 'Survival'
    }

    for skill_key, skill_name in skill_mapping.items():
        if skill_key in char_data['skills']:
            skill_data = char_data['skills'][skill_key]

            # Fill bonus value
            fields[f'Front_Skill {skill_name}{suffix}'] = skill_data['bonus']

            # Mark proficiency (checkboxes need /Yes format)
            if skill_data['proficiency'] == 'P':
                fields[f'Front_Proficiency {skill_name}{suffix}'] = '/Yes'

            # Note: Expertise would be marked with:
            # fields[f'Front_Expertise {skill_name}{suffix}'] = '/Yes'

    return fields
