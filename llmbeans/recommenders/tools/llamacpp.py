# llmbeans/recommenders/tools/llamacpp.py
"""llama.cpp flag generator."""

from llmbeans.recommenders.registry import register_tool

@register_tool("llamacpp")
def generate_flags(model, hardware, gpu_offload_layers, context_length,
                   batch_size, thread_count, quality_mode):
    flags = {}
    total_layers = model.num_layers

    # GPU offload (-ngl): number of layers to offload to GPU
    # Bug fix: hardware.cuda was always False for auto-detected NVIDIA systems
    # because from_detection() hardcoded cuda=False. Now from_detection() sets
    # cuda=True when gpu_vendor=="nvidia", so this condition fires correctly.
    if hardware.cuda or hardware.metal:
        flags["-ngl"] = str(gpu_offload_layers)
    else:
        flags["-ngl"] = "0"

    # Context length (-c): 0 = model default
    flags["-c"] = str(context_length)

    # Thread count (-t): CPU threads for generation
    flags["-t"] = str(thread_count)

    # Batch size (-b): prompt batch size
    flags["-b"] = str(batch_size)

    # KV cache quantisation — use f16 if memory allows, q8_0 if tight
    model_size_gb = model.estimated_vram_gb
    available = hardware.gpu_vram_gb if not hardware.unified_memory else hardware.ram_gb

    if available and model_size_gb > available * 0.7:
        flags["-ctk"] = "q8_0"
        flags["-ctv"] = "q8_0"
    else:
        flags["-ctk"] = "f16"
        flags["-ctv"] = "f16"

    # Split mode for multi-GPU or partial offload
    if hardware.cuda and 0 < gpu_offload_layers < total_layers:
        flags["-sm"] = "layer"

    # Flash attention — enable on CUDA, skip on CPU/Metal
    if hardware.cuda:
        flags["-fa"] = ""

    # Memory lock for large models that fit in RAM
    if not hardware.unified_memory:
        if model_size_gb < hardware.ram_gb * 0.8:
            flags["-mlock"] = ""

    # RoPE scaling for long context
    if context_length > 8192:
        flags["--rope-scaling"] = "yarn"
        flags["--rope-freq-scale"] = "0.5"

    # Sampling defaults
    flags["--temp"] = "0.7"
    flags["--repeat-penalty"] = "1.1"

    # Build command string
    parts = ["llama-cli", "-m", model.source_path]
    for k, v in flags.items():
        if v == "":
            parts.append(k)
        else:
            parts.append(f"{k} {v}")

    command = " ".join(parts)

    return {"flags": flags, "command": command, "extra_config": None}
