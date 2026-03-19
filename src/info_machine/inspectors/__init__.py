"""Hardware inspectors package — auto-registers all inspectors on import."""

from info_machine.inspectors.cpu import CpuInspector
from info_machine.inspectors.ram import RamInspector
from info_machine.inspectors.disk import DiskInspector
from info_machine.inspectors.gpu import GpuInspector
from info_machine.inspectors.display import DisplayInspector
from info_machine.inspectors.battery import BatteryInspector
from info_machine.inspectors.network import NetworkInspector
from info_machine.inspectors.motherboard import MotherboardInspector

__all__ = [
    "CpuInspector",
    "RamInspector",
    "DiskInspector",
    "GpuInspector",
    "DisplayInspector",
    "BatteryInspector",
    "NetworkInspector",
    "MotherboardInspector",
]
