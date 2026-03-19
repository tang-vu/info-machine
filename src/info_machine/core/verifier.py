"""Spec verification — compare actual hardware against seller claims."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class VerificationResult:
    """Result of comparing one spec field."""

    MATCH = "match"
    MISMATCH = "mismatch"
    CANNOT_VERIFY = "cannot_verify"

    def __init__(
        self,
        field: str,
        claimed: str,
        actual: str,
        status: str,
        note: str = "",
    ) -> None:
        self.field = field
        self.claimed = claimed
        self.actual = actual
        self.status = status
        self.note = note

    def to_dict(self) -> dict[str, str]:
        return {
            "field": self.field,
            "claimed": self.claimed,
            "actual": self.actual,
            "status": self.status,
            "note": self.note,
        }

    @property
    def icon(self) -> str:
        icons = {
            self.MATCH: "✅",
            self.MISMATCH: "⚠️",
            self.CANNOT_VERIFY: "❓",
        }
        return icons.get(self.status, "❓")


def load_claims(path: str | Path) -> dict[str, str]:
    """Load seller claims from a JSON file.

    Expected format:
    {
        "cpu": "Intel Core i7-12700H",
        "ram": "16GB DDR5 4800MHz",
        "storage": "512GB NVMe SSD",
        "gpu": "NVIDIA RTX 3060 6GB",
        "display": "1920x1080 144Hz",
        "battery": "76Wh"
    }

    Args:
        path: Path to the JSON claims file.

    Returns:
        Dict of field -> claimed value.

    Raises:
        FileNotFoundError: If claims file doesn't exist.
        json.JSONDecodeError: If file is not valid JSON.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Claims file not found: {path}")

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def verify_specs(
    claims: dict[str, str],
    inspector_results: list[dict[str, Any]],
) -> list[VerificationResult]:
    """Verify hardware specs against seller claims.

    Args:
        claims: Dict of field -> claimed value string.
        inspector_results: List of inspector result dicts (from to_dict()).

    Returns:
        List of VerificationResult for each claimed field.
    """
    # Build a flat lookup of actual data
    actual_data = _flatten_results(inspector_results)
    results = []

    # Verification strategies per field
    verifiers = {
        "cpu": _verify_cpu,
        "ram": _verify_ram,
        "storage": _verify_storage,
        "disk": _verify_storage,
        "gpu": _verify_gpu,
        "display": _verify_display,
        "battery": _verify_battery,
    }

    for field, claimed in claims.items():
        field_lower = field.lower().strip()
        verifier = verifiers.get(field_lower)

        if verifier:
            result = verifier(field, claimed, actual_data)
        else:
            result = VerificationResult(
                field=field,
                claimed=claimed,
                actual="N/A",
                status=VerificationResult.CANNOT_VERIFY,
                note=f"No verifier for field: {field}",
            )

        results.append(result)

    return results


