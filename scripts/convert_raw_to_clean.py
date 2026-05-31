#!/usr/bin/env python3
"""
Convert raw D&D Beyond extraction to clean character data format
Transforms the by-page field structure into our generator's expected format

KNOWN D&D BEYOND VARIATIONS:
- Skill proficiency: "AcrobaticsProf" (no space) vs "Acrobatics prof" (with space)
- Weapon fields: Variable trailing spaces "Wpn2 AtkBonus ", "Wpn2 AtkBonus  "
- Spell location: Page 1 (older) vs Page 5 (newer)
- Proficiency values: "P" vs "Yes" for checkboxes

Strategy: Try multiple field name patterns using get_field_value with variants
"""

import json
import argparse
import os


def get_field_value(pages_data, field_name, variants=None):
    """
    Search all pages for a field and return its value

    Tries multiple field name patterns to handle D&D Beyond inconsistencies

    Args:
        pages_data: Pages data dict
        field_name: Primary field name to search for
        variants: List of alternative field names to try

    Returns:
        Field value or empty string
    """
    # Try primary field name first
    for page_key, page_data in pages_data.items():
        if field_name in page_data['fields']:
            value = page_data['fields'][field_name]['value']
            if value and value != 'Off':
                return value

    # Try variants if provided
    if variants:
        for variant in variants:
            for page_key, page_data in pages_data.items():
                if variant in page_data['fields']:
                    value = page_data['fields'][variant]['value']
                    if value and value != 'Off':
                        return value

    return ''


def extract_ability_scores(pages_data):
    """Extract all 6 ability scores and modifiers"""
    abilities = {}
    
    ability_mapping = {
        'strength': ('STR', 'STRmod'),
        'dexterity': ('DEX', 'DEXmod'),
        'constitution': ('CON', 'CONmod'),
        'intelligence': ('INT', 'INTmod'),
        'wisdom': ('WIS', 'WISmod'),
        'charisma': ('CHA', 'CHamod')
    }
    
    for ability_name, (score_field, mod_field) in ability_mapping.items():
        score = get_field_value(pages_data, score_field)
        modifier = get_field_value(pages_data, mod_field)
        abilities[ability_name] = {
            'score': score,
            'modifier': modifier
        }
    
    return abilities


def extract_skills(pages_data):
    """Extract all 18 skills with bonuses and proficiencies"""
    skills = {}
    
    # D&D Beyond skill field names with variants
    # Format: skill_key: (bonus_field, prof_field_primary, prof_field_variants)
    skill_mapping = {
        'acrobatics': ('Acrobatics', 'AcrobaticsProf', ['Acrobatics prof']),
        'animal_handling': ('Animal', 'AnimalProf', ['Animal prof', 'Animal Handling prof']),
        'arcana': ('Arcana', 'ArcanaProf', ['Arcana prof']),
        'athletics': ('Athletics', 'AthleticsProf', ['Athletics prof']),
        'deception': ('Deception', 'DeceptionProf', ['Deception prof']),
        'history': ('History', 'HistoryProf', ['History prof']),
        'insight': ('Insight', 'InsightProf', ['Insight prof']),
        'intimidation': ('Intimidation', 'IntimidationProf', ['Intimidation prof']),
        'investigation': ('Investigation', 'InvestigationProf', ['Investigation prof']),
        'medicine': ('Medicine', 'MedicineProf', ['Medicine prof']),
        'nature': ('Nature', 'NatureProf', ['Nature prof']),
        'perception': ('Perception', 'PerceptionProf', ['Perception prof']),
        'performance': ('Performance', 'PerformanceProf', ['Performance prof']),
        'persuasion': ('Persuasion', 'PersuasionProf', ['Persuasion prof']),
        'religion': ('Religion', 'ReligionProf', ['Religion prof']),
        'sleight': ('Sleight of Hand', 'SleightOfHandProf', ['Sleight of Hand prof']),
        'stealth': ('Stealth', 'StealthProf', ['Stealth prof']),
        'survival': ('Survival', 'SurvivalProf', ['Survival prof'])
    }

    for skill_key, (skill_field, prof_field, prof_variants) in skill_mapping.items():
        bonus = get_field_value(pages_data, skill_field)

        # Try primary prof field, then variants
        # D&D Beyond uses 'P' for proficiency (or 'Yes' in some versions)
        prof_value = get_field_value(pages_data, prof_field, variants=prof_variants)
        proficiency = 'P' if prof_value in ['P', 'Yes'] else ''

        skills[skill_key] = {
            'bonus': bonus,
            'proficiency': proficiency
        }
    
    return skills


def extract_saving_throws(pages_data):
    """Extract saving throws with proficiency markers"""
    saves = {}

    # Try multiple field name patterns for saves
    ability_mapping = {
        'strength': ('ST Strength', ['StrProf', 'ST Strength prof']),
        'dexterity': ('ST Dexterity', ['DexProf', 'ST Dexterity prof']),
        'constitution': ('ST Constitution', ['ConProf', 'ST Constitution prof']),
        'intelligence': ('ST Intelligence', ['IntProf', 'ST Intelligence prof']),
        'wisdom': ('ST Wisdom', ['WisProf', 'ST Wisdom prof']),
        'charisma': ('ST Charisma', ['ChaProf', 'ST Charisma prof'])
    }

    for ability, (field_name, prof_variants) in ability_mapping.items():
        save_value = get_field_value(pages_data, field_name)

        # Try multiple proficiency field patterns
        prof_value = get_field_value(pages_data, field_name + ' prof', variants=prof_variants)

        saves[ability] = save_value
        # Accept 'Yes', 'P', or '•' as proficiency markers
        if prof_value in ['Yes', 'P', '•']:
            saves[f'{ability}_proficient'] = '•'

    return saves


