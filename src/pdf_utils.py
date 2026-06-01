#!/usr/bin/env python3
"""
PDF utility functions for character sheet generation
"""

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject, TextStringObject


def clean_duration(duration):
    """Remove 'Concentration, up to' prefix from duration string"""
    if duration.startswith("Concentration, up to "):
        return duration.replace("Concentration, up to ", "")
    return duration


def modify_field_font_size(writer, field_name, font_size=8, allow_overflow=False):
    """
    Modify a PDF form field's font size

    Args:
        writer: PdfWriter object
        field_name: Name of the field to modify
        font_size: Font size in points (default: 8)
        allow_overflow: If True, removes clipping to allow text overflow (default: False)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if "/AcroForm" in writer._root_object:
            acro_form = writer._root_object["/AcroForm"]
            if "/Fields" in acro_form:
                fields = acro_form["/Fields"]

                for field_ref in fields:
                    field_obj = field_ref.get_object() if hasattr(field_ref, 'get_object') else field_ref

                    if "/T" in field_obj:
                        current_name = str(field_obj["/T"])
                        if current_name == field_name:
                            # Set font size in default appearance
                            new_da = f"/Helv {font_size} Tf 0 g"
                            field_obj[NameObject("/DA")] = TextStringObject(new_da)

                            # Enable multiline (bit 12 = 4096)
                            if "/Ff" in field_obj:
                                flags = int(field_obj["/Ff"])
                                field_obj[NameObject("/Ff")] = NumberObject(flags | 4096)
                            else:
                                field_obj[NameObject("/Ff")] = NumberObject(4096)

                            # Remove clipping if overflow allowed
                            if allow_overflow:
                                # Delete the appearance stream to force regeneration without clipping
                                if "/AP" in field_obj:
                                    del field_obj[NameObject("/AP")]

                                # Set DoNotScroll flag (bit 23 = 4194304) to prevent scrolling
                                # This often helps with text overflow issues
                                if "/Ff" in field_obj:
                                    flags = int(field_obj["/Ff"])
                                    # Remove DoNotScroll if set, allows better rendering
                                    field_obj[NameObject("/Ff")] = NumberObject(flags & ~4194304)

                            return True
    except Exception as e:
        print(f"    Warning: Could not set font size for {field_name}: {e}")
    return False


def fill_spell_sheet(spell_sheet_template, spells_to_fill, output_path, sheet_title,
                     field_prefix="SpellSheet1_", level_field="SpellSheet 1_Spells Level "):
    """
    Fill a spell sheet PDF with spell data

    Args:
        spell_sheet_template: Path to template PDF
        spells_to_fill: List of spell dictionaries
        output_path: Where to save the filled PDF
        sheet_title: Display name for progress output
        field_prefix: Prefix for field names
        level_field: Field name pattern for spell level
    """
    reader = PdfReader(spell_sheet_template)
    writer = PdfWriter()
    writer.append(reader)

    print(f"\n  {sheet_title} ({len(spells_to_fill)} spells)")

    updates = {}

    for i, spell in enumerate(spells_to_fill[:15], 1):  # Max 15 per sheet
        slot_str = f"{i:02d}-Alt"

        duration = clean_duration(spell['duration'])
        components = spell['material_text'] if spell['material'] else ""
        description = spell.get('description', '')

        # Build field updates
        updates[f"{field_prefix}Spell Name {slot_str}"] = spell['name']
        updates[f"{level_field}{slot_str}"] = spell['level']
        updates[f"{field_prefix}Spell School {slot_str}"] = spell['school']
        updates[f"{field_prefix}Range {slot_str}"] = spell['range']
        updates[f"{field_prefix}Casting Time {slot_str}"] = spell['casting_time']
        updates[f"{field_prefix}Save {slot_str}"] = spell['save']
        updates[f"{field_prefix}Duration {slot_str}"] = duration
        updates[f"{field_prefix}Components {slot_str}"] = components
        updates[f"{field_prefix}Spell Effect {slot_str}"] = description

        # Checkboxes
        updates[f"{field_prefix}Verbal {slot_str}"] = '/Yes' if spell['verbal'] else '/Off'
        updates[f"{field_prefix}Somatic {slot_str}"] = '/Yes' if spell['somatic'] else '/Off'
        updates[f"{field_prefix}Material {slot_str}"] = '/Yes' if spell['material'] else '/Off'
        updates[f"{field_prefix}Ritual {slot_str}"] = '/Yes' if spell['ritual'] else '/Off'
        updates[f"{field_prefix}Concentration {slot_str}"] = '/Yes' if spell['concentration'] else '/Off'
        updates[f"{field_prefix}Prepared {slot_str}"] = '/Yes' if spell['prepared'] else '/Off'

    # Apply updates
    writer.update_page_form_field_values(writer.pages[0], updates)

    # Set smaller font for spell descriptions
    print(f"    Setting 8pt font for descriptions...")
    for i in range(1, min(len(spells_to_fill), 15) + 1):
        slot_str = f"{i:02d}-Alt"
        modify_field_font_size(writer, f"{field_prefix}Spell Effect {slot_str}", font_size=8)

    # Save
    with open(output_path, 'wb') as f:
        writer.write(f)

    print(f"    ✓ Saved")


def fill_widget_fields(writer, field_values):
    """
    Fill Widget annotation fields (D&D Beyond style PDFs)

    Args:
        writer: PdfWriter object
        field_values: Dict of {field_name: value}

    Returns:
        int: Number of fields filled
    """
    filled_count = 0

    for page in writer.pages:
        if "/Annots" not in page:
            continue

        for annot in page["/Annots"]:
            annot_obj = annot.get_object()

            if annot_obj.get("/Subtype") != "/Widget":
                continue

            # Get field name
            field_name = annot_obj.get("/T")
            if not field_name:
                continue

            field_name_str = str(field_name)

            # Check if we have a value for this field
            if field_name_str in field_values:
                value = str(field_values[field_name_str])

                # Set the value
                annot_obj[NameObject("/V")] = TextStringObject(value)
                filled_count += 1

                # For checkboxes, also set appearance state
                if annot_obj.get("/FT") == "/Btn":
                    # Checkbox: set /AS to value or /Off
                    if value in ['Yes', 'On', '•', 'P']:
                        annot_obj[NameObject("/AS")] = NameObject("/Yes")
                    else:
                        annot_obj[NameObject("/AS")] = NameObject("/Off")

    return filled_count


def get_pdf_fields(pdf_path, filter_str=None):
    """
    Get all form fields from a PDF, optionally filtered

    Args:
        pdf_path: Path to PDF file
        filter_str: Optional string to filter field names

    Returns:
        dict: Field names and their properties
    """
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()

    if filter_str:
        return {k: v for k, v in fields.items() if filter_str in k}

    return fields
