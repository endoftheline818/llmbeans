# llmbeans

Find the optimal way to run any LLM locally on your hardware.
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

## Architecture

Design decisions are documented in `adr/adr.md`.

## Install

```bash
pip install -e .
```

## Run

```bash
llmbeans
```