def extract_combat_stats(pages_data):
    """Extract combat-related stats"""
    return {
        'armor_class': get_field_value(pages_data, 'AC'),
        'initiative': get_field_value(pages_data, 'Initiative'),
        'speed': get_field_value(pages_data, 'Speed').replace(' ft.', '').replace(' (Walking)', '').strip(),
        'max_hp': get_field_value(pages_data, 'HPMax'),
        'current_hp': get_field_value(pages_data, 'HPCurrent'),
        'passive_perception': get_field_value(pages_data, 'Passive'),
        'passive_insight': get_field_value(pages_data, 'Passive')  # D&D Beyond only has one Passive field
    }


def extract_weapons(pages_data):
    """Extract weapon attacks"""
    weapons = []
    
    # D&D Beyond has up to 3 weapons on the main sheet
    for i in range(1, 4):
        name = get_field_value(pages_data, f'Wpn Name{"" if i == 1 else " " + str(i)}')
        if not name:
            continue
            
        # Attack bonus field has variable spacing
        atk_field_variants = [
            f'Wpn{i} AtkBonus',
            f'Wpn{i} AtkBonus ',
            f'Wpn{i} AtkBonus  '
        ]
        attack_bonus = ''
        for variant in atk_field_variants:
            attack_bonus = get_field_value(pages_data, variant)
            if attack_bonus:
                break
        
        # Damage field has variable spacing  
        dmg_field_variants = [
            f'Wpn{i} Damage',
            f'Wpn{i} Damage ',
            f'Wpn{i} Damage  '
        ]
        damage = ''
        for variant in dmg_field_variants:
            damage = get_field_value(pages_data, variant)
            if damage:
                break
        
        weapons.append({
            'name': name,
            'attack_bonus': attack_bonus,
            'damage': damage
        })
    
    return weapons


def extract_spellcasting(pages_data):
    """Extract spell save DC and attack bonus"""
    return {
        'spell_save_dc': get_field_value(pages_data, 'spellSaveDC0'),
        'spell_attack_bonus': get_field_value(pages_data, 'spellAtkBonus0')
    }


def extract_proficiencies(pages_data):
    """Extract proficiencies as formatted text"""

    # Try the combined field first (newer D&D Beyond format)
    combined = get_field_value(pages_data, 'ProficienciesLang', variants=['Proficiencies'])
    if combined:
        return combined

    # Fall back to individual fields (older format)
    armor = get_field_value(pages_data, 'Armor')
    weapons_prof = get_field_value(pages_data, 'Weapons')
    tools = get_field_value(pages_data, 'Tools')
    languages = get_field_value(pages_data, 'Languages')

    sections = []

    if armor:
        sections.append(f"=== ARMOR ===\n{armor}")
    if weapons_prof:
        sections.append(f"=== WEAPONS ===\n{weapons_prof}")
    if tools:
        sections.append(f"=== TOOLS ===\n{tools}")
    if languages:
        sections.append(f"=== LANGUAGES ===\n{languages}")

    return '\n\n'.join(sections)


def convert_raw_to_clean(raw_data):
    """Convert raw D&D Beyond data to clean format"""
    
    pages_data = raw_data['pages']
    
    # Extract character info
    character_name = get_field_value(pages_data, 'CharacterName')
    class_level = get_field_value(pages_data, 'CLASS  LEVEL')
    race = get_field_value(pages_data, 'RACE')
    background = get_field_value(pages_data, 'BACKGROUND')
    alignment = get_field_value(pages_data, 'ALIGNMENT')
    player_name = get_field_value(pages_data, 'PLAYER NAME')
    
    clean_data = {
        'character': {
            'character_info': {
                'name': character_name,
                'class_and_level': class_level,
                'race': race,
                'background': background,
                'alignment': alignment,
                'player_name': player_name,
                'experience_points': get_field_value(pages_data, 'XP')
            },
            'ability_scores': extract_ability_scores(pages_data),
            'skills': extract_skills(pages_data),
            'saving_throws': extract_saving_throws(pages_data),
            'combat': extract_combat_stats(pages_data),
            'spellcasting': extract_spellcasting(pages_data),
            'weapons': extract_weapons(pages_data),
            'proficiencies': extract_proficiencies(pages_data),
            'spells': []  # TODO: Extract spell list
        }
    }
    
    return clean_data


def main():
    parser = argparse.ArgumentParser(
        description='Convert raw D&D Beyond extraction to clean character data'
    )
    parser.add_argument('--input', '-i', required=True,
                        help='Input raw JSON file')
    parser.add_argument('--output', '-o', required=True,
                        help='Output clean JSON file')
    
    args = parser.parse_args()
    
    # Load raw data
    print(f"📖 Loading raw data: {args.input}")
    with open(args.input) as f:
        raw_data = json.load(f)
    
    # Convert
    print("🔄 Converting to clean format...")
    clean_data = convert_raw_to_clean(raw_data)
    
    # Save
    print(f"💾 Saving clean data: {args.output}")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(clean_data, f, indent=2)
    
    char_name = clean_data['character']['character_info']['name']
    char_class = clean_data['character']['character_info']['class_and_level']
    print(f"✅ Converted: {char_name} ({char_class})")


if __name__ == '__main__':
    main()
