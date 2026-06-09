#!/usr/bin/env python3
"""
Test script for llmbeans CLI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llmbeans.cli import main

if __name__ == "__main__":
    main()