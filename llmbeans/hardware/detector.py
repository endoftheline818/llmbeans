# llmbeans/hardware/detector.py
"""System hardware detection — OS, RAM, GPU, disk."""

import os
import platform
import subprocess
from dataclasses import dataclass


@dataclass
class HardwareProfile:
    os: str
    cpu_cores: int
    ram_total_gb: float
    ram_free_gb: float
    gpu_vendor: str | None
    gpu_vram_gb: float | None
    gpu_name: str | None
    is_apple_silicon: bool
    unified_memory: bool
    metal_supported: bool
    disk_is_ssd: bool
    laptop_model: str | None
    memory_bandwidth_gbps: float | None


def detect_hardware() -> HardwareProfile | None:
    """Attempt to auto-detect system hardware. Returns None if detection fails."""
    try:
        import psutil
        ram = psutil.virtual_memory()
        ram_total_gb = round(ram.total / (1024**3), 1)
        ram_free_gb = round(ram.available / (1024**3), 1)
    except ImportError:
        ram_total_gb = 0.0
        ram_free_gb = 0.0

    os_type = platform.system().lower()
    cpu_cores = os.cpu_count() or 0
    is_apple = False
    metal = False
    unified = False
    gpu_vendor = None
    gpu_vram = None
    gpu_name = None
    laptop_model = None
    bandwidth = None
    disk_is_ssd = _detect_disk_is_ssd()

    if os_type == "darwin":
        is_apple = True
        unified = True
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True, timeout=5,
            )
            chip = result.stdout.strip()
            if "Apple" in chip:
                gpu_name = chip
                gpu_vendor = "apple"
                metal = True
            laptop_model = _detect_mac_model()
        except Exception:
            pass

    elif os_type == "linux":
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        ram_total_gb = round(int(line.split()[1]) / (1024**2), 1)
                        break
        except Exception:
            pass
        gpu_vendor, gpu_vram, gpu_name = _detect_linux_gpu()

    elif os_type == "windows":
        # If psutil returned 0, fall back to wmic for RAM
        if ram_total_gb == 0.0:
            ram_total_gb, ram_free_gb = _detect_windows_ram()
        gpu_info = _detect_windows_gpu()
        if gpu_info:
            gpu_vendor, gpu_vram, gpu_name = gpu_info

    return HardwareProfile(
        os=os_type,
        cpu_cores=cpu_cores,
        ram_total_gb=ram_total_gb,
        ram_free_gb=ram_free_gb,
        gpu_vendor=gpu_vendor,
        gpu_vram_gb=gpu_vram,
        gpu_name=gpu_name,
        is_apple_silicon=is_apple,
        unified_memory=unified,
        metal_supported=metal,
        disk_is_ssd=disk_is_ssd,
        laptop_model=laptop_model,
        memory_bandwidth_gbps=bandwidth,
    )


def _detect_windows_ram() -> tuple[float, float]:
    """Detect total and free RAM on Windows via wmic as psutil fallback."""
    total_gb = 0.0
    free_gb = 0.0
    try:
        result = subprocess.run(
            ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory", "/value"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("TotalVisibleMemorySize="):
                    kb = int(line.split("=")[1].strip())
                    total_gb = round(kb / (1024**2), 1)
                elif line.startswith("FreePhysicalMemory="):
                    kb = int(line.split("=")[1].strip())
                    free_gb = round(kb / (1024**2), 1)
    except Exception:
        pass
    return total_gb, free_gb


def _detect_disk_is_ssd() -> bool:
    """Detect if the primary disk is an SSD."""
    try:
        if platform.system() == "Darwin":
            result = subprocess.run(
                ["diskutil", "info", "/"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if "Solid State" in line and "Yes" in line:
                        return True
                    if "Solid State" in line and "No" in line:
                        return False
        elif platform.system() == "Linux":
            try:
                with open("/sys/block/$(mountpoint -d / | cut -d'/' -f3)/queue/rotational", "r") as f:
                    return f.read().strip() == "0"
            except Exception:
                for device in os.listdir("/sys/block/"):
                    if device.startswith(("sd", "nvme", "mmcblk")):
                        try:
                            with open(f"/sys/block/{device}/queue/rotational", "r") as f:
                                if f.read().strip() == "0":
                                    return True
                        except Exception:
                            continue
        elif platform.system() == "Windows":
            try:
                result = subprocess.run([
                    "powershell", "-command",
                    "Get-PhysicalMedia | Where-Object {$_.MediaType -eq 'SSD'} | Select-Object -First 1"
                ], capture_output=True, text=True, timeout=10)
                return result.returncode == 0 and result.stdout.strip() != ""
            except Exception:
                pass
    except Exception:
        pass
    return True


def _detect_mac_model() -> str | None:
    """Detect Mac model identifier."""
    try:
        result = subprocess.run(
            ["sysctl", "-n", "hw.model"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return None


def _detect_linux_gpu() -> tuple:
    """Detect GPU on Linux."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(",")
            name = parts[0].strip()
            vram = float(parts[1].strip().replace("MiB", "").replace("MB", "")) / 1024
            return ("nvidia", round(vram, 1), name)
    except Exception:
        pass
    return (None, None, None)


def _detect_windows_gpu() -> tuple | None:
    """Detect GPU on Windows. Tries nvidia-smi first, falls back to wmic."""
    # Prefer nvidia-smi — more accurate VRAM reading
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(",")
            name = parts[0].strip()
            vram_mib = float(parts[1].strip().replace("MiB", "").replace("MB", ""))
            vram_gb = round(vram_mib / 1024, 1)
            return ("nvidia", vram_gb, name)
    except Exception:
        pass

    # wmic fallback — parses AdapterRAM bytes → GB
    try:
        result = subprocess.run(
            ["wmic", "path", "win32_videocontroller", "get", "Name,AdapterRAM", "/value"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            name = None
            adapter_ram_bytes = None
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("Name="):
                    name = line.split("=", 1)[1].strip()
                elif line.startswith("AdapterRAM="):
                    val = line.split("=", 1)[1].strip()
                    if val.isdigit():
                        adapter_ram_bytes = int(val)
            if name:
                vendor = "nvidia" if "nvidia" in name.lower() else (
                    "amd" if "amd" in name.lower() or "radeon" in name.lower() else "intel"
                )
                vram_gb = None
                if adapter_ram_bytes and adapter_ram_bytes > 0:
                    vram_gb = round(adapter_ram_bytes / (1024**3), 1)
                    # wmic caps AdapterRAM at 4GB (32-bit overflow) — flag as unreliable
                    if vram_gb >= 4.0:
                        vram_gb = round(adapter_ram_bytes / (1024**3), 1)
                return (vendor, vram_gb, name)
    except Exception:
        pass
    return None
