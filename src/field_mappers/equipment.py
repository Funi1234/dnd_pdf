"""
Equipment & Features field mapper
Handles com_feat_equip pages with overflow
"""


def map_equipment(char_data, fields, page_offset=0):
    """
    Map equipment and features to com_feat_equip template

    Main page: FeaturesTraits1-3, Eq Name/Qty/Weight 0-25 (26 slots)
    Additional: FeaturesTraits4-6, Eq Name/Qty/Weight 26-55 (30 slots)

    Args:
        char_data: Character data dictionary
        fields: Dictionary to populate
        page_offset: 0 = main, 1 = additional page 1, etc.
    """
    equipment = char_data.get('equipment', [])
    features = char_data.get('features', [])

    # Determine field ranges based on page
    if page_offset == 0:
        # Main page
        feature_start = 1
        eq_start = 0
        eq_count = 26
    else:
        # Additional pages
        feature_start = 1 + (page_offset * 3)
        eq_start = 26 + ((page_offset - 1) * 30)
        eq_count = 30

    # Fill features (3 per page)
    for i in range(3):
        feat_idx = (page_offset * 3) + i
        if feat_idx < len(features):
            field_num = feature_start + i
            fields[f'FeaturesTraits{field_num}'] = features[feat_idx]

    # Fill equipment
    for i in range(eq_count):
        eq_idx = eq_start + i
        if eq_idx < len(equipment):
            item = equipment[eq_idx]
            fields[f'Eq Name{eq_start + i}'] = item.get('name', '')
            fields[f'Eq Qty{eq_start + i}'] = item.get('quantity', '')
            fields[f'Eq Weight{eq_start + i}'] = item.get('weight', '')

    return fields


def calculate_equipment_pages_needed(char_data):
    """
    Calculate how many equipment pages needed

    Returns list of page_offset values
    Example: [0] for main only, [0, 1] for main + 1 additional
    """
    equipment = char_data.get('equipment', [])
    features = char_data.get('features', [])

    # Main page holds 26 equipment + 3 features
    # Additional pages hold 30 equipment + 3 features each

    pages_needed = [0]  # Always need main page

    # Check if need additional pages
    eq_overflow = max(0, len(equipment) - 26)
    feat_overflow = max(0, len(features) - 3)

    # Calculate additional pages needed
    additional_pages = 0

    if eq_overflow > 0 or feat_overflow > 0:
        # Each additional page holds 30 eq + 3 features
        eq_pages = (eq_overflow + 29) // 30  # Ceiling division
        feat_pages = (feat_overflow + 2) // 3

        additional_pages = max(eq_pages, feat_pages)

    for i in range(1, additional_pages + 1):
        pages_needed.append(i)

    return pages_needed
