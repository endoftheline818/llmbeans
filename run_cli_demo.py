#!/usr/bin/env python3
"""
Demo script to run the llmbeans CLI with mocked inputs and mocked model scanning.
This shows what the CLI output would look like without requiring real model files.
"""

import sys
import os
from unittest.mock import patch
from io import StringIO

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Change to the llmbeans directory
os.chdir('/Users/tjax/llmbeans')

def run_cli_demo():
    """Run the CLI with mocked inputs and return the output."""
    print("Running llmbeans CLI demo with mocked inputs...")
    print("=" * 60)

    # Mock user inputs for the prompts
    mock_inputs = [
        '/fake/path/to/model.gguf',  # Model path
        'y',                         # Use auto-detected hardware
        '1',                         # Select first tool (llamacpp)
        '1'                          # Select first quality mode (balanced)
    ]

    input_iter = iter(mock_inputs)

    def mock_input(prompt):
        try:
            value = next(input_iter)
            # Print the prompt and value so we can see the interaction
            print(f"{prompt} {value}", end="")
            # If the prompt doesn't end with a newline, add one for clarity
            if not prompt.endswith('\n') and not prompt.endswith(' '):
                print(" ", end="")
            print(value)  # Echo the value on a new line for clarity
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

        # We need to mock several functions to avoid requiring real files/hardware
        with patch('builtins.input', side_effect=mock_input), \
             patch('llmbeans.cli.scan_model') as mock_scan_model, \
             patch('llmbeans.cli.detect_hardware') as mock_detect_hardware, \
             patch('llmbeans.cli.get_hardware_profiles') as mock_get_hardware_profiles, \
             patch('llmbeans.cli.get_available_tools') as mock_get_available_tools, \
             patch('llmbeans.cli.recommend') as mock_recommend, \
             patch('llmbeans.cli.generate_summary') as mock_generate_summary, \
             patch('llmbeans.cli.write_scripts') as mock_write_scripts:

            # Setup mock return values
            # Mock model info
            from llmbeans.models.scanner import ModelInfo
            mock_model_info = ModelInfo(
                name='demo-model',
                architecture='llama',
                quantization='Q4_K_M',
                bits=4.5,
                size_gb=4.5,
                context_length=32768,
                num_layers=32,
                embedding_dim=4096,
                num_attention_heads=32,
                num_key_value_heads=8,
                vocab_size=32000,
                model_size_gb=4.5,
                estimated_vram_gb=4.5,
                source_path='/fake/path/to/model.gguf',
                is_remote=False,
                format=None  # Will be set by scanner, but we'll mock it
            )
            mock_scan_model.return_value = mock_model_info

            # Mock hardware info
            from llmbeans.hardware.detector import HardwareInfo
            mock_hardware_info = HardwareInfo(
                id='m4-pro',
                name='Apple M4 Pro',
                year=2024,
                ram_gb=24,
                ram_type='LPDDR5X',
                cpu_cores=12,
                cpu_threads=12,
                gpu_type='apple_silicon',
                gpu_name='Apple M4 Pro',
                gpu_vram_gb=None,  # Unified memory
                metal=True,
                cuda=False,
                cuda_compute=None,
                vram_bandwidth_gbps=None,
                ssd_recommended=True,
                category='laptop'
            )
            mock_detect_hardware.return_value = mock_hardware_info
            mock_get_hardware_profiles.return_value = []  # Empty to force auto-detect path

            # Mock available tools
            mock_get_available_tools.return_value = ['llamacpp', 'ollama', 'mlx', 'vllm', 'lmstudio']

            # Mock recommendation
            from llmbeans.recommenders.engine import Recommendation
            mock_recommendation = Recommendation(
                hosting_tool='llamacpp',
                context_length=8192,
                batch_size=512,
                thread_count=12,
                gpu_offload_layers=32,
                estimated_tok_per_sec=45.0,
                estimated_vram_usage_gb=3.6,
                estimated_ram_usage_gb=5.2,
                warnings=['Model is smaller than available unified memory, consider increasing context length for better utilization.']
            )
            mock_recommend.return_value = mock_recommendation

            # Mock summary generation
            mock_generate_summary.return_value = """Model: demo-model (llama)
Architecture: llama
Quantization: Q4_K_M (4.5 bits)
Size: 4.5 GB
Context length: 32768 tokens
Layers: 32

Hardware: Apple M4 Pro
RAM: 24 GB (LPDDR5X)
GPU: Apple M4 Pro (Unified memory)
Memory bandwidth: 273.0 GB/s

Hosting Tool: llamacpp
Quality Mode: balanced

Recommended Configuration:
  Context length: 8192
  Batch size: 512
  Thread count: 12
  GPU offload layers: 32
  -ctk: f16         (KV cache key type)
  -ctv: f16         (KV cache value type)
  --rope-scaling: yarn
  --rope-freq-scale: 0.5
  --temp: 0.7
  --repeat-penalty: 1.1

Estimated Performance:
  Tokens/second: ~45.0
  VRAM usage: ~3.6 GB
  RAM usage: ~5.2 GB

Warnings:
  - Model is smaller than available unified memory, consider increasing context length for better utilization."""

            # Mock script writing
            mock_write_scripts.return_value = {
                'shell': '/Users/tjax/llmbeans-output/run.sh',
                'batch': '/Users/tjax/llmbeans-output/run.bat'
            }

            # Run the main function
            try:
                cli.main()
            except SystemExit:
                pass  # Expected when main completes normally
            except Exception as e:
                print(f"[Demo] Unexpected error: {e}")
                import traceback
                traceback.print_exc()

    finally:
        # Restore stdout
        output = captured_output.getvalue()
        sys.stdout = old_stdout

    return output

if __name__ == "__main__":
    output = run_cli_demo()
    print("\n" + "="*60)
    print("DEMO OUTPUT:")
    print("="*60)
    print(output)
