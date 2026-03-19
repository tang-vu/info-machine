"""Battery hardware inspector."""

from __future__ import annotations

from typing import Any

import psutil

from info_machine.core.inspector import BaseInspector, registry
from info_machine.utils.system import is_windows, wmi_query, safe_int


@registry.register
class BatteryInspector(BaseInspector):
    """Inspector for Battery information (laptops only)."""

    name = "battery"
    display_name = "Battery"

    def collect(self) -> dict[str, Any]:
        """Collect battery information including charge, health, and cycle count."""
        data: dict[str, Any] = {"present": False}

        battery = psutil.sensors_battery()
        if battery is None:
            data["present"] = False
            data["note"] = "No battery detected (desktop PC or battery not found)"
            return data

        data["present"] = True
        data["percent"] = battery.percent
        data["plugged_in"] = battery.power_plugged
        if battery.secsleft >= 0:
            hours = battery.secsleft // 3600
            minutes = (battery.secsleft % 3600) // 60
            data["time_remaining"] = f"{hours}h {minutes}m"
            data["seconds_remaining"] = battery.secsleft
        else:
            data["time_remaining"] = "Charging" if battery.power_plugged else "Unknown"

        # Detailed battery info via WMI (Windows)
        if is_windows():
            try:
                batteries = wmi_query(
                    "Win32_Battery",
                    [
                        "Name",
                        "Status",
                        "EstimatedChargeRemaining",
                        "DesignVoltage",
                        "BatteryStatus",
                    ],
                )
                if batteries:
                    bat = batteries[0]
                    data["name"] = (bat.get("Name") or "Unknown").strip()
                    data["status"] = bat.get("Status", "Unknown")
                    data["design_voltage_mv"] = safe_int(bat.get("DesignVoltage"))
            except Exception:
                pass

            # Try to get design capacity vs current capacity
            try:
                full_cap = wmi_query(
                    "BatteryFullChargedCapacity",
                    ["FullChargedCapacity"],
                )
                design_cap = wmi_query(
                    "BatteryStaticData",
                    ["DesignedCapacity", "ManufactureName", "SerialNumber", "CycleCount"],
                )

                if full_cap and design_cap:
                    current = safe_int(full_cap[0].get("FullChargedCapacity"))
                    designed = safe_int(design_cap[0].get("DesignedCapacity"))
                    if designed > 0 and current > 0:
                        data["design_capacity_mwh"] = designed
                        data["full_charge_capacity_mwh"] = current
                        data["battery_health_percent"] = round((current / designed) * 100, 1)
                        data["wear_level_percent"] = round(
                            ((designed - current) / designed) * 100, 1
                        )

                if design_cap:
                    d = design_cap[0]
                    data["manufacturer"] = (d.get("ManufactureName") or "Unknown").strip()
                    data["serial_number"] = (d.get("SerialNumber") or "N/A").strip()
                    cycle = safe_int(d.get("CycleCount"))
                    if cycle:
                        data["cycle_count"] = cycle
            except Exception:
                pass

        return data

    def health_score(self) -> int:
        """Score based on battery health percentage and cycle count."""
        data = self._data or self.safe_collect()

        if not data.get("present"):
            return -1  # No battery

        score = 100

        health = data.get("battery_health_percent")
        if health:
            if health < 40:
                score -= 50
            elif health < 60:
                score -= 30
            elif health < 80:
                score -= 15
            elif health < 90:
                score -= 5

        cycles = data.get("cycle_count", 0)
        if cycles > 1000:
            score -= 25
        elif cycles > 500:
            score -= 10
        elif cycles > 300:
            score -= 5

        return max(0, min(100, score))

    def health_details(self) -> str:
        """Describe battery health status."""
        data = self._data or self.safe_collect()

        if not data.get("present"):
            return "No battery (desktop PC)"

        parts = []
        health = data.get("battery_health_percent")
        if health:
            if health < 60:
                parts.append(f"⚠️ Battery degraded: {health}% capacity remaining")
            else:
                parts.append(f"Battery health: {health}%")

        cycles = data.get("cycle_count")
        if cycles:
            parts.append(f"Cycles: {cycles}")

        parts.append(f"Charge: {data.get('percent', 'N/A')}%")

        return " | ".join(parts)
