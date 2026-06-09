# llmbeans/cli.py
"""
Command-line interface for llmbeans.
Provides a terminal-based wizard for generating LLM startup configurations.
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add the project root to sys.path so we can import llmbeans modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"DEBUG: sys.path[0] = {sys.path[0]}")
print(f"DEBUG: sys.path = {sys.path}")

from llmbeans.models.scanner import ModelInfo
from llmbeans.hardware.profiles import HardwareProfileEntry, load_profiles, get_profile_by_id
from llmbeans.hardware.detector import detect_hardware
from llmbeans.hardware.estimator import (
    estimate_tokens_per_sec,
    estimate_total_memory_gb,
    estimate_max_context,
)
from llmbeans.recommenders.engine import recommend, Recommendation, get_available_tools
from llmbeans.output.script_gen import write_scripts, generate_summary

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def prompt_model_path() -> str:
    """Prompt user for model path."""
    while True:
        path = input(f"{Colors.BOLD}Enter path to model file or directory:{Colors.ENDC} ").strip()
        if not path:
            print_error("Path cannot be empty")
            continue
        if os.path.exists(path):
            return path
        print_error(f"Path does not exist: {path}")

def scan_model(model_path: str) -> Optional[ModelInfo]:
    """Scan model and return ModelInfo."""
    try:
        print_info(f"Scanning model: {model_path}")
        # Reuse the scanner logic from the existing code
        from llmbeans.models.scanner import detect_format, _scan_gguf, _scan_safetensors, _scan_hf_repo
        from llmbeans.models.scanner import ModelFormat

        fmt = detect_format(model_path)
        if fmt == ModelFormat.GGUF:
            return _scan_gguf(model_path)
        elif fmt == ModelFormat.SAFETENSORS:
            return _scan_safetensors(model_path)
        elif fmt == ModelFormat.HF_REPO:
            return _scan_hf_repo(model_path)
        else:
            print_error(f"Unsupported model format: {fmt.value}")
            return None
    except Exception as e:
        print_error(f"Failed to scan model: {e}")
        return None

def get_hardware_profiles() -> list[HardwareProfileEntry]:
    """Load hardware profiles."""
    try:
        return load_profiles()
    except Exception as e:
        print_warning(f"Could not load hardware profiles: {e}")
        return []

def prompt_hardware_selection(profiles: list[HardwareProfileEntry]) -> HardwareProfileEntry:
    """Prompt user to select hardware profile."""
    if not profiles:
        print_warning("No hardware profiles available. Using auto-detection.")
        return detect_hardware()
    
    print_info("Available hardware profiles:")
    for i, profile in enumerate(profiles, 1):
        print(f"  {i}. {profile.name} ({profile.id})")
        print(f"     RAM: {profile.ram_gb}GB, GPU: {profile.gpu_name} ({profile.gpu_vram_gb or 'N/A'}GB VRAM)")
    
    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Select hardware profile (1-{len(profiles)}):{Colors.ENDC} ").strip()
            if not choice:
                # Default to first profile
                return profiles[0]
            idx = int(choice) - 1
            if 0 <= idx < len(profiles):
                return profiles[idx]
            print_error(f"Please enter a number between 1 and {len(profiles)}")
        except ValueError:
            print_error("Please enter a valid number")

def prompt_tool_selection() -> str:
    """Prompt user to select hosting tool."""
    tools = get_available_tools()
    if not tools:
        print_error("No hosting tools available")
        return "llamacpp"  # fallback
    
    print_info("Available hosting tools:")
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool}")
    
    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Select hosting tool (1-{len(tools)}):{Colors.ENDC} ").strip()
            if not choice:
                return tools[0]  # default to first
            idx = int(choice) - 1
            if 0 <= idx < len(tools):
                return tools[idx]
            print_error(f"Please enter a number between 1 and {len(tools)}")
        except ValueError:
            print_error("Please enter a valid number")

def prompt_quality_mode() -> str:
    """Prompt user to select quality mode."""
    modes = ["balanced", "quality", "speed"]
    print_info("Quality modes:")
    for i, mode in enumerate(modes, 1):
        print(f"  {i}. {mode}")
    
    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Select quality mode (1-{len(modes)}):{Colors.ENDC} ").strip()
            if not choice:
                return "balanced"  # default
            idx = int(choice) - 1
            if 0 <= idx < len(modes):
                return modes[idx]
            print_error(f"Please enter a number between 1 and {len(modes)}")
        except ValueError:
            print_error("Please enter a valid number")

def main():
    """Main CLI entry point."""
    print_header("llmbeans - Local LLM Configuration Generator")
    print_info("This tool will help you generate optimal startup configurations for running LLMs locally.")
    
    try:
        # Step 1: Get model path
        model_path = prompt_model_path()
        
        # Step 2: Scan model
        model_info = scan_model(model_path)
        if not model_info:
            print_error("Failed to scan model. Exiting.")
            sys.exit(1)
        
        print_success(f"Model scanned: {model_info.name}")
        print_info(f"  Architecture: {model_info.architecture}")
        print_info(f"  Quantization: {model_info.quant_method} ({model_info.quant_bits} bits)")
        print_info(f"  Layers: {model_info.num_layers}")
        print_info(f"  Context length: {model_info.context_length}")
        print_info(f"  Estimated VRAM needed: {model_info.estimated_vram_gb:.1f} GB")
        
        # Step 3: Get hardware
        print_header("Hardware Detection")
        hardware_info = detect_hardware()
        hw_name = hardware_info.gpu_name or hardware_info.os
        print_info(f"Auto-detected hardware: {hw_name}")
        print_info(f"  RAM: {hardware_info.ram_total_gb}GB")
        print_info(f"  CPU: {hardware_info.cpu_cores} cores")
        print_info(f"  GPU: {hardware_info.gpu_name or 'None'}")
        if hardware_info.gpu_vram_gb:
            print_info(f"  VRAM: {hardware_info.gpu_vram_gb:.1f} GB")
        print_info(f"  Unified memory: {hardware_info.unified_memory}")
        print_info(f"  Memory bandwidth: {hardware_info.memory_bandwidth_gbps or 0:.1f} GB/s")
        
        # Ask if user wants to use auto-detected hardware or choose from profiles
        use_auto = input(f"\n{Colors.BOLD}Use auto-detected hardware? (y/n):{Colors.ENDC} ").strip().lower()
        if use_auto not in ('y', 'yes', ''):
            profiles = get_hardware_profiles()
            if profiles:
                hardware_info = prompt_hardware_selection(profiles)
                print_success(f"Selected hardware: {hardware_info.name}")
            else:
                print_warning("No profiles available, using auto-detected hardware.")
        
        # Step 4: Select hosting tool
        print_header("Hosting Tool Selection")
        selected_tool = prompt_tool_selection()
        print_success(f"Selected tool: {selected_tool}")
        
        # Step 5: Select quality mode
        print_header("Quality Mode Selection")
        quality_mode = prompt_quality_mode()
        print_success(f"Selected quality mode: {quality_mode}")
        
        # Step 6: Generate recommendation
        print_header("Generating Recommendation")
        print_info("Calculating optimal configuration...")
        
        recommendation = recommend(
            model=model_info,
            hardware=hardware_info,
            hosting_tool=selected_tool,
            quality_mode=quality_mode
        )
        
        # Step 7: Display results
        print_header("Recommendation Summary")
        
        # Generate and display summary
        summary = generate_summary(model_info, hardware_info, recommendation)
        print(summary)
        
        # Save outputs
        output_dir = Path.home() / "llmbeans-output"
        output_dir.mkdir(exist_ok=True)
        
        # Save summary
        summary_path = output_dir / "llmbeans-summary.txt"
        summary_path.write_text(summary)
        print_success(f"Summary saved to: {summary_path}")
        
        # Generate and save scripts
        script_files = write_scripts(model_info, recommendation, selected_tool, str(output_dir))
        for label, path in script_files.items():
            print_success(f"{label} script saved to: {path}")
        
        print_header("Next Steps")
        print_info("1. Review the summary above for key configuration details")
        print_info(f"2. Open the summary file: {summary_path}")
        print_info(f"3. Run the generated script to start your LLM server")
        print_info("4. Adjust parameters as needed based on your specific use case")
        
    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()