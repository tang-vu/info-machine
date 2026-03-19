"""Unit tests for CPU inspector."""

from unittest.mock import patch, MagicMock
import pytest

from info_machine.inspectors.cpu import CpuInspector


class TestCpuInspector:
    """Tests for CpuInspector."""

    def test_name_and_display_name(self):
        inspector = CpuInspector()
        assert inspector.name == "cpu"
        assert inspector.display_name == "CPU / Processor"

    @patch("info_machine.inspectors.cpu.is_windows", return_value=False)
    @patch("info_machine.inspectors.cpu.psutil")
    def test_collect_basic(self, mock_psutil, mock_is_win):
        mock_psutil.cpu_count.side_effect = lambda logical=True: 16 if logical else 8
        mock_psutil.cpu_percent.return_value = 25.0
        mock_psutil.cpu_freq.return_value = MagicMock(current=3200.0, min=800.0, max=4500.0)
        mock_psutil.sensors_temperatures.side_effect = AttributeError

        mock_cpuinfo = MagicMock()
        mock_cpuinfo.get_cpu_info.return_value = {
            "brand_raw": "Intel Core i7-12700H",
            "arch": "X86_64",
            "bits": 64,
            "vendor_id_raw": "GenuineIntel",
            "l2_cache_size": "1280 KiB",
            "l3_cache_size": "24576 KiB",
        }

        with patch.dict("sys.modules", {"cpuinfo": mock_cpuinfo}):
            inspector = CpuInspector()
            data = inspector.collect()

        assert data["physical_cores"] == 8
        assert data["logical_cores"] == 16
        assert data["model"] == "Intel Core i7-12700H"
        assert data["frequency_max_mhz"] == 4500.0

    def test_health_score_normal(self):
        inspector = CpuInspector()
        inspector._data = {"temperature_c": 50, "usage_percent": 30}
        assert inspector.health_score() == 100

    def test_health_score_high_temp(self):
        inspector = CpuInspector()
        inspector._data = {"temperature_c": 92, "usage_percent": 30}
        assert inspector.health_score() <= 60

    def test_health_score_no_temp(self):
        inspector = CpuInspector()
        inspector._data = {"usage_percent": 50}
        assert inspector.health_score() == 100

    def test_safe_collect_handles_errors(self):
        inspector = CpuInspector()
        with patch.object(inspector, "collect", side_effect=RuntimeError("WMI fail")):
            result = inspector.safe_collect()
        assert "error" in result
        assert inspector._error == "WMI fail"

    def test_to_dict(self):
        inspector = CpuInspector()
        inspector._data = {"model": "Test CPU", "usage_percent": 10}
        result = inspector.to_dict()
        assert result["name"] == "cpu"
        assert result["display_name"] == "CPU / Processor"
        assert result["data"]["model"] == "Test CPU"
        assert "health_score" in result
