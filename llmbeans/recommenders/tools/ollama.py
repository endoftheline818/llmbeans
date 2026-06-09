# llmbeans/recommenders/tools/ollama.py
"""Ollama flag generator — outputs a Modelfile."""

from llmbeans.recommenders.registry import register_tool

OLLAMA_PARAM_MAP = {
    "temperature": "0.7",
    "repeat_penalty": "1.1",
    "num_ctx": "{{context_length}}",
    "num_thread": "{{thread_count}}",
    "num_batch": "{{batch_size}}",
}


@register_tool("ollama")
def generate_flags(model, hardware, gpu_offload_layers, context_length,
                   batch_size, thread_count, quality_mode):
    params = {
        "temperature": "0.7",
        "repeat_penalty": "1.1",
        "num_ctx": str(context_length),
        "num_thread": str(thread_count),
        "num_batch": str(batch_size),
    }

    # Ollama auto-detects GPU, but we can hint
    flags = {}
    if hardware.cuda:
        flags["OLLAMA_FLASH_ATTENTION"] = "1"
    if hardware.metal:
        flags["OLLAMA_METAL"] = "1"

    # GPU layer override (via num_gpu_layers)
    total_layers = model.num_layers
    if hardware.cuda or hardware.metal:
        flags["num_gpu_layers"] = str(gpu_offload_layers)

    # Build Modelfile
    lines = ["FROM {{model_path}}", ""]

    for key, val in params.items():
        lines.append(f'PARAMETER {key} {val}')

    lines.append("")
    lines.append("# System prompt (optional)")
    lines.append('SYSTEM """You are a helpful assistant."""')

    modelfile = "\n".join(lines)

    # Command
    model_ref = model.source_path if not model.is_remote else model.source_path
    command = f"ollama create {model.name}-llmbeans -f Modelfile"
    command += f"\nollama run {model.name}-llmbeans"

    return {"flags": flags, "command": command, "extra_config": modelfile}