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
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_cli_demo():
    """Run the CLI with mocked inputs and return the output."""
    print("Running llmbeans CLI demo with mocked inputs...")
    print("=" * 60)

    # Use this actual script file as a placeholder path so os.path.exists passes
    valid_placeholder_path = os.path.abspath(__file__)

    # Mock user inputs for the prompts
    mock_inputs = [
        valid_placeholder_path,      # Model path (must exist on disk)
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
            return ''

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    try:
        # Setup mock data structures
        from llmbeans.models.scanner import ModelInfo, ModelFormat
        mock_model_info = ModelInfo(
            name='demo-model',
            format=ModelFormat.GGUF,
            architecture='llama',
            parameter_count=7.0,
            quant_method='Q4_K_M',
            quant_bits=4.5,
            context_length=32768,
            hidden_size=4096,
            intermediate_size=11008,
            num_layers=32,
            num_attention_heads=32,
            num_key_value_heads=8,
            vocab_size=32000,
            model_size_gb=4.5,
            estimated_vram_gb=4.5,
            source_path=valid_placeholder_path,
            is_remote=False
        )

        from llmbeans.hardware.detector import HardwareProfile
        mock_hardware_profile = HardwareProfile(
            os='darwin',
            cpu_cores=12,
            ram_total_gb=24.0,
            ram_free_gb=16.0,
            gpu_vendor='Apple',
            gpu_vram_gb=None,
            gpu_name='Apple M4 Pro',
            is_apple_silicon=True,
            unified_memory=True,
            metal_supported=True,
            disk_is_ssd=True,
            laptop_model='MacBook Pro',
            memory_bandwidth_gbps=273.0
        )

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

        # Mock summary text output
        mock_summary_text = """Model: demo-model (llama)
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

        output_dir = os.path.abspath('./llmbeans-output')
        mock_scripts_dict = {
            'shell': os.path.join(output_dir, 'run.sh'),
            'batch': os.path.join(output_dir, 'run.bat')
        }

        # Open the patch context manager targeting both potential namespaces
        with patch('builtins.input', side_effect=mock_input), \
             patch('cli.scan_model', create=True, return_value=mock_model_info), \
             patch('cli.detect_hardware', create=True, return_value=mock_hardware_profile), \
             patch('cli.get_hardware_profiles', create=True, return_value=[]), \
             patch('cli.get_available_tools', create=True, return_value=['llamacpp', 'ollama', 'mlx', 'vllm', 'lmstudio']), \
             patch('cli.recommend', create=True, return_value=mock_recommendation), \
             patch('cli.generate_summary', create=True, return_value=mock_summary_text), \
             patch('cli.write_scripts', create=True, return_value=mock_scripts_dict), \
             patch('llmbeans.cli.scan_model', create=True, return_value=mock_model_info), \
             patch('llmbeans.cli.detect_hardware', create=True, return_value=mock_hardware_profile), \
             patch('llmbeans.cli.get_hardware_profiles', create=True, return_value=[]), \
             patch('llmbeans.cli.get_available_tools', create=True, return_value=['llamacpp', 'ollama', 'mlx', 'vllm', 'lmstudio']), \
             patch('llmbeans.cli.recommend', create=True, return_value=mock_recommendation), \
             patch('llmbeans.cli.generate_summary', create=True, return_value=mock_summary_text), \
             patch('llmbeans.cli.write_scripts', create=True, return_value=mock_scripts_dict):

            # Safely import the module inside the active mock session
            import cli

            # Run the main engine pipeline
            try:
                cli.main()
            except SystemExit:
                pass  # Clean exit handling
            except Exception as e:
                print(f"[Demo] Unexpected inner error: {e}")
                import traceback
                traceback.print_exc()

    finally:
        # Restore normal stdout streaming to terminal
        output = captured_output.getvalue()
        sys.stdout = old_stdout

    return output

if __name__ == "__main__":
    output = run_cli_demo()
    print("\n" + "="*60)
    print("DEMO OUTPUT:")
    print("="*60)
    print(output)
