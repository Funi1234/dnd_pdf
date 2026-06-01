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


def normalize_text(text):
    if not text or not isinstance(text, str):
        return text
    text = text.replace(chr(0x2019), "'")
    text = text.replace(chr(0x2018), "'")
    text = text.replace(chr(0x201D), '"')
    text = text.replace(chr(0x201C), '"')
    text = text.replace(chr(0x2013), "-")
    text = text.replace(chr(0x2014), "-")
    return text



def get_field_value(pages_data, field_name, variants=None):
    """
    Search all pages for a field and return its value

    Tries multiple field name patterns to handle D&D Beyond inconsistencies

    Args:
        pages_data: Pages data dict
        field_name: Primary field name to search for
        variants: List of alternative field names to try

    Returns:
        Field value or empty string (with normalized characters)
    """
    # Try primary field name first
    for page_key, page_data in pages_data.items():
        if field_name in page_data['fields']:
            value = page_data['fields'][field_name]['value']
            if value and value != 'Off':
                return normalize_text(value)

    # Try variants if provided
    if variants:
        for variant in variants:
            for page_key, page_data in pages_data.items():
                if variant in page_data['fields']:
                    value = page_data['fields'][variant]['value']
                    if value and value != 'Off':
                        return normalize_text(value)

    return ''


