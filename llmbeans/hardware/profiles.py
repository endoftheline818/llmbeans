# llmbeans/hardware/profiles.py
"""Laptop and desktop hardware profile database.

Loads profiles from profiles.json and provides lookup helpers.
"""

import json
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


PROFILES_PATH = Path(__file__).parent / "profiles.json"


@dataclass
class HardwareProfileEntry:
    id: str
    name: str
    year: int
    ram_gb: int
    ram_type: str
    cpu_cores: int
    cpu_threads: int
    gpu_type: str          # "integrated" | "discrete" | "apple_silicon"
    gpu_name: str
    gpu_vram_gb: Optional[float]
    gpu_cores: int
    unified_memory: bool
    memory_bandwidth_gbps: float
    metal: bool
    cuda: bool
    cuda_compute: Optional[str]
    vram_bandwidth_gbps: Optional[float]
    ssd_recommended: bool
    category: str


# ── NVIDIA VRAM bandwidth lookup table ────────────────────────────────────────
# Used by from_detection() when nvidia-smi doesn't report bandwidth directly.
# Values are approximate VRAM bandwidth in GB/s for common consumer GPUs.
# Source: official NVIDIA specs.
_NVIDIA_VRAM_BANDWIDTH: dict[str, float] = {
    # RTX 40-series desktop
    "RTX 4090": 1008.0,
    "RTX 4080 SUPER": 736.3,
    "RTX 4080": 716.8,
    "RTX 4070 Ti SUPER": 672.3,
    "RTX 4070 Ti": 504.2,
    "RTX 4070 SUPER": 504.2,
    "RTX 4070": 504.2,
    "RTX 4060 Ti": 288.0,
    "RTX 4060": 272.0,
    # RTX 40-series laptop
    "RTX 4090 Laptop": 576.0,
    "RTX 4080 Laptop": 432.0,
    "RTX 4070 Laptop": 256.0,
    "RTX 4060 Laptop": 192.0,
    # RTX 30-series desktop
    "RTX 3090 Ti": 1008.0,
    "RTX 3090": 936.2,
    "RTX 3080 Ti": 912.4,
    "RTX 3080": 760.3,
    "RTX 3070 Ti": 608.0,
    "RTX 3070": 448.0,
    "RTX 3060 Ti": 448.0,
    "RTX 3060": 360.0,
    # RTX 30-series laptop
    "RTX 3080 Laptop": 384.0,
    "RTX 3070 Laptop": 256.0,
    "RTX 3060 Laptop": 192.0,
    # RTX 20-series
    "RTX 2080 Ti": 616.0,
    "RTX 2080 SUPER": 496.1,
    "RTX 2080": 448.0,
    "RTX 2070 SUPER": 448.0,
    "RTX 2070": 448.0,
    "RTX 2060 SUPER": 448.0,
    "RTX 2060": 336.1,
}


def _lookup_nvidia_bandwidth(gpu_name: str) -> Optional[float]:
    """Return known VRAM bandwidth for a GPU name string, or None.

    Performs a substring match so "NVIDIA GeForce RTX 4070 Ti" hits the
    "RTX 4070 Ti" key correctly.
    """
    if not gpu_name:
        return None
    upper = gpu_name.upper()
    # Sort by key length descending so more-specific keys win
    # (e.g. "RTX 4070 Ti" beats "RTX 4070" for "RTX 4070 Ti SUPER")
    for key in sorted(_NVIDIA_VRAM_BANDWIDTH, key=len, reverse=True):
        if key.upper() in upper:
            return _NVIDIA_VRAM_BANDWIDTH[key]
    return None


def load_profiles() -> list[HardwareProfileEntry]:
    """Load all hardware profiles from profiles.json."""
    with open(PROFILES_PATH) as f:
        data = json.load(f)

    profiles = []
    for category, entries in data.items():
        if category == "meta":
            continue
        for entry in entries:
            profiles.append(HardwareProfileEntry(
                id=entry["id"],
                name=entry["name"],
                year=entry["year"],
                ram_gb=entry["ram_gb"],
                ram_type=entry["ram_type"],
                cpu_cores=entry["cpu_cores"],
                cpu_threads=entry["cpu_threads"],
                gpu_type=entry["gpu_type"],
                gpu_name=entry["gpu_name"],
                gpu_vram_gb=entry.get("gpu_vram_gb"),
                gpu_cores=entry["gpu_cores"],
                unified_memory=entry["unified_memory"],
                memory_bandwidth_gbps=entry["memory_bandwidth_gbps"],
                metal=entry.get("metal", False),
                cuda=entry.get("cuda", False),
                cuda_compute=entry.get("cuda_compute"),
                vram_bandwidth_gbps=entry.get("vram_bandwidth_gbps"),
                ssd_recommended=entry.get("ssd_recommended", True),
                category=category,
            ))
    return profiles


