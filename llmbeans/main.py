# llmbeans/main.py
"""Entry point for llmbeans."""

import sys


def main():
    """Run the llmbeans CLI."""
    try:
        from llmbeans.cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"Error: Missing dependency — {e}")
        print("Install with: pip install gguf safetensors huggingface-hub rich")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
