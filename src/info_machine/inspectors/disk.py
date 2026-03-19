"""Disk / Storage hardware inspector."""

from __future__ import annotations

from typing import Any

import psutil

from info_machine.core.inspector import BaseInspector, registry
from info_machine.utils.system import (
    bytes_to_gb,
    bytes_to_readable,
    is_windows,
    safe_int,
    wmi_query,
)


@registry.register
class DiskInspector(BaseInspector):
    """Inspector for Disk / Storage information."""

    name = "disk"
    display_name = "Disk / Storage"

    def collect(self) -> dict[str, Any]:
        """Collect disk information including partitions, capacity, and drive type."""
        partitions = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append(
                    {
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "total_gb": bytes_to_gb(usage.total),
                        "used_gb": bytes_to_gb(usage.used),
                        "free_gb": bytes_to_gb(usage.free),
                        "usage_percent": usage.percent,
                        "total_readable": bytes_to_readable(usage.total),
                    }
                )
            except (PermissionError, OSError):
                partitions.append(
                    {
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "error": "Unable to read",
                    }
                )

        data: dict[str, Any] = {"partitions": partitions}

        # Physical disk details via WMI (Windows)
        if is_windows():
            try:
                disks = wmi_query(
                    "Win32_DiskDrive",
                    [
                        "Model",
                        "Size",
                        "MediaType",
                        "InterfaceType",
                        "SerialNumber",
                        "FirmwareRevision",
                        "Status",
                    ],
                )
                physical_disks = []
                for disk in disks:
                    size = safe_int(disk.get("Size"))
                    media = disk.get("MediaType", "")
                    interface = disk.get("InterfaceType", "")

                    # Determine drive type
                    drive_type = "Unknown"
                    if "SSD" in str(media) or "Solid" in str(media):
                        drive_type = "SSD"
                    elif "HDD" in str(media) or "Fixed" in str(media):
                        drive_type = "NVMe SSD" if "NVMe" in str(interface) else "HDD"

                    # Try to detect NVMe from model name
                    model = disk.get("Model", "")
                    if "NVMe" in str(model) or "nvme" in str(model).lower():
                        drive_type = "NVMe SSD"
                    elif "SSD" in str(model) or "ssd" in str(model).lower():
                        drive_type = "SSD"

                    physical_disks.append(
                        {
                            "model": str(model).strip(),
                            "size_gb": bytes_to_gb(size) if size else 0,
                            "size_readable": bytes_to_readable(size) if size else "Unknown",
                            "type": drive_type,
                            "interface": interface,
                            "serial": (disk.get("SerialNumber") or "N/A").strip(),
                            "firmware": (disk.get("FirmwareRevision") or "N/A").strip(),
                            "status": disk.get("Status", "Unknown"),
                        }
                    )

                data["physical_disks"] = physical_disks
            except Exception:
                pass

        # Disk I/O stats
        try:
            io = psutil.disk_io_counters()
            if io:
                data["io_read_gb"] = bytes_to_gb(io.read_bytes)
                data["io_write_gb"] = bytes_to_gb(io.write_bytes)
        except Exception:
            pass

        return data

    def health_score(self) -> int:
        """Score based on disk usage and drive status."""
        score = 100
        data = self._data or self.safe_collect()

        # Check partition usage
        for part in data.get("partitions", []):
            usage = part.get("usage_percent", 0)
            if usage > 95:
                score -= 25
            elif usage > 90:
                score -= 15
            elif usage > 80:
                score -= 5

        # Check physical disk status
        for disk in data.get("physical_disks", []):
            status = disk.get("status", "")
            if status and status.lower() not in ("ok", "online", ""):
                score -= 30

        return max(0, min(100, score))

    def health_details(self) -> str:
        """Describe disk health status."""
        data = self._data or self.safe_collect()
        parts = []

        physical = data.get("physical_disks", [])
        if physical:
            for disk in physical:
                parts.append(f"{disk['model']} ({disk['type']}, {disk['size_readable']})")

        partitions = data.get("partitions", [])
        critical = [p for p in partitions if p.get("usage_percent", 0) > 90]
        if critical:
            drives = ", ".join(p["mountpoint"] for p in critical)
            parts.append(f"⚠️ Low space: {drives}")

        return " | ".join(parts) if parts else "No disk info available"
