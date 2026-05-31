#!/usr/bin/env python3
"""
Extract spell descriptions from markdown files
"""

import os
import re


def extract_description_from_markdown(file_path):
    """
    Extract spell description from a markdown file

    Args:
        file_path: Path to the markdown file

    Returns:
        str: Spell description or None if not found
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Find the description after the metadata and before any code blocks
        # Split by --- to skip frontmatter
        parts = content.split('---')
        if len(parts) >= 3:
            main_content = '---'.join(parts[2:])
        else:
            main_content = content

        # Extract description - everything after the spell header until code block or end
        lines = main_content.split('\n')
        description_lines = []
        in_description = False

        for line in lines:
            # Skip headers and metadata lines
            if line.startswith('#') or line.startswith('**'):
                in_description = False
                continue

            # Stop at code blocks
            if line.startswith('```'):
                break

            # Start collecting after we see actual content
            line = line.strip()
            if line and not line.startswith('*') and not line.startswith('---'):
                in_description = True

            if in_description and line:
                # Clean up dice notation
                line = re.sub(r'`dice: ([^`]+)`', r'\1', line)
                description_lines.append(line)

        description = ' '.join(description_lines).strip()

        # If we didn't get anything, try simpler approach
        if not description:
            # Just get everything between the Duration line and the code block
            match = re.search(r'\*\*Duration:\*\*[^\n]+\n\n(.+?)(?=```|$)', content, re.DOTALL)
            if match:
                description = match.group(1).strip()
                description = re.sub(r'`dice: ([^`]+)`', r'\1', description)
                description = ' '.join(description.split())

        return description if description else None

    except Exception as e:
        print(f"  Error reading {os.path.basename(file_path)}: {e}")
        return None


def find_spell_markdown(spell_name, spell_dir):
    """
    Find the markdown file for a spell, handling name variations

    Args:
        spell_name: Name of the spell
        spell_dir: Directory containing spell markdown files

    Returns:
        str: Path to the markdown file or None if not found
    """
    # Try exact match first
    file_path = os.path.join(spell_dir, f"{spell_name}.md")

    if os.path.exists(file_path):
        return file_path

    # Try case-insensitive match
    for filename in os.listdir(spell_dir):
        if filename.lower().replace('.md', '') == spell_name.lower():
            return os.path.join(spell_dir, filename)

    # Handle special cases
    special_cases = {
        "Homunculus Servant": "Create Homunculus.md",
        "Enlarge/Reduce": "EnlargeReduce.md"
    }

    if spell_name in special_cases:
        file_path = os.path.join(spell_dir, special_cases[spell_name])
        if os.path.exists(file_path):
            return file_path

    return None


def extract_all_spell_descriptions(spells, spell_dir):
    """
    Extract descriptions for all spells from markdown files

    Args:
        spells: List of spell dictionaries
        spell_dir: Directory containing spell markdown files

    Returns:
        int: Number of spells with descriptions found
    """
    found = 0

    for spell in spells:
        name = spell['name']
        file_path = find_spell_markdown(name, spell_dir)

        if file_path:
            description = extract_description_from_markdown(file_path)
            if description:
                spell['description'] = description
                print(f"✓ {name}: {description[:60]}...")
                found += 1
            else:
                spell['description'] = ""
                print(f"✗ {name}: Could not extract description")
        else:
            spell['description'] = ""
            print(f"✗ {name}: File not found")

    return found
