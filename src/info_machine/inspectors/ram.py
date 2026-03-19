"""RAM / Memory hardware inspector."""

from __future__ import annotations

from typing import Any

import psutil

from info_machine.core.inspector import BaseInspector, registry
from info_machine.utils.system import is_windows, wmi_query, safe_int, bytes_to_gb, bytes_to_readable


@registry.register
class RamInspector(BaseInspector):
    """Inspector for RAM / Memory information."""

    name = "ram"
    display_name = "RAM / Memory"

    def collect(self) -> dict[str, Any]:
        """Collect RAM information including capacity, usage, speed, and slot details."""
        mem = psutil.virtual_memory()
        data: dict[str, Any] = {
            "total_bytes": mem.total,
            "total_readable": bytes_to_readable(mem.total),
            "total_gb": bytes_to_gb(mem.total),
            "available_gb": bytes_to_gb(mem.available),
            "used_gb": bytes_to_gb(mem.used),
            "usage_percent": mem.percent,
        }

        # Swap memory
        swap = psutil.swap_memory()
        data["swap_total_gb"] = bytes_to_gb(swap.total)
        data["swap_used_gb"] = bytes_to_gb(swap.used)
        data["swap_percent"] = swap.percent

        # Detailed slot info via WMI (Windows)
        if is_windows():
            try:
                sticks = wmi_query(
                    "Win32_PhysicalMemory",
                    [
                        "BankLabel",
                        "Capacity",
                        "Speed",
                        "Manufacturer",
                        "MemoryType",
                        "FormFactor",
                        "SMBIOSMemoryType",
                        "PartNumber",
                    ],
                )
                slots = []
                for stick in sticks:
                    capacity = safe_int(stick.get("Capacity"))
                    speed = safe_int(stick.get("Speed"))
                    smbios_type = safe_int(stick.get("SMBIOSMemoryType"))

                    # DDR type from SMBIOS
                    ddr_map = {
                        20: "DDR",
                        21: "DDR2",
                        22: "DDR2",
                        24: "DDR3",
                        26: "DDR4",
                        34: "DDR5",
                    }
                    ddr_type = ddr_map.get(smbios_type, f"Type {smbios_type}")

                    slots.append(
                        {
                            "bank": stick.get("BankLabel", "Unknown"),
                            "capacity_gb": bytes_to_gb(capacity) if capacity else 0,
                            "speed_mhz": speed,
                            "type": ddr_type,
                            "manufacturer": (stick.get("Manufacturer") or "Unknown").strip(),
                            "part_number": (stick.get("PartNumber") or "Unknown").strip(),
                        }
                    )

                data["slots"] = slots
                data["slot_count"] = len(slots)
                if slots:
                    data["speed_mhz"] = slots[0]["speed_mhz"]
                    data["type"] = slots[0]["type"]
            except Exception:
                pass

        return data

    def health_score(self) -> int:
        """Score based on memory usage and swap pressure."""
        score = 100
        data = self._data or self.safe_collect()

        usage = data.get("usage_percent", 0)
        if usage > 95:
            score -= 30
        elif usage > 85:
            score -= 15
        elif usage > 75:
            score -= 5

        swap_percent = data.get("swap_percent", 0)
        if swap_percent > 80:
            score -= 20
        elif swap_percent > 50:
            score -= 10

        return max(0, min(100, score))

    def health_details(self) -> str:
        """Describe RAM health status."""
        data = self._data or self.safe_collect()
        usage = data.get("usage_percent", 0)
        total = data.get("total_readable", "Unknown")

        if usage > 90:
            status = "⚠️ Critical memory pressure"
        elif usage > 75:
            status = "⚠️ High memory usage"
        else:
            status = "Normal"

        return f"Total: {total} | Usage: {usage}% | Status: {status}"
