#!/usr/bin/env python3
"""
Rename split PDF pages with descriptive names
"""

import os
import sys
import argparse
import shutil


def rename_pages(pages_dir, name_mapping):
    """
    Rename page files using a mapping

    Args:
        pages_dir: Directory containing page_N.pdf files
        name_mapping: Dict of {page_number: "descriptive_name"}
    """

    print("=" * 80)
    print("PDF PAGE RENAMER")
    print("=" * 80)
    print(f"\n📁 Directory: {pages_dir}")
    print(f"📝 Renaming {len(name_mapping)} pages...")

    for page_num, new_name in name_mapping.items():
        old_filename = f"page_{page_num}.pdf"
        old_path = os.path.join(pages_dir, old_filename)

        # Add .pdf extension if not present
        if not new_name.endswith('.pdf'):
            new_name = f"{new_name}.pdf"

        new_path = os.path.join(pages_dir, new_name)

        if not os.path.exists(old_path):
            print(f"  ⚠️  Warning: {old_filename} not found, skipping")
            continue

        if os.path.exists(new_path):
            print(f"  ⚠️  Warning: {new_name} already exists, skipping")
            continue

        shutil.move(old_path, new_path)
        print(f"  ✅ {old_filename} -> {new_name}")

    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Rename split PDF pages with descriptive names'
    )

    parser.add_argument('--dir', '-d', required=True,
                        help='Directory containing page_N.pdf files')
    parser.add_argument('--class-template', '-c',
                        help='Use predefined naming for a class template (artificer, cleric, wizard)')

    args = parser.parse_args()

    # Predefined mappings for class templates
    class_mappings = {
        'artificer': {
            1: 'front_combined',
            2: 'front_separate',
            3: 'background_regular',
            4: 'background_sidekick',
            5: 'spells_1',
            6: 'spells_2',
            7: 'spells_3',
            8: 'spells_4'
        },
        'cleric': {
            1: 'front_combined',
            2: 'front_separate',
            3: 'background_regular',
            4: 'background_sidekick',
            5: 'spells_1',
            6: 'spells_2',
            7: 'spells_3',
            8: 'spells_4'
        },
        'wizard': {
            1: 'front_combined',
            2: 'front_separate',
            3: 'background_regular',
            4: 'background_sidekick',
            5: 'spells_1',
            6: 'spells_2',
            7: 'spells_3',
            8: 'spells_4'
        }
    }

    if args.class_template:
        if args.class_template.lower() not in class_mappings:
            print(f"❌ Error: Unknown class template '{args.class_template}'")
            print(f"Available: {', '.join(class_mappings.keys())}")
            sys.exit(1)

        name_mapping = class_mappings[args.class_template.lower()]
    else:
        print("❌ Error: Must specify --class-template (or implement custom mapping)")
        sys.exit(1)

    # Validate directory exists
    if not os.path.exists(args.dir):
        print(f"❌ Error: Directory not found: {args.dir}")
        sys.exit(1)

    # Rename the pages
    rename_pages(args.dir, name_mapping)


if __name__ == '__main__':
    main()
