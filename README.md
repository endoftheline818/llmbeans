# llmbeans 🫘
Find the optimal way to run any LLM locally on your hardware.
Interactive CLI for llmbeans — model scanner + config recommender.

Guided terminal workflow:
  1. Pick a hosting tool (llama-cli, lmstudio, omlx, ollama)
  2. Select a model from the tool's default model directory
  3. Auto-detect or select hardware profile
  4. Choose quality mode (balanced / quality / speed)
  5. Get recommendation with flags, estimates, and warnings
  6. Write launch scripts

## Architecture

Design decisions are documented in `adr/adr.md`.

## Install

```bash
git clone git@github.com:tjax4376/llmbeans.git
cd llmbeans
pip install -e .
```

## Run

```bash
llmbeans
```
## Project folder structure description
```
llmbeans/
├── main.py              # Entry point, TUI orchestration
├── hardware/
│   ├── detector.py      # System scanning (OS, RAM, GPU, disk)
│   ├── profiles.json    # Laptop model database
│   └── estimator.py     # Performance estimation formula
├── models/
│   ├── scanner.py       # Model file format detection + metadata extraction
│   ├── gguf.py          # GGUF-specific reader
│   └── safetensors.py   # Safetensors/config.json reader
├── recommenders/
│   ├── engine.py        # Core recommendation logic
│   └── tools/
│       ├── llamacpp.py  # llama.cpp flag generation
│       ├── mlx.py       # MLX flag generation
│       ├── vllm.py      # vLLM flag generation
│       └── ollama.py    # Ollama flag generation
├── output/
│   └── script_gen.py    # Startup script + summary generation
└── tui/
    ├── app.py           # Textual app shell
    ├── screens.py       # Selection screens
    └── widgets.py       # Custom TUI components
```
## Status

v0.1.0 — in active development.

## Security
Please report vulnerabilities privately via GitHub security advisories if available, or by opening a minimal issue that does not disclose exploit details.
