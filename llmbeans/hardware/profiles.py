# llmbeans/hardware/profiles.py
"""Laptop and desktop hardware profile database.

Loads profiles from profiles.json and provides lookup helpers.
"""

import json
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
        # Apple Silicon: no hyperthreading on efficiency cores, but
        # performance cores have 2 threads.  Use cores * 1.5 as estimate.
        if getattr(hw, "is_apple_silicon", False):
            cpu_threads = max(cpu_cores, int(cpu_cores * 1.5))
        else:
            cpu_threads = cpu_cores * 2

    ram_gb = getattr(hw, "ram_total_gb", getattr(hw, "ram_gb", 0))

    # Build a human-readable name
    name = hw.laptop_model or "Auto-detected System"
    try:
        # Only run system_profiler on macOS
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

    return HardwareProfileEntry(
        id="auto-detected",
        name=name,
        year=0,
        ram_gb=int(ram_gb),
        ram_type="",
        cpu_cores=hw.cpu_cores,
        cpu_threads=cpu_threads,
        gpu_type="apple_silicon" if getattr(hw, "is_apple_silicon", False)
                else "discrete" if hw.gpu_vram_gb else "integrated",
        gpu_name=hw.gpu_name or "Unknown",
        gpu_vram_gb=hw.gpu_vram_gb,
        gpu_cores=0,
        unified_memory=hw.unified_memory,
        memory_bandwidth_gbps=hw.memory_bandwidth_gbps or 0,
        metal=getattr(hw, "metal_supported", getattr(hw, "metal", False)),
        cuda=False,
        cuda_compute=None,
        vram_bandwidth_gbps=None,
        ssd_recommended=getattr(hw, "disk_is_ssd", True),
        category="auto",
    )
