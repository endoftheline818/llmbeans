#!/usr/bin/env python3
"""
Simple test to verify the CLI module structure and imports work correctly.
This avoids interactive prompts.
"""

import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    # Test CLI module imports
    try:
        import cli
        print("✓ CLI module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import CLI module: {e}")
        return False
    
    # Test that we can access key functions/classes
    try:
        from cli import Colors, print_header, print_success, print_warning, print_error, print_info
        print("✓ CLI helper functions imported successfully")
    except Exception as e:
        print(f"✗ Failed to import CLI helpers: {e}")
        return False
    
    # Test llmbeans modules
    try:
        from llmbeans.models.scanner import ModelInfo
        from llmbeans.hardware.profiles import HardwareProfileEntry
        from llmbeans.hardware.detector import detect_hardware
        from llmbeans.recommenders.engine import recommend, Recommendation, get_available_tools
        from llmbeans.output.script_gen import write_scripts, generate_summary
        print("✓ llmbeans modules imported successfully")
    except Exception as e:
        print(f"✗ Failed to import llmbeans modules: {e}")
        return False
    
    return True

def test_colors():
    """Test that color constants are defined."""
    try:
        from cli import Colors
        # Check that key colors exist
        assert hasattr(Colors, 'HEADER')
        assert hasattr(Colors, 'SUCCESS')
        assert hasattr(Colors, 'WARNING')
        assert hasattr(Colors, 'FAIL')
        assert hasattr(Colors, 'ENDC')
        assert hasattr(Colors, 'BOLD')
        print("✓ Color constants defined correctly")
        return True
    except Exception as e:
        print(f"✗ Color constants test failed: {e}")
        return False

def test_print_functions():
    """Test that print functions work (they just print to stdout)."""
    try:
        from cli import print_header, print_success, print_warning, print_error, print_info
        # These should not raise exceptions
        print_header("Test Header")
        print_success("Test Success")
        print_warning("Test Warning")
        print_error("Test Error")
        print_info("Test Info")
        print("✓ Print functions work correctly")
        return True
    except Exception as e:
        print(f"✗ Print functions test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("llmbeans CLI Module Test")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_colors()
    all_passed &= test_print_functions()
    
    print("=" * 50)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        sys.exit(1)