def extract_ability_scores(pages_data):
    """Extract all 6 ability scores and modifiers"""
    abilities = {}

    # Note: Some modifier fields have trailing spaces in D&D Beyond PDFs
    ability_mapping = {
        'strength': ('STR', 'STRmod'),
        'dexterity': ('DEX', 'DEXmod', ['DEXmod ']),  # Try with space
        'constitution': ('CON', 'CONmod'),
        'intelligence': ('INT', 'INTmod'),
        'wisdom': ('WIS', 'WISmod'),
        'charisma': ('CHA', 'CHamod')
    }
    
    for ability_name, fields_tuple in ability_mapping.items():
        score_field = fields_tuple[0]
        mod_field = fields_tuple[1]
        mod_variants = fields_tuple[2] if len(fields_tuple) > 2 else None

        score = get_field_value(pages_data, score_field)
        modifier = get_field_value(pages_data, mod_field, variants=mod_variants)
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
    """Extract combat-related stats with cascading fallbacks"""

    # Passive scores - try multiple patterns (D&D Beyond inconsistent!)
    # Patterns: 'Passive', 'Passive1', 'Passive Perception', etc.
    passive_perception = get_field_value(pages_data, 'Passive Perception', variants=[
        'Passive1', 'Passive', 'PassivePerception'
    ])
    passive_insight = get_field_value(pages_data, 'Passive Insight', variants=[
        'Passive2', 'Passive', 'PassiveInsight'
    ])

    # If still empty, use Passive1 as perception, Passive2 as insight
    if not passive_perception:
        passive_perception = get_field_value(pages_data, 'Passive1')
    if not passive_insight:
        passive_insight = get_field_value(pages_data, 'Passive2')

    return {
        'armor_class': get_field_value(pages_data, 'AC'),
        'initiative': get_field_value(pages_data, 'Initiative'),
        'speed': get_field_value(pages_data, 'Speed').replace(' ft.', '').replace(' (Walking)', '').strip(),
        'max_hp': get_field_value(pages_data, 'HPMax'),
        'current_hp': get_field_value(pages_data, 'HPCurrent'),
        'passive_perception': passive_perception,
        'passive_insight': passive_insight
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


def extract_physical_traits(pages_data):
    """Extract physical appearance traits"""
    return {
        'age': get_field_value(pages_data, 'AGE'),
        'height': get_field_value(pages_data, 'HEIGHT'),
        'weight': get_field_value(pages_data, 'WEIGHT'),
        'eyes': get_field_value(pages_data, 'EYES'),
        'skin': get_field_value(pages_data, 'SKIN'),
        'hair': get_field_value(pages_data, 'HAIR'),
        'appearance': get_field_value(pages_data, 'Appearance', variants=['APPEARANCE'])
    }


def extract_personality(pages_data):
    """Extract personality traits, ideals, bonds, flaws, backstory"""
    return {
        'personality_traits': get_field_value(pages_data, 'PersonalityTraits ', variants=['PersonalityTraits', 'Personality Traits']),
        'ideals': get_field_value(pages_data, 'Ideals'),
        'bonds': get_field_value(pages_data, 'Bonds'),
        'flaws': get_field_value(pages_data, 'Flaws'),
        'backstory': get_field_value(pages_data, 'Backstory')
    }


def extract_equipment(pages_data):
    """Extract equipment list from D&D Beyond data

    Equipment on page_2/page_3 with structure:
    - Eq Name{i}, Eq Qty{i}, Eq Weight{i}
    """
    equipment = []

    # Equipment typically on page_2 (0-25) and page_3 (26-55)
    for i in range(60):
        name_key = f'Eq Name{i}'
        name = get_field_value(pages_data, name_key).strip()

        if not name:
            continue

        equipment.append({
            'name': name,
            'quantity': get_field_value(pages_data, f'Eq Qty{i}'),
            'weight': get_field_value(pages_data, f'Eq Weight{i}')
        })

    return equipment


def extract_features(pages_data):
    """Extract features/traits text from D&D Beyond data

    Features on page_2/page_3 as FeaturesTraits1-6
    """
    features = []

    for i in range(1, 10):
        feat_text = get_field_value(pages_data, f'FeaturesTraits{i}').strip()
        if feat_text:
            features.append(feat_text)

    return features


def extract_spells(pages_data):
    """Extract spell list from D&D Beyond data

    D&D Beyond spell structure:
    - spellHeader0/1/2 exist but are NOT indexed with spells
    - Spells numbered 0-59 across all levels
    - Level inferred from index ranges (0-7 cantrips, 8-32 1st, 33+ 2nd, etc.)
    - Must collect all spells first, then assign levels based on count
    """
    spells_raw = []

    # Find which page has spell data
    spell_page = None
    for page_key in ['page_5', 'page_1', 'page_6']:
        if page_key in pages_data and 'spellName0' in pages_data[page_key]['fields']:
            spell_page = pages_data[page_key]['fields']
            break

    if not spell_page:
        return []

    # Collect all spells first (NOT zero-padded indices)
    for i in range(60):
        name_key = f'spellName{i}'
        name = spell_page.get(name_key, {}).get('value', '').strip()
        if not name:
            continue

        spells_raw.append({
            'index': i,
            'name': name,
            'prepared': spell_page.get(f'spellPrepared{i}', {}).get('value', ''),
            'school': spell_page.get(f'spellSchool{i}', {}).get('value', ''),
            'casting_time': spell_page.get(f'spellCastingTime{i}', {}).get('value', ''),
            'range': spell_page.get(f'spellRange{i}', {}).get('value', ''),
            'duration': spell_page.get(f'spellDuration{i}', {}).get('value', ''),
            'components': spell_page.get(f'spellComponents{i}', {}).get('value', ''),
            'save_hit': spell_page.get(f'spellSaveHit{i}', {}).get('value', '')
        })

    # Assign levels based on spell index ranges
    # Pattern observed: 0-7 cantrips, 8-32 1st level, 33-44 2nd level
    # Heuristic: known cantrips have single-word casting times or common names
    known_cantrips = {'Guidance', 'True Strike', 'Shocking Grasp', 'Message',
                      'Ray of Frost', 'Minor Illusion', 'Mending', 'Tasha\'s Caustic Brew',
                      'Fire Bolt', 'Prestidigitation', 'Mage Hand', 'Light'}

    for spell in spells_raw:
        # Use index ranges based on observed pattern
        if spell['index'] <= 7:
            spell['level'] = '0'
        elif spell['index'] <= 32:
            spell['level'] = '1'
        elif spell['index'] <= 44:
            spell['level'] = '2'
        else:
            spell['level'] = '3'  # Higher levels if present

        # Remove temp index field
        del spell['index']

    return spells_raw


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
            'physical_traits': extract_physical_traits(pages_data),
            'personality': extract_personality(pages_data),
            'spells': extract_spells(pages_data),
            'equipment': extract_equipment(pages_data),
            'features': extract_features(pages_data)
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
