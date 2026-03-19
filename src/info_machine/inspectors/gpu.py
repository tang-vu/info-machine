"""GPU / Graphics hardware inspector."""

from __future__ import annotations

from typing import Any

from info_machine.core.inspector import BaseInspector, registry
from info_machine.utils.system import bytes_to_readable, is_windows, safe_int, wmi_query


@registry.register
class GpuInspector(BaseInspector):
    """Inspector for GPU / Graphics Card information."""

    name = "gpu"
    display_name = "GPU / Graphics"

    def collect(self) -> dict[str, Any]:
        """Collect GPU information including model, VRAM, driver, and utilization."""
        data: dict[str, Any] = {"gpus": []}

        # Try GPUtil first (NVIDIA GPUs)
        try:
            import GPUtil

            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                data["gpus"].append(
                    {
                        "id": gpu.id,
                        "name": gpu.name,
                        "driver": gpu.driver,
                        "vram_total_mb": round(gpu.memoryTotal, 0),
                        "vram_used_mb": round(gpu.memoryUsed, 0),
                        "vram_free_mb": round(gpu.memoryFree, 0),
                        "vram_usage_percent": round(gpu.memoryUtil * 100, 1),
                        "gpu_load_percent": round(gpu.load * 100, 1),
                        "temperature_c": gpu.temperature,
                    }
                )
        except Exception:
            pass

        # WMI fallback (all GPUs including integrated)
        if is_windows():
            try:
                wmi_gpus = wmi_query(
                    "Win32_VideoController",
                    [
                        "Name",
                        "AdapterRAM",
                        "DriverVersion",
                        "DriverDate",
                        "VideoProcessor",
                        "CurrentRefreshRate",
                        "VideoModeDescription",
                        "Status",
                    ],
                )

                # Use WMI data if GPUtil found nothing, or to supplement with integrated GPUs
                existing_names = {g["name"] for g in data["gpus"]}
                for gpu in wmi_gpus:
                    name = (gpu.get("Name") or "Unknown").strip()
                    if name not in existing_names:
                        vram = safe_int(gpu.get("AdapterRAM"))
                        data["gpus"].append(
                            {
                                "name": name,
                                "driver": gpu.get("DriverVersion", "Unknown"),
                                "vram_total_mb": round(vram / (1024 * 1024)) if vram else 0,
                                "vram_readable": bytes_to_readable(vram) if vram else "Unknown",
                                "video_processor": gpu.get("VideoProcessor", "Unknown"),
                                "refresh_rate": gpu.get("CurrentRefreshRate"),
                                "video_mode": gpu.get("VideoModeDescription", "Unknown"),
                                "status": gpu.get("Status", "Unknown"),
                            }
                        )
            except Exception:
                pass

        data["gpu_count"] = len(data["gpus"])
        return data

    def health_score(self) -> int:
        """Score based on GPU temperature and VRAM pressure."""
        score = 100
        data = self._data or self.safe_collect()

        for gpu in data.get("gpus", []):
            temp = gpu.get("temperature_c")
            if temp:
                if temp > 95:
                    score -= 40
                elif temp > 85:
                    score -= 20
                elif temp > 75:
                    score -= 10

            vram_usage = gpu.get("vram_usage_percent")
            if vram_usage and vram_usage > 95:
                score -= 15

            status = gpu.get("status", "")
            if status and status.lower() not in ("ok", ""):
                score -= 20

        if not data.get("gpus"):
            return -1  # No GPU detected

        return max(0, min(100, score))

    def health_details(self) -> str:
        """Describe GPU health status."""
        data = self._data or self.safe_collect()
        gpus = data.get("gpus", [])

        if not gpus:
            return "No GPU detected"

        parts = []
        for gpu in gpus:
            name = gpu.get("name", "Unknown")
            temp = gpu.get("temperature_c")
            temp_str = f"{temp}°C" if temp else "N/A"
            parts.append(f"{name} (Temp: {temp_str})")

        return " | ".join(parts)
