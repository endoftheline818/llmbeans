#!/usr/bin/env python3
"""
Integration test for llmbeans CLI with mocked inputs.
"""

import sys
import os
from unittest.mock import patch
from io import StringIO

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Change to the llmbeans directory
os.chdir('/Users/tjax/llmbeans')

def test_cli_with_mocked_inputs():
    """Test CLI flow with mocked user inputs."""
    print("Testing CLI with mocked inputs...")

    # Mock user inputs for the prompts
    # Order of inputs:
    # 1. Model path (we'll use a fake path that exists in our test)
    # 2. Hardware auto-detect choice (y/n)
    # 3. Tool selection
    # 4. Quality mode selection

    # First, let's check if we have a test model we can use
    test_model_path = "/tmp/test-model.gguf"
    if not os.path.exists(test_model_path):
        # Create a dummy file for testing
        os.makedirs(os.path.dirname(test_model_path), exist_ok=True)
        with open(test_model_path, 'w') as f:
            f.write("dummy content")

    mock_inputs = [
        test_model_path,  # Model path
        'y',              # Use auto-detected hardware
        '1',              # Select first tool (llamacpp)
        '1'               # Select first quality mode (balanced)
    ]

    input_iter = iter(mock_inputs)

    def mock_input(prompt):
        try:
            value = next(input_iter)
            print(f"{prompt} {value}")  # Echo the prompt and value for visibility
            return value
        except StopIteration:
            # If we run out of inputs, return empty string or default
            return ''

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    try:
        # Import and run main
        import cli

        # Patch the input function
        with patch('builtins.input', side_effect=mock_input):
            # Also patch functions that might require actual files or hardware
            # We'll let them run but they should handle missing data gracefully
            try:
                cli.main()
            except SystemExit:
                pass  # Expected when main completes
            except Exception as e:
                print(f"CLI exited with exception: {e}")
                import traceback
                traceback.print_exc()

    finally:
        # Restore stdout
        output = captured_output.getvalue()
        sys.stdout = old_stdout

    print("\n" + "="*60)
    print("CAPTURED OUTPUT:")
    print("="*60)
    print(output)
    print("="*60)

    # Check for expected elements in output
    if "llmbeans - Local LLM Configuration Generator" in output:
        print("✓ Header found in output")
    else:
        print("✗ Header NOT found in output")

    if "Model scanned:" in output or "Scanning model:" in output:
        print("✓ Model scanning mentioned in output")
    else:
        print("✗ Model scanning NOT mentioned in output")

    if "Recommendation Summary" in output:
        print("✓ Recommendation section found in output")
    else:
        print("✗ Recommendation section NOT found in output")

    if "Summary saved to:" in output:
        print("✓ Save message found in output")
    else:
        print("✗ Save message NOT found in output")

    return output

if __name__ == "__main__":
    test_cli_with_mocked_inputs()
