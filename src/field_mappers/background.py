"""
Background Page field mapper
Handles: Age, Height, Weight, Eyes, Skin, Hair, Background
Personality Traits, Ideals, Bonds, Flaws
Supports both regular and sidekick background pages
"""


def find_paragraph_break(text, target_length):
    """
    Find a good paragraph break near the target length

    Args:
        text: Text to split
        target_length: Target character count

    Returns:
        int: Index to break at (on paragraph boundary)
    """
    if len(text) <= target_length:
        return len(text)

    # Look for double newline (paragraph break) near the target
    search_start = max(0, target_length - 200)
    search_end = min(len(text), target_length + 200)

    # Find all paragraph breaks in the search window
    para_breaks = []
    for i in range(search_start, search_end - 1):
        if text[i:i+2] == '\n\n':
            para_breaks.append(i + 2)  # Include the newlines in first section

    if para_breaks:
        # Choose the break closest to target
        return min(para_breaks, key=lambda x: abs(x - target_length))

    # No paragraph break found, look for single newline
    for i in range(search_start, search_end):
        if text[i] == '\n':
            return i + 1

    # Fall back to target length
    return target_length


def map_background(char_data, fields, background_page='regular', template_type='class'):
    """
    Map background page fields (physical traits, appearance)

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
        background_page: 'regular' for standard background, 'sidekick' for sidekick page
        template_type: 'class' for class templates (Back_ prefix), 'generic' for D&D Beyond templates (no prefix)
    """

    # Determine field suffix and prefix based on template type
    if template_type == 'generic':
        # Generic D&D Beyond templates (background_regular.pdf)
        prefix = ''
        suffix = ''
    else:
        # Class-specific templates (Artificer, Cleric, etc.)
        prefix = 'Back_'
        suffix = '' if background_page == 'regular' else '-SK'

    # Get physical traits and personality
    physical_traits = char_data.get('physical_traits', {})
    personality = char_data.get('personality', {})

    # Character name
    if template_type == 'generic':
        fields['CharacterName4'] = char_data['character_info']['name']
    else:
        fields[f'{prefix}Character Name{suffix}'] = char_data['character_info']['name']

    # Physical traits
    fields[f'{prefix}AGE{suffix}'] = physical_traits.get('age', '') if template_type == 'generic' else physical_traits.get('age', '')
    fields[f'{prefix}HEIGHT{suffix}'] = physical_traits.get('height', '') if template_type == 'generic' else physical_traits.get('height', '')
    fields[f'{prefix}WEIGHT{suffix}'] = physical_traits.get('weight', '') if template_type == 'generic' else physical_traits.get('weight', '')
    fields[f'{prefix}EYES{suffix}'] = physical_traits.get('eyes', '') if template_type == 'generic' else physical_traits.get('eyes', '')
    fields[f'{prefix}SKIN{suffix}'] = physical_traits.get('skin', '') if template_type == 'generic' else physical_traits.get('skin', '')
    fields[f'{prefix}HAIR{suffix}'] = physical_traits.get('hair', '') if template_type == 'generic' else physical_traits.get('hair', '')

    # Alignment
    fields[f'{prefix}ALIGNMENT{suffix}'] = char_data['character_info'].get('alignment', '') if template_type == 'generic' else char_data['character_info'].get('alignment', '')

    # Background (not on generic template)
    if template_type != 'generic':
        fields[f'{prefix}Background{suffix}'] = char_data['character_info'].get('background', '')

    # Personality traits
    fields[f'{prefix}PersonalityTraits {suffix}'] = personality.get('personality_traits', '')
    fields[f'{prefix}Ideals{suffix}'] = personality.get('ideals', '')
    fields[f'{prefix}Bonds{suffix}'] = personality.get('bonds', '')
    fields[f'{prefix}Flaws{suffix}'] = personality.get('flaws', '')

    # Backstory (long narrative - split across multiple fields if needed)
    if template_type == 'generic':
        backstory = personality.get('backstory', '')
        if backstory:
            # Split on newline AFTER 1500 chars for cleaner breaks

            if len(backstory) <= 1500:
                fields['Backstory'] = backstory
            else:
                # Find first newline after 1500 chars
                break1 = backstory.find('\n', 1500)
                if break1 == -1:
                    # No newline found, split at 1500
                    break1 = 1500
                else:
                    break1 += 1  # Include the newline

                fields['Backstory'] = backstory[:break1]
                remainder = backstory[break1:].strip()

                # Split remainder between AdditionalNotes1 and AdditionalNotes2
                if len(remainder) <= 1500:
                    fields['AdditionalNotes1'] = remainder
                else:
                    # Find first newline after 1500 chars in remainder
                    break2 = remainder.find('\n', 1500)
                    if break2 == -1:
                        break2 = 1500
                    else:
                        break2 += 1

                    fields['AdditionalNotes1'] = remainder[:break2]
                    fields['AdditionalNotes2'] = remainder[break2:].strip()

    # Appearance (long description - only on generic template)
    if template_type == 'generic':
        fields['Appearance'] = physical_traits.get('appearance', '')

    # Distinguishing Marks and Scars are template-only (not in D&D Beyond)
    # Users can fill these manually

    return fields
