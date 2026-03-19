"""System detection and WMI helper utilities."""

from __future__ import annotations

import platform
import sys
from typing import Any


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def get_os_info() -> dict[str, str]:
    """Get operating system information.

    Returns:
        Dict with OS name, version, architecture, and hostname.
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
    }


def wmi_query(wmi_class: str, properties: list[str] | None = None) -> list[dict[str, Any]]:
    """Execute a WMI query and return results as list of dicts.

    Args:
        wmi_class: WMI class to query (e.g., "Win32_Processor").
        properties: Specific properties to retrieve. If None, retrieves all.

    Returns:
        List of dicts, one per WMI object found.

    Raises:
        RuntimeError: If not running on Windows or WMI unavailable.
    """
    if not is_windows():
        raise RuntimeError("WMI queries are only available on Windows")

    try:
        import wmi as wmi_module

        c = wmi_module.WMI()
        wmi_class_obj = getattr(c, wmi_class)
        results = []

        for obj in wmi_class_obj():
            if properties:
                item = {}
                for prop in properties:
                    try:
                        item[prop] = getattr(obj, prop, None)
                    except Exception:
                        item[prop] = None
                results.append(item)
            else:
                item = {}
                try:
                    for prop in obj.properties:
                        try:
                            item[prop] = getattr(obj, prop, None)
                        except Exception:
                            item[prop] = None
                except Exception:
                    pass
                results.append(item)

        return results
    except ImportError:
        raise RuntimeError("WMI module not installed. Install with: pip install wmi")
    except Exception as e:
        raise RuntimeError(f"WMI query failed for {wmi_class}: {e}")


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int.

    Args:
        value: Value to convert.
        default: Default if conversion fails.

    Returns:
        Integer value or default.
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float.

    Args:
        value: Value to convert.
        default: Default if conversion fails.

    Returns:
        Float value or default.
    """
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def bytes_to_gb(value: int | float, decimals: int = 1) -> float:
    """Convert bytes to gigabytes.

    Args:
        value: Value in bytes.
        decimals: Decimal places to round to.

    Returns:
        Value in GB.
    """
    return round(value / (1024**3), decimals)


def bytes_to_readable(value: int | float) -> str:
    """Convert bytes to human-readable string.

    Args:
        value: Value in bytes.

    Returns:
        Formatted string like "16.0 GB" or "512.0 MB".
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(value) < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"
