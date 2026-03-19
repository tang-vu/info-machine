"""Network adapter hardware inspector."""

from __future__ import annotations

from typing import Any

import psutil

from info_machine.core.inspector import BaseInspector, registry
from info_machine.utils.system import bytes_to_readable, is_windows, wmi_query


@registry.register
class NetworkInspector(BaseInspector):
    """Inspector for Network adapter information."""

    name = "network"
    display_name = "Network Adapters"

    def collect(self) -> dict[str, Any]:
        """Collect network adapter information including MAC, speed, and IP addresses."""
        data: dict[str, Any] = {"adapters": []}

        # Network interfaces from psutil
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        for iface_name, iface_addrs in addrs.items():
            adapter: dict[str, Any] = {
                "name": iface_name,
                "ipv4": [],
                "ipv6": [],
                "mac": None,
            }

            for addr in iface_addrs:
                if addr.family.name == "AF_INET":
                    adapter["ipv4"].append(addr.address)
                elif addr.family.name == "AF_INET6":
                    adapter["ipv6"].append(addr.address)
                elif addr.family.name == "AF_LINK" or addr.family.value == -1:
                    adapter["mac"] = addr.address

            # Interface stats
            if iface_name in stats:
                st = stats[iface_name]
                adapter["is_up"] = st.isup
                adapter["speed_mbps"] = st.speed
                adapter["mtu"] = st.mtu

            data["adapters"].append(adapter)

        # Network I/O
        try:
            io = psutil.net_io_counters()
            data["total_bytes_sent"] = io.bytes_sent
            data["total_bytes_recv"] = io.bytes_recv
            data["sent_readable"] = bytes_to_readable(io.bytes_sent)
            data["recv_readable"] = bytes_to_readable(io.bytes_recv)
        except Exception:
            pass

        # WMI details (Windows) for physical adapter info
        if is_windows():
            try:
                wmi_adapters = wmi_query(
                    "Win32_NetworkAdapter",
                    [
                        "Name",
                        "MACAddress",
                        "Speed",
                        "NetConnectionStatus",
                        "Manufacturer",
                        "PhysicalAdapter",
                        "NetConnectionID",
                    ],
                )
                physical = []
                for a in wmi_adapters:
                    if a.get("PhysicalAdapter"):
                        speed = a.get("Speed")
                        physical.append(
                            {
                                "name": (a.get("Name") or "Unknown").strip(),
                                "connection_name": a.get("NetConnectionID", ""),
                                "mac": a.get("MACAddress", "N/A"),
                                "speed_bps": int(speed) if speed else 0,
                                "speed_readable": bytes_to_readable(int(speed)) if speed else "N/A",
                                "manufacturer": (a.get("Manufacturer") or "Unknown").strip(),
                                "connected": a.get("NetConnectionStatus") == 2,
                            }
                        )
                data["physical_adapters"] = physical
            except Exception:
                pass

        return data

    def health_score(self) -> int:
        """Network health based on connectivity."""
        data = self._data or self.safe_collect()
        score = 100

        adapters = data.get("adapters", [])
        active = [a for a in adapters if a.get("is_up")]

        if not active:
            score -= 50

        return max(0, min(100, score))

    def health_details(self) -> str:
        """Describe network health status."""
        data = self._data or self.safe_collect()
        adapters = data.get("adapters", [])
        active = [a for a in adapters if a.get("is_up")]

        return f"Adapters: {len(adapters)} total, {len(active)} active"
