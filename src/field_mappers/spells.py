"""
Spells field mapper
Fills spell sheet pages (12 spells per page, split by level)
"""

import re
from src.spell_lookup import lookup_spell


def map_spells(char_data, fields, layout='combined', level_filter=None, page_offset=0, template_type='main'):
    """
    Map spell names to spell sheet template (12 slots per page)

    Multi-page strategy:
    - Page 1 (spells_main): Cantrips only (level 0)
    - Page 2+: Level 1 spells (12 per page)
    - Next pages: Level 2 spells (12 per page)
    - Each level starts new page, no mixing

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
        layout: Not used for spell sheet
        level_filter: Spell level to show ('0', '1', '2', etc.) or None for all
        page_offset: Which page of this level (0 = first 12, 1 = next 12, etc.)
        template_type: 'main' or 'additional' (determines -Alt suffix)
    """
    spells = char_data.get('spells', [])

    if not spells:
        return fields

    # Determine suffix based on template type
    suffix = '-Alt' if template_type == 'additional' else ''

    # Filter by level if specified
    if level_filter is not None:
        spells_filtered = [s for s in spells if s.get('level') == str(level_filter)]
    else:
        spells_filtered = spells

    # Apply pagination (12 per page)
    start_idx = page_offset * 12
    end_idx = start_idx + 12
    page_spells = spells_filtered[start_idx:end_idx]

    # Fill spell counts & stats (only on first page / cantrip page)
    # NOTE: Front page spell DC/attack handled by combat.py (backwards field names!)
    if page_offset == 0 and level_filter in [None, '0']:
        cantrips = [s for s in spells if s.get('level') == '0']

        # Calculate spells known for Artificer: INT mod + half level
        # Get INT modifier from ability scores
        int_mod = int(char_data.get('ability_scores', {}).get('intelligence', {}).get('modifier', '+0').replace('+', ''))

        # Get level from class_and_level
        class_level = char_data['character_info']['class_and_level']
        level = int(class_level.rsplit(' ', 1)[1]) if ' ' in class_level else 5

        spells_known = int_mod + (level // 2)

        # Fill spell sheet page counts (NOT front page - those are backwards!)
        fields[f'SpellSheet 1_Cantrips Known{suffix}'] = str(len(cantrips))
        fields[f'SpellSheet 1_Spells Known{suffix}'] = str(spells_known)

        # Fill spell DC and attack bonus on spell sheets
        spellcasting = char_data.get('spellcasting', {})
        if spellcasting:
            fields[f'SpellSheet 1_Spell DC{suffix}'] = spellcasting.get('spell_save_dc', '')
            fields[f'SpellSheet 1_Spell Atk{suffix}'] = spellcasting.get('spell_attack_bonus', '')

    # Fill spell slots (1-12) with full details from lookup
    for i, spell in enumerate(page_spells, 1):
        spell_name = spell['name']

        # Check for ritual marker [R] and strip it
        is_ritual = '[R]' in spell_name
        clean_name = spell_name.replace(' [R]', '').replace('[R]', '').strip()

        fields[f'SpellSheet1_Spell Name {i:02d}{suffix}'] = clean_name
        fields[f'SpellSheet 1_Spells Level {i:02d}{suffix}'] = spell.get('level', '')

        # Mark prepared
        if spell.get('level') == '0' or spell.get('prepared') == 'P':
            fields[f'SpellSheet1_Prepared {i:02d}{suffix}'] = '/Yes'

        # Mark ritual
        if is_ritual:
            fields[f'SpellSheet1_Ritual {i:02d}{suffix}'] = '/Yes'

        # Lookup full spell details (use clean name)
        details = lookup_spell(clean_name)
        if details:
            fields[f'SpellSheet1_Spell School {i:02d}{suffix}'] = details.get('school', '')
            fields[f'SpellSheet1_Range {i:02d}{suffix}'] = details.get('range', '')
            fields[f'SpellSheet1_Casting Time {i:02d}{suffix}'] = details.get('casting_time', '')
            fields[f'SpellSheet1_Duration {i:02d}{suffix}'] = details.get('duration', '')

            # Clean Obsidian markdown from description ([[links]], `dice:` syntax)
            description = details.get('description', '')
            description = re.sub(r'\[\[([^\]]+)\]\]', r'\1', description)  # [[link]] -> link
            description = re.sub(r'`dice:\s*([^`]+)`', r'\1', description)  # `dice: 2d4` -> 2d4
            fields[f'SpellSheet1_Spell Effect {i:02d}{suffix}'] = description

            # Parse components (V, S, M)
            components = details.get('components', '')
            if 'V' in components:
                fields[f'SpellSheet1_Verbal {i:02d}{suffix}'] = '/Yes'
            if 'S' in components:
                fields[f'SpellSheet1_Somatic {i:02d}{suffix}'] = '/Yes'
            if 'M' in components:
                fields[f'SpellSheet1_Material {i:02d}{suffix}'] = '/Yes'
                # Extract material component text (in parentheses)
                material_match = re.search(r'M \((.+?)\)', components)
                if material_match:
                    fields[f'SpellSheet1_Components {i:02d}{suffix}'] = material_match.group(1)

            # Check for concentration/ritual in duration
            if 'concentration' in details.get('duration', '').lower():
                fields[f'SpellSheet1_Concentration {i:02d}{suffix}'] = '/Yes'

    return fields


def calculate_spell_pages_needed(char_data):
    """
    Calculate how many spell sheet pages needed

    Returns list of (template, level, page_offset) tuples
    Example: [('spells_main', '0', 0), ('spells_additional', '1', 0), ('spells_additional', '1', 1)]
    """
    spells = char_data.get('spells', [])
    if not spells:
        return [('spells_main', '0', 0)]  # Empty cantrip page

    pages = []

    # Group spells by level
    by_level = {}
    for spell in spells:
        level = spell.get('level', '0')
        if level not in by_level:
            by_level[level] = []
        by_level[level].append(spell)

    # Sort levels (cantrips first)
    sorted_levels = sorted(by_level.keys(), key=lambda x: int(x) if x.isdigit() else 99)

    for level in sorted_levels:
        level_spells = by_level[level]
        num_pages = (len(level_spells) + 11) // 12  # Ceiling division

        for page_idx in range(num_pages):
            template = 'spells_main' if level == '0' and page_idx == 0 else 'spells_additional'
            pages.append((template, level, page_idx))

    return pages
