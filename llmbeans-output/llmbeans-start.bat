@echo off
REM llmbeans generated startup script for gemma-4-e4b-it-OptiQ-4bit
REM Hosting tool: llamacpp
REM Hardware: MacBook Pro 14" M4 16GB (2024)
REM Generated: 2026-06-05 20:54
REM Estimated speed: ~0.0 tok/s

./llama-cli -m /Users/tjax/.lmstudio/models/mlx-community/gemma-4-e4b-it-OptiQ-4bit -ngl 0 -c 4096 -t 8 -b 512 -tb 8 -ctk q8_0 -ctv q8_0 -fa --temp 0.7 --repeat-penalty 1.1 --logit-bias

pause