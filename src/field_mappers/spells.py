"""
Spells field mapper
Handles: Layout-specific spell fields (if any)

Note: Most spell fields are in core.py since they're layout-independent
This module can handle layout-specific spell fields if needed in the future
"""


def map_spells(char_data, fields, layout='combined'):
    """
    Map spell-related fields that depend on layout

    Currently, most spell fields are layout-independent and handled by core.py
    This function is here for future layout-specific spell fields.

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate with field mappings
        layout: 'combined' for page 1, 'separate' for page 2
    """

    # Determine field suffix based on layout
    suffix = '' if layout == 'combined' else '-Alt'

    # Currently no layout-specific spell fields
    # Future: Could have spell preparation markers on page 1 vs page 2

    return fields
