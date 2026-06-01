"""
Spell lookup from local Obsidian vault or GitHub fallback
Fetches spell details for PDF field filling
"""

import re
import os
import requests
from pathlib import Path
from typing import Optional, Dict
import yaml


REPO_BASE_URL = "https://raw.githubusercontent.com/Obsidian-TTRPG-Community/dnd5e-markdown/main/compendium/spells"
LOCAL_SPELL_DIR = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/DnD/2. Mechanics/Spells"


def spell_name_to_filename(spell_name: str) -> str:
    """
    Convert spell name to kebab-case filename

    Examples:
        "Cure Wounds" -> "cure-wounds.md"
        "Tasha's Caustic Brew" -> "tashas-caustic-brew.md"
        "Faerie Fire" -> "faerie-fire.md"
    """
    # Remove possessives, special chars
    name = spell_name.lower()
    name = re.sub(r"['']s?\b", "", name)  # Remove 's or '
    name = re.sub(r"[^\w\s-]", "", name)  # Remove special chars except hyphen
    name = re.sub(r"\s+", "-", name.strip())  # Spaces -> hyphens
    name = re.sub(r"-+", "-", name)  # Collapse multiple hyphens

    return f"{name}.md"


def fetch_spell_markdown(spell_name: str) -> Optional[str]:
    """
    Fetch spell markdown from GitHub repo

    Returns raw markdown content or None if not found
    """
    filename = spell_name_to_filename(spell_name)
    url = f"{REPO_BASE_URL}/{filename}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        return None
    except requests.RequestException:
        return None


def parse_spell_markdown(markdown: str) -> Dict[str, str]:
    """
    Parse spell markdown into structured data

    Returns dict with keys:
        - school: "Evocation"
        - level: "1"
        - casting_time: "1 action"
        - range: "Touch"
        - components: "V, S"
        - duration: "Instantaneous"
        - description: Full spell text
    """
    data = {}

    # Extract YAML frontmatter school/level
    school_match = re.search(r'spell/school/(\w+)', markdown)
    if school_match:
        data['school'] = school_match.group(1).capitalize()

    level_match = re.search(r'spell/level/(\d+)', markdown)
    if level_match:
        data['level'] = level_match.group(1)
    elif 'spell/level/cantrip' in markdown:
        data['level'] = '0'

    # Extract spell header (level + school)
    header_match = re.search(r'\*(.+?-level|Cantrip),\s+(.+?)\*', markdown)
    if header_match:
        if not data.get('school'):
            data['school'] = header_match.group(2).strip()

    # Extract stats
    stats_section = re.search(r'- \*\*Casting time:\*\* (.+?)\n', markdown)
    if stats_section:
        data['casting_time'] = stats_section.group(1).strip()

    range_match = re.search(r'- \*\*Range:\*\* (.+?)\n', markdown)
    if range_match:
        data['range'] = range_match.group(1).strip()

    components_match = re.search(r'- \*\*Components:\*\* (.+?)\n', markdown)
    if components_match:
        data['components'] = components_match.group(1).strip()

    duration_match = re.search(r'- \*\*Duration:\*\* (.+?)\n', markdown)
    if duration_match:
        data['duration'] = duration_match.group(1).strip()

    # Extract description (text after Duration line, before "At Higher Levels" or "Classes")
    # Skip the stats block entirely
    desc_pattern = r'- \*\*Duration:\*\*.+?\n\n(.+?)(?:\n\n\*\*At Higher Levels|Classes:|$)'
    desc_match = re.search(desc_pattern, markdown, re.DOTALL)
    if desc_match:
        data['description'] = desc_match.group(1).strip()
    else:
        # Fallback: grab everything after stats section
        fallback = re.search(r'- \*\*Duration:\*\*.+?\n\n(.+?)$', markdown, re.DOTALL)
        if fallback:
            # Remove "At Higher Levels" and "Classes" sections
            desc = fallback.group(1).strip()
            desc = re.sub(r'\n\n\*\*At Higher Levels\.?\*\*.+', '', desc, flags=re.DOTALL)
            desc = re.sub(r'\n\n\*\*Classes\*\*:.+', '', desc, flags=re.DOTALL)
            data['description'] = desc.strip()

    return data


def fetch_local_spell(spell_name: str) -> Optional[str]:
    """
    Fetch spell from local Obsidian vault

    Returns markdown content or None if not found
    """
    if not LOCAL_SPELL_DIR.exists():
        return None

    # Try exact filename match first
    exact_path = LOCAL_SPELL_DIR / f"{spell_name}.md"
    if exact_path.exists():
        return exact_path.read_text()

    # Try case-insensitive search
    for file_path in LOCAL_SPELL_DIR.glob("*.md"):
        if file_path.stem.lower() == spell_name.lower():
            return file_path.read_text()

    return None


def parse_local_spell_markdown(markdown: str) -> Dict[str, str]:
    """
    Parse local Obsidian spell markdown (has YAML frontmatter)

    Local format has structured frontmatter with all fields
    """
    data = {}

    # Extract YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.+?)\n---', markdown, re.DOTALL)
    if frontmatter_match:
        try:
            fm = yaml.safe_load(frontmatter_match.group(1))
            data['school'] = str(fm.get('school', ''))
            data['level'] = str(fm.get('level', ''))
            data['casting_time'] = str(fm.get('casting_time', ''))
            data['range'] = str(fm.get('range', ''))
            data['components'] = str(fm.get('components', ''))
            data['duration'] = str(fm.get('duration', ''))
        except yaml.YAMLError:
            pass

    # Extract description (after stats block, before "At Higher Levels")
    desc_pattern = r'\*\*Duration:\*\*.+?\n\n(.+?)(?:\n\n\*\*At Higher Levels|```dataviewjs|$)'
    desc_match = re.search(desc_pattern, markdown, re.DOTALL)
    if desc_match:
        data['description'] = desc_match.group(1).strip()

    return data


def lookup_spell(spell_name: str) -> Optional[Dict[str, str]]:
    """
    Lookup spell details from local vault first, fallback to GitHub

    Returns structured spell data or None if not found
    """
    # Try local first
    local_md = fetch_local_spell(spell_name)
    if local_md:
        return parse_local_spell_markdown(local_md)

    # Fallback to GitHub
    markdown = fetch_spell_markdown(spell_name)
    if not markdown:
        return None

    return parse_spell_markdown(markdown)


if __name__ == '__main__':
    # Test with Cure Wounds
    result = lookup_spell("Cure Wounds")
    if result:
        print("✅ Cure Wounds:")
        for k, v in result.items():
            print(f"  {k}: {v}")
    else:
        print("❌ Not found")
