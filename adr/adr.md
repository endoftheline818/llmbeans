# ADR — llmbeans

Architecture Decision Records for the llmbeans project.
Each decision below was made through interview/grilling on 2026-05-25.

---

## ADR-001: Target Audience

**Decision:** Universal audience — everyone and anyone who wants to run a model locally and get the best out of it.

**Implications:** The tool must be usable by novices (no CLI flag knowledge) and experts (who want to inspect/override). Output must be educational and transparent.

---

## ADR-002: Output Format

**Decision:** Generate a startup script with optimized flags + a summary of expected results (tokens/sec estimate, RAM/VRAM usage, context length achievable).

**Implications:** Two-part output: summary section first, then the script. The script must be platform-native (.sh on macOS/Linux, .bat on Windows).

---

## ADR-003: Script Delivery

**Decision:** Print the script inline in the terminal AND offer to save it as an executable file.

**Implications:** Immediate review + persistence. File must be written with execute permissions. c across the board for output.

---

## ADR-004: Hardware Input Method

**Decision:** User manually selects their OS, base RAM, and laptop model from curated lists. Auto-detection is NOT used for hardware.

**Implications:** Requires a bundled laptop profile database (hardcoded JSON). Simplifies cross-platform detection. Includes a free-text fallback for unlisted laptops.

---

## ADR-005: Hosting Tool Selection

**Decision:** User selects their model hosting app from a list: llama.cpp, LM Studio, MLX, vLLM, or Ollama.

**Implications:** Tool-specific flag generators needed for each hosting tool. Recommendation logic must be aware of each tool's capabilities and flag syntax.

---

## ADR-006: Model Format Support

**Decision:** Support ALL formats from v1: GGUF files, safetensors directories, HuggingFace repo IDs (remote), and by extension AWQ/GPTQ.

**Implications:** Need a flexible scanner abstraction with format-specific parsers. GGUF is self-contained (easiest). Safetensors require directory + config.json parsing. HF repo IDs require network access.

---

## ADR-007: Model Input Method

**Decision:** Accept both local file paths and HuggingFace repo IDs.

**Implications:** HF repo support enables pre-download recommendations ("for your hardware, grab Q6_K"). HuggingFace Hub library required. Must handle network errors gracefully.

---

## ADR-008: Hardware Detection Depth

**Decision:** Comprehensive scanning — total RAM, free/available RAM (real-time), GPU VRAM, Metal on macOS (M-series + unified memory), ROCm on AMD, CUDA compute capability, disk speed, CPU cores.

**Implications:** Platform-specific detection paths:
- macOS: `system_profiler` for chip, `vm_stat` for free memory, Metal API
- Linux: `/proc/meminfo`, `nvidia-smi` or `rocm-smi`, `lscpu`
- Windows: WMI queries, `nvidia-smi` from PATH

---

## ADR-009: Optimization Goal

**Decision:** Balanced by default, with user toggle for quality-biased or speed-biased recommendations.

**Implications:** Recommendation engine must expose a weighting parameter. Affects choices like quant level, context length, GPU offload layers.

---

## ADR-010: Expected Results & Estimation

**Decision:** Formula-based performance estimation in v1. Factors: model parameter count, quant bits, context length, offload ratio, hardware memory bandwidth. Community benchmark database deferred to v2.

**Implications:** Need to research and encode memory bandwidth figures for common hardware (M1-M4, NVIDIA laptop GPUs). Formula must account for KV cache size based on context length.

---

## ADR-011: Interface (v1)

**Decision:** Interactive TUI using Textual. CLI flags mode deferred to v2.

**Implications:** Natural fit for the selection flow (OS → laptop → hosting tool → model). InquirerPy or Textual for Python TUI. v2 adds `--model`, `--tool`, `--os` CLI args for scripting.

---

## ADR-012: Interface (v2)

**Decision:** Add optional CLI flags mode alongside TUI for power users and scripting.

**Implications:** Architecture must support both interactive and non-interactive modes from the start. Core logic must be decoupled from the TUI layer.

---

## ADR-013: Language & Framework

**Decision:** Python. huggingface_hub, safetensors, gguf for model scanning. Textual for TUI.

**Implications:** Best ML ecosystem support. Cross-platform. Progressive prototyping friendly. pip distribution.

---

## ADR-014: Distribution

**Decision:** `pip install llmbeans` from PyPI for v1. Standalone binary (PyInstaller/pyoxidizer) deferred until after v1 stabilizes.

**Implications:** Requires proper package structure, setup.cfg/pyproject.toml, entry points.

---

## ADR-015: Project Structure

**Decision:**

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

**Implications:** Component-by-component file structure. Each module is independently testable. Clear separation between scanning, recommendation, and output layers.

---

## Open Questions / Deferred

- **LM Studio integration:** LM Studio is primarily a GUI. Need to determine what "switches" mean for it (CLI launch args? config file?).
- **Community benchmark database:** Deferred to v2. Requires backend infrastructure.
- **Micro-benchmark validation:** Deferred to v2. Run a quick tokens/sec test to validate recommendations.
- **Standalone binary distribution:** Deferred to post-v1.
- **CLI flags mode:** Deferred to v2.
