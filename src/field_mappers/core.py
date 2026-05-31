"""
Core field mapper
Handles fields that appear on BOTH page layouts or are layout-independent
Examples: Spell DC/Attack (on page 7), Spell Slots (on page 7)
"""


def map_core_fields(char_data, fields):
    """
    Map core fields that don't depend on layout choice

    These fields are the same regardless of whether user picks
    page 1 (combined) or page 2 (separate) layout.

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
    """

    # Spell DC and Attack Bonus (page 7 - no layout suffix)
    fields['SpellSheet 1_Spell DC'] = char_data['spellcasting']['spell_save_dc']
    fields['SpellSheet 1_Spell Atk'] = char_data['spellcasting']['spell_attack_bonus']

    # Spell slots for level 5 Artificer: 4×1st, 2×2nd (page 7 - no layout suffix)
    fields['SpellSheet1_Spell Slot 1st 1'] = '/Yes'
    fields['SpellSheet1_Spell Slot 1st 2'] = '/Yes'
    fields['SpellSheet1_Spell Slot 1st 3'] = '/Yes'
    fields['SpellSheet1_Spell Slot 1st 4'] = '/Yes'

    fields['SpellSheet1_Spell Slot 2nd 1'] = '/Yes'
    fields['SpellSheet1_Spell Slot 2nd 2'] = '/Yes'

    # Cantrips on page 8 (uses -Alt suffix but independent of page 1/2 choice)
    map_cantrips(char_data, fields)

    return fields


def map_cantrips(char_data, fields):
    """
    Map cantrips to page 8 spell slots (01-12)

    Page 8 always uses -Alt suffix regardless of page 1/2 layout choice.

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
    """

    spells = char_data['spells']

    # Filter cantrips (based on header markers in spell list)
    cantrips = []
    in_cantrips = False

    for spell in spells:
        if spell['name'] == '=== CANTRIPS ===':
            in_cantrips = True
            continue
        elif '===' in spell['name']:  # Hit another header
            in_cantrips = False
            continue

        if in_cantrips:
            cantrips.append(spell)

    # Fill page 8 with cantrips (slots 01-12)
    for i, spell in enumerate(cantrips[:12], 1):  # Max 12 slots
        idx = f"{i:02d}"

        fields[f'SpellSheet1_Spell Name {idx}-Alt'] = spell['name']
        fields[f'SpellSheet1_Spell School {idx}-Alt'] = spell.get('notes', '')
        fields[f'SpellSheet1_Range {idx}-Alt'] = spell['range']
        fields[f'SpellSheet1_Casting Time {idx}-Alt'] = spell['casting_time']
        fields[f'SpellSheet1_Duration {idx}-Alt'] = spell['duration']

        # Components (checkboxes need /Yes)
        components = spell.get('components', '')
        if 'V' in components:
            fields[f'SpellSheet1_Verbal {idx}-Alt'] = '/Yes'
        if 'S' in components:
            fields[f'SpellSheet1_Somatic {idx}-Alt'] = '/Yes'
        if 'M' in components:
            fields[f'SpellSheet1_Material {idx}-Alt'] = '/Yes'

        # Prepared marker (checkbox needs /Yes)
        if spell.get('prepared') == 'O':
            fields[f'SpellSheet1_Prepared {idx}-Alt'] = '/Yes'

    return fields