def get_profiles_by_category(category: str) -> list[HardwareProfileEntry]:
    """Get all profiles in a category (e.g. 'apple', 'windows_nvidia')."""
    return [p for p in load_profiles() if p.category == category]


def get_profile_by_id(profile_id: str) -> Optional[HardwareProfileEntry]:
    """Look up a single profile by its ID."""
    for p in load_profiles():
        if p.id == profile_id:
            return p
    return None


def get_categories() -> list[str]:
    """Return available profile categories."""
    with open(PROFILES_PATH) as f:
        data = json.load(f)
    return [k for k in data if k != "meta"]


def from_detection(hw) -> HardwareProfileEntry:
    """Convert a HardwareProfile (from detector) into a HardwareProfileEntry.

    The detector and the profile database use different dataclasses with
    overlapping but not identical fields.  This bridges the gap so the
    auto-detected hardware can be used everywhere a profile entry is
    expected.
    """
    # Derive cpu_threads: on Apple Silicon physical ≈ logical, otherwise
    # assume 2× cores when we can't detect.
    cpu_threads = getattr(hw, "cpu_threads", None)
    if cpu_threads is None:
        cpu_cores = hw.cpu_cores
        if getattr(hw, "is_apple_silicon", False):
            cpu_threads = max(cpu_cores, int(cpu_cores * 1.5))
        else:
            cpu_threads = cpu_cores * 2

    ram_gb = getattr(hw, "ram_total_gb", getattr(hw, "ram_gb", 0))

    # Build a human-readable name
    name = hw.laptop_model or "Auto-detected System"
    try:
        if platform.system() == "Darwin":
            import subprocess as _sp
            result = _sp.run(
                ["system_profiler", "SPHardwareDataType", "-json"],
                capture_output=True, text=True, timeout=5,
            )
            import json as _json
            data = _json.loads(result.stdout)
            hw_data = data.get("SPHardwareDataType", [{}])[0]
            machine_name = hw_data.get("machine_name", "")
            chip_type = hw_data.get("chip_type", "")
            if machine_name and chip_type:
                name = f"{machine_name} ({chip_type})"
            elif chip_type:
                name = chip_type
            elif machine_name:
                name = machine_name
    except Exception:
        pass

    # ── Derive cuda flag from gpu_vendor ──────────────────────────────────────
    # Bug fix: was hardcoded to False, causing -ngl to always be 0 for NVIDIA
    # GPUs and tokens/sec to always be 0.0 (no bandwidth path was taken).
    is_nvidia = getattr(hw, "gpu_vendor", "") == "nvidia"
    is_apple_silicon = getattr(hw, "is_apple_silicon", False)

    # ── VRAM bandwidth lookup ─────────────────────────────────────────────────
    # Bug fix: detector.py never populated memory_bandwidth_gbps for NVIDIA,
    # leaving it None → 0 → estimate_tokens_per_sec() returned 0.0.
    # Use the lookup table to fill in a known value for common GPUs.
    vram_bw: Optional[float] = None
    if is_nvidia:
        vram_bw = _lookup_nvidia_bandwidth(hw.gpu_name or "")

    # memory_bandwidth_gbps on the profile entry is the *system* RAM bandwidth
    # (used as fallback when no GPU). For auto-detected non-Apple systems we
    # don't have a reliable figure, so default to a conservative DDR4 estimate.
    system_ram_bandwidth = getattr(hw, "memory_bandwidth_gbps", None) or 50.0

    # ── RAM type default ──────────────────────────────────────────────────────
    # Bug fix: was always "" for non-Apple, showing "RAM: 15 GB ()" in summary.
    # Default to DDR4 for Linux/Windows when we can't detect the actual type.
    ram_type = ""
    if is_apple_silicon:
        ram_type = "LPDDR5X"
    else:
        ram_type = "DDR4"

    return HardwareProfileEntry(
        id="auto-detected",
        name=name,
        year=0,
        ram_gb=int(ram_gb),
        ram_type=ram_type,
        cpu_cores=hw.cpu_cores,
        cpu_threads=cpu_threads,
        gpu_type="apple_silicon" if is_apple_silicon
                else "discrete" if hw.gpu_vram_gb else "integrated",
        gpu_name=hw.gpu_name or "Unknown",
        gpu_vram_gb=hw.gpu_vram_gb,
        gpu_cores=0,
        unified_memory=hw.unified_memory,
        memory_bandwidth_gbps=system_ram_bandwidth,
        metal=getattr(hw, "metal_supported", getattr(hw, "metal", False)),
        cuda=is_nvidia,
        cuda_compute=None,
        vram_bandwidth_gbps=vram_bw,
        ssd_recommended=getattr(hw, "disk_is_ssd", True),
        category="auto",
    )
