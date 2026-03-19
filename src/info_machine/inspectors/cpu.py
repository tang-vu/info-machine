"""CPU hardware inspector."""

from __future__ import annotations

from typing import Any

import psutil

from info_machine.core.inspector import BaseInspector, registry
from info_machine.utils.system import is_windows, safe_int, wmi_query


@registry.register
class CpuInspector(BaseInspector):
    """Inspector for CPU / Processor information."""

    name = "cpu"
    display_name = "CPU / Processor"

    def collect(self) -> dict[str, Any]:
        """Collect CPU information including model, cores, frequency, and usage."""
        data: dict[str, Any] = {
            "physical_cores": psutil.cpu_count(logical=False) or 0,
            "logical_cores": psutil.cpu_count(logical=True) or 0,
            "usage_percent": psutil.cpu_percent(interval=1),
            "per_core_usage": psutil.cpu_percent(interval=0.5, percpu=True),
        }

        # CPU frequency
        freq = psutil.cpu_freq()
        if freq:
            data["frequency_current_mhz"] = round(freq.current, 0)
            data["frequency_min_mhz"] = round(freq.min, 0)
            data["frequency_max_mhz"] = round(freq.max, 0)

        # Detailed info via py-cpuinfo
        try:
            import cpuinfo

            info = cpuinfo.get_cpu_info()
            data["model"] = info.get("brand_raw", "Unknown")
            data["architecture"] = info.get("arch", "Unknown")
            data["bits"] = info.get("bits", 0)
            data["vendor"] = info.get("vendor_id_raw", "Unknown")
            l2 = info.get("l2_cache_size")
            l3 = info.get("l3_cache_size")
            if l2:
                data["l2_cache"] = str(l2)
            if l3:
                data["l3_cache"] = str(l3)
        except Exception:
            data["model"] = "Unknown"

        # WMI details (Windows)
        if is_windows():
            try:
                wmi_data = wmi_query(
                    "Win32_Processor",
                    ["Name", "MaxClockSpeed", "CurrentVoltage", "SocketDesignation"],
                )
                if wmi_data:
                    cpu = wmi_data[0]
                    if not data.get("model") or data["model"] == "Unknown":
                        data["model"] = cpu.get("Name", "Unknown")
                    data["socket"] = cpu.get("SocketDesignation", "Unknown")
                    data["max_clock_speed_mhz"] = safe_int(cpu.get("MaxClockSpeed"))
            except Exception:
                pass

        # CPU temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for _name, entries in temps.items():
                    if entries:
                        data["temperature_c"] = entries[0].current
                        break
        except (AttributeError, Exception):
            pass

        return data

    def health_score(self) -> int:
        """Score based on CPU temperature and usage patterns."""
        score = 100
        data = self._data or self.safe_collect()

        # Temperature penalty
        temp = data.get("temperature_c")
        if temp:
            if temp > 90:
                score -= 40
            elif temp > 80:
                score -= 20
            elif temp > 70:
                score -= 10

        # High sustained usage penalty
        usage = data.get("usage_percent", 0)
        if usage > 95:
            score -= 15
        elif usage > 85:
            score -= 5

        return max(0, min(100, score))

    def health_details(self) -> str:
        """Describe CPU health status."""
        data = self._data or self.safe_collect()
        parts = []

        temp = data.get("temperature_c")
        if temp:
            if temp > 90:
                parts.append(f"⚠️ Critical temperature: {temp}°C")
            elif temp > 80:
                parts.append(f"⚠️ High temperature: {temp}°C")
            else:
                parts.append(f"Temperature: {temp}°C (Normal)")
        else:
            parts.append("Temperature: N/A")

        usage = data.get("usage_percent", 0)
        parts.append(f"Current usage: {usage}%")

        return " | ".join(parts)
