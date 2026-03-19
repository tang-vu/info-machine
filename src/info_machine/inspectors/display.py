"""Display / Monitor hardware inspector."""

from __future__ import annotations

from typing import Any

from info_machine.core.inspector import BaseInspector, registry
from info_machine.utils.system import is_windows, wmi_query, safe_int


@registry.register
class DisplayInspector(BaseInspector):
    """Inspector for Display / Monitor information."""

    name = "display"
    display_name = "Display / Monitor"

    def collect(self) -> dict[str, Any]:
        """Collect display information including resolution, refresh rate, and monitor details."""
        data: dict[str, Any] = {"monitors": []}

        # Get screen resolution via ctypes (Windows)
        if is_windows():
            try:
                import ctypes

                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
                data["screen_width"] = user32.GetSystemMetrics(0)
                data["screen_height"] = user32.GetSystemMetrics(1)
                data["resolution"] = f"{data['screen_width']}x{data['screen_height']}"
            except Exception:
                pass

            # Monitor details via WMI
            try:
                monitors = wmi_query(
                    "Win32_DesktopMonitor",
                    [
                        "Name",
                        "MonitorManufacturer",
                        "MonitorType",
                        "ScreenWidth",
                        "ScreenHeight",
                        "Status",
                    ],
                )
                for mon in monitors:
                    data["monitors"].append(
                        {
                            "name": (mon.get("Name") or "Unknown").strip(),
                            "manufacturer": (mon.get("MonitorManufacturer") or "Unknown").strip(),
                            "type": (mon.get("MonitorType") or "Unknown").strip(),
                            "width": safe_int(mon.get("ScreenWidth")),
                            "height": safe_int(mon.get("ScreenHeight")),
                            "status": mon.get("Status", "Unknown"),
                        }
                    )
            except Exception:
                pass

            # Video controller info for refresh rate and color depth
            try:
                controllers = wmi_query(
                    "Win32_VideoController",
                    [
                        "CurrentRefreshRate",
                        "CurrentBitsPerPixel",
                        "CurrentHorizontalResolution",
                        "CurrentVerticalResolution",
                        "VideoModeDescription",
                    ],
                )
                if controllers:
                    ctrl = controllers[0]
                    data["refresh_rate_hz"] = safe_int(ctrl.get("CurrentRefreshRate"))
                    data["color_depth_bits"] = safe_int(ctrl.get("CurrentBitsPerPixel"))
                    data["video_mode"] = ctrl.get("VideoModeDescription", "Unknown")
            except Exception:
                pass

        data["monitor_count"] = len(data["monitors"])
        return data

    def health_score(self) -> int:
        """Display health is generally stable; score based on status."""
        data = self._data or self.safe_collect()
        score = 100

        for mon in data.get("monitors", []):
            status = mon.get("status", "")
            if status and status.lower() not in ("ok", ""):
                score -= 20

        if not data.get("monitors") and not data.get("resolution"):
            return -1

        return max(0, min(100, score))

    def health_details(self) -> str:
        """Describe display health status."""
        data = self._data or self.safe_collect()
        parts = []

        res = data.get("resolution")
        if res:
            parts.append(f"Resolution: {res}")

        refresh = data.get("refresh_rate_hz")
        if refresh:
            parts.append(f"Refresh: {refresh}Hz")

        count = data.get("monitor_count", 0)
        parts.append(f"Monitors: {count}")

        return " | ".join(parts) if parts else "No display info available"
