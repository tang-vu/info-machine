"""Unit tests for health scoring engine."""

import pytest

from info_machine.core.health import calculate_overall_health
from info_machine.utils.formatting import health_grade


class TestHealthScoring:
    """Tests for health scoring calculations."""

    def test_overall_health_all_perfect(self):
        results = [
            {"name": "cpu", "display_name": "CPU", "health_score": 100, "health_details": "OK"},
            {"name": "ram", "display_name": "RAM", "health_score": 100, "health_details": "OK"},
        ]
        health = calculate_overall_health(results)
        assert health["overall_score"] == 100
        assert health["overall_grade"] == "A"
        assert len(health["critical_issues"]) == 0
        assert len(health["warnings"]) == 0

    def test_overall_health_mixed(self):
        results = [
            {"name": "cpu", "display_name": "CPU", "health_score": 90, "health_details": "Good"},
            {
                "name": "ram",
                "display_name": "RAM",
                "health_score": 50,
                "health_details": "High usage",
            },
            {
                "name": "battery",
                "display_name": "Battery",
                "health_score": 30,
                "health_details": "Degraded",
            },
        ]
        health = calculate_overall_health(results)
        # (90 + 50 + 30) / 3 = 56.67 ≈ 57
        assert 50 <= health["overall_score"] <= 60
        assert len(health["critical_issues"]) == 1  # battery < 40
        assert len(health["warnings"]) == 1  # ram < 70

    def test_overall_health_skip_unavailable(self):
        results = [
            {"name": "cpu", "display_name": "CPU", "health_score": 80, "health_details": "OK"},
            {
                "name": "battery",
                "display_name": "Battery",
                "health_score": -1,
                "health_details": "N/A",
            },
        ]
        health = calculate_overall_health(results)
        assert health["overall_score"] == 80  # Only CPU counted
        assert health["component_count"] == 1

    def test_overall_health_empty(self):
        health = calculate_overall_health([])
        assert health["overall_score"] == -1

    def test_health_grade_ranges(self):
        assert health_grade(100) == "A"
        assert health_grade(80) == "A"
        assert health_grade(79) == "B"
        assert health_grade(60) == "B"
        assert health_grade(59) == "C"
        assert health_grade(40) == "C"
        assert health_grade(39) == "D"
        assert health_grade(20) == "D"
        assert health_grade(19) == "F"
        assert health_grade(0) == "F"
        assert health_grade(-1) == "N/A"
