"""Motherboard / BIOS hardware inspector."""

from __future__ import annotations

from typing import Any

from info_machine.core.inspector import BaseInspector, registry
from info_machine.utils.system import is_windows, wmi_query


@registry.register
class MotherboardInspector(BaseInspector):
    """Inspector for Motherboard and BIOS information."""

    name = "motherboard"
    display_name = "Motherboard / BIOS"

    def collect(self) -> dict[str, Any]:
        """Collect motherboard and BIOS information."""
        data: dict[str, Any] = {}

        if not is_windows():
            data["note"] = "Motherboard inspection requires Windows (WMI)"
            return data

        # Baseboard (motherboard) info
        try:
            boards = wmi_query(
                "Win32_BaseBoard",
                ["Manufacturer", "Product", "SerialNumber", "Version", "Status"],
            )
            if boards:
                board = boards[0]
                data["manufacturer"] = (board.get("Manufacturer") or "Unknown").strip()
                data["model"] = (board.get("Product") or "Unknown").strip()
                data["serial_number"] = (board.get("SerialNumber") or "N/A").strip()
                data["version"] = (board.get("Version") or "N/A").strip()
                data["status"] = board.get("Status", "Unknown")
        except Exception:
            pass

        # BIOS info
        try:
            bios_data = wmi_query(
                "Win32_BIOS",
                [
                    "Manufacturer",
                    "Name",
                    "Version",
                    "SMBIOSBIOSVersion",
                    "ReleaseDate",
                    "SerialNumber",
                ],
            )
            if bios_data:
                bios = bios_data[0]
                data["bios_manufacturer"] = (bios.get("Manufacturer") or "Unknown").strip()
                data["bios_name"] = (bios.get("Name") or "Unknown").strip()
                data["bios_version"] = (bios.get("SMBIOSBIOSVersion") or bios.get("Version") or "Unknown").strip()

                release = bios.get("ReleaseDate")
                if release and len(str(release)) >= 8:
                    # WMI date format: YYYYMMDDHHMMSS.ffffff+***
                    date_str = str(release)[:8]
                    try:
                        data["bios_date"] = (
                            f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                        )
                    except Exception:
                        data["bios_date"] = str(release)

                data["system_serial"] = (bios.get("SerialNumber") or "N/A").strip()
        except Exception:
            pass

        # System info (computer model, manufacturer)
        try:
            systems = wmi_query(
                "Win32_ComputerSystem",
                ["Manufacturer", "Model", "SystemType", "TotalPhysicalMemory"],
            )
            if systems:
                sys_info = systems[0]
                data["system_manufacturer"] = (sys_info.get("Manufacturer") or "Unknown").strip()
                data["system_model"] = (sys_info.get("Model") or "Unknown").strip()
                data["system_type"] = sys_info.get("SystemType", "Unknown")
        except Exception:
            pass

        return data

    def health_score(self) -> int:
        """Motherboard health based on status."""
        data = self._data or self.safe_collect()
        score = 100

        status = data.get("status", "")
        if status and status.lower() not in ("ok", ""):
            score -= 30

        if not data.get("model") and not data.get("manufacturer"):
            return -1

        return max(0, min(100, score))

    def health_details(self) -> str:
        """Describe motherboard health status."""
        data = self._data or self.safe_collect()
        parts = []

        manufacturer = data.get("manufacturer") or data.get("system_manufacturer", "")
        model = data.get("model") or data.get("system_model", "")
        if manufacturer or model:
            parts.append(f"{manufacturer} {model}".strip())

        bios_ver = data.get("bios_version")
        if bios_ver:
            parts.append(f"BIOS: {bios_ver}")

        status = data.get("status", "")
        if status:
            parts.append(f"Status: {status}")

        return " | ".join(parts) if parts else "No motherboard info available"