def _flatten_results(inspector_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Flatten inspector results into a single lookup dict."""
    flat: dict[str, Any] = {}
    for result in inspector_results:
        name = result.get("name", "")
        data = result.get("data", {})
        flat[name] = data
    return flat


def _normalize(text: str) -> str:
    """Normalize a string for comparison."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _extract_number(text: str) -> float | None:
    """Extract the first number from a string."""
    match = re.search(r"(\d+\.?\d*)", text)
    return float(match.group(1)) if match else None


def _verify_cpu(field: str, claimed: str, data: dict) -> VerificationResult:
    """Verify CPU model."""
    cpu_data = data.get("cpu", {})
    actual_model = cpu_data.get("model", "Unknown")

    # Check if key parts of the claimed model appear in actual
    claimed_norm = _normalize(claimed)
    actual_norm = _normalize(actual_model)

    # Extract key identifiers (e.g., "i7-12700H", "Ryzen 7 5800X")
    claimed_parts = re.findall(r"[a-z0-9][\w-]*\d[\w-]*", claimed_norm)

    if any(part in actual_norm for part in claimed_parts):
        return VerificationResult(field, claimed, actual_model, VerificationResult.MATCH)
    elif actual_model == "Unknown":
        return VerificationResult(
            field,
            claimed,
            actual_model,
            VerificationResult.CANNOT_VERIFY,
            note="Could not detect CPU model",
        )
    else:
        return VerificationResult(
            field,
            claimed,
            actual_model,
            VerificationResult.MISMATCH,
            note="CPU model does not match seller claim",
        )


def _verify_ram(field: str, claimed: str, data: dict) -> VerificationResult:
    """Verify RAM capacity and type."""
    ram_data = data.get("ram", {})
    actual_gb = ram_data.get("total_gb", 0)
    actual_type = ram_data.get("type", "")

    claimed_gb = _extract_number(claimed)
    actual_str = f"{actual_gb}GB"
    if actual_type:
        actual_str += f" {actual_type}"

    speed = ram_data.get("speed_mhz")
    if speed:
        actual_str += f" {speed}MHz"

    if claimed_gb:
        # Allow small tolerance (e.g., 15.6GB vs 16GB)
        if abs(actual_gb - claimed_gb) <= 1:
            return VerificationResult(field, claimed, actual_str, VerificationResult.MATCH)
        else:
            return VerificationResult(
                field,
                claimed,
                actual_str,
                VerificationResult.MISMATCH,
                note=f"Expected ~{claimed_gb}GB, found {actual_gb}GB",
            )

    return VerificationResult(
        field,
        claimed,
        actual_str,
        VerificationResult.CANNOT_VERIFY,
    )


def _verify_storage(field: str, claimed: str, data: dict) -> VerificationResult:
    """Verify storage capacity and type."""
    disk_data = data.get("disk", {})
    physical = disk_data.get("physical_disks", [])

    if not physical:
        partitions = disk_data.get("partitions", [])
        total_gb = sum(p.get("total_gb", 0) for p in partitions)
        actual_str = f"{total_gb}GB total"
    else:
        parts = []
        total_gb = 0
        for d in physical:
            total_gb += d.get("size_gb", 0)
            parts.append(f"{d['model']} ({d['type']}, {d.get('size_readable', 'N/A')})")
        actual_str = " + ".join(parts)

    claimed_gb = _extract_number(claimed)
    if claimed_gb:
        # Storage manufacturers use base-10, so 512GB ≈ 476GB actual
        tolerance = claimed_gb * 0.1  # 10% tolerance
        if abs(total_gb - claimed_gb) <= tolerance:
            return VerificationResult(field, claimed, actual_str, VerificationResult.MATCH)
        else:
            return VerificationResult(
                field,
                claimed,
                actual_str,
                VerificationResult.MISMATCH,
                note=f"Expected ~{claimed_gb}GB, found ~{total_gb}GB",
            )

    return VerificationResult(field, claimed, actual_str, VerificationResult.CANNOT_VERIFY)


def _verify_gpu(field: str, claimed: str, data: dict) -> VerificationResult:
    """Verify GPU model."""
    gpu_data = data.get("gpu", {})
    gpus = gpu_data.get("gpus", [])

    if not gpus:
        return VerificationResult(
            field,
            claimed,
            "No GPU found",
            VerificationResult.CANNOT_VERIFY,
        )

    gpu_names = [g.get("name", "") for g in gpus]
    actual_str = " + ".join(gpu_names)
    claimed_norm = _normalize(claimed)

    # Check if key parts match any GPU
    claimed_parts = re.findall(r"[a-z0-9][\w-]*\d[\w-]*", claimed_norm)
    for gpu_name in gpu_names:
        gpu_norm = _normalize(gpu_name)
        if any(part in gpu_norm for part in claimed_parts):
            return VerificationResult(field, claimed, actual_str, VerificationResult.MATCH)

    return VerificationResult(
        field,
        claimed,
        actual_str,
        VerificationResult.MISMATCH,
        note="GPU model does not match seller claim",
    )


def _verify_display(field: str, claimed: str, data: dict) -> VerificationResult:
    """Verify display resolution and refresh rate."""
    display_data = data.get("display", {})
    actual_res = display_data.get("resolution", "Unknown")
    actual_refresh = display_data.get("refresh_rate_hz", 0)

    actual_str = actual_res
    if actual_refresh:
        actual_str += f" {actual_refresh}Hz"

    claimed_norm = _normalize(claimed)
    actual_norm = _normalize(actual_str)

    # Check resolution match
    res_match = re.search(r"(\d{3,4})x(\d{3,4})", claimed_norm)
    if res_match:
        claimed_res = f"{res_match.group(1)}x{res_match.group(2)}"
        if claimed_res in actual_norm:
            return VerificationResult(field, claimed, actual_str, VerificationResult.MATCH)
        else:
            return VerificationResult(
                field,
                claimed,
                actual_str,
                VerificationResult.MISMATCH,
            )

    return VerificationResult(field, claimed, actual_str, VerificationResult.CANNOT_VERIFY)


def _verify_battery(field: str, claimed: str, data: dict) -> VerificationResult:
    """Verify battery capacity."""
    bat_data = data.get("battery", {})

    if not bat_data.get("present"):
        return VerificationResult(
            field,
            claimed,
            "No battery",
            VerificationResult.CANNOT_VERIFY,
            note="No battery detected (desktop PC?)",
        )

    design_cap = bat_data.get("design_capacity_mwh")
    if design_cap:
        actual_wh = round(design_cap / 1000, 1)
        actual_str = f"{actual_wh}Wh"

        claimed_wh = _extract_number(claimed)
        if claimed_wh and abs(actual_wh - claimed_wh) <= 5:
            return VerificationResult(field, claimed, actual_str, VerificationResult.MATCH)
        elif claimed_wh:
            return VerificationResult(
                field,
                claimed,
                actual_str,
                VerificationResult.MISMATCH,
                note=f"Expected ~{claimed_wh}Wh, found {actual_wh}Wh",
            )

    return VerificationResult(
        field,
        claimed,
        "Cannot determine capacity",
        VerificationResult.CANNOT_VERIFY,
    )
