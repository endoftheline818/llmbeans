#!/usr/bin/env bash
# llmbeans generated startup script for gemma-4-e4b-it-OptiQ-4bit
# Hosting tool: llamacpp
# Hardware: MacBook Pro 14" M4 16GB (2024)
# Generated: 2026-06-05 20:54
# Estimated speed: ~0.0 tok/s

set -euo pipefail

llama-cli -m /Users/tjax/.lmstudio/models/mlx-community/gemma-4-e4b-it-OptiQ-4bit -ngl 0 -c 32768 -t 8 -b 512 -tb 8 -ctk q8_0 -ctv q8_0  --temp 0.7 --repeat-penalty 1.1 --logit-bias
