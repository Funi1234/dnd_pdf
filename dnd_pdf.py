#!/usr/bin/env python3
"""
D&D PDF Converter - Main CLI Entry Point
Command-line tool for converting D&D Beyond character data to class-specific PDFs
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the generator
from scripts.generate_character_sheet import main

if __name__ == '__main__':
    main()
