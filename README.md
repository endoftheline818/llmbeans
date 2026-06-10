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

python --version
pip --version
git --version



### Macbook
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" # install homebrew if not installed
brew install python@3.12
brew install git
git clone https://github.com/tjax4376/llmbeans
cd llmbeans
python3 -m pip install --upgrade pip
pip install -e .
```

### Linux
```
sudo apt update
sudo apt install -y python3 python3-pip git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git clone https://github.com/tjax4376/llmbeans
cd llmbeans
python3 -m pip install --upgrade pip
pip install -e .
```

### Windows
```Powershell
Start PowerShell:
winget install --id Python.Python.3.12 -e
winget install --id Git.Git -e --source winget
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
python -m ensurepip --upgrade
python -m pip install --upgrade pip
git clone https://github.com/tjax4376/llmbeans
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
