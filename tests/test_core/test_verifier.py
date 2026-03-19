"""Unit tests for spec verifier."""

import json
import tempfile
from pathlib import Path

import pytest

from info_machine.core.verifier import (
    VerificationResult,
    load_claims,
    verify_specs,
)


class TestVerifier:
    """Tests for spec verification logic."""

    def test_load_claims_valid(self, tmp_path):
        claims_file = tmp_path / "claims.json"
        claims_file.write_text(json.dumps({"cpu": "Intel i7-12700H", "ram": "16GB DDR5"}))

        claims = load_claims(str(claims_file))
        assert claims["cpu"] == "Intel i7-12700H"
        assert claims["ram"] == "16GB DDR5"

    def test_load_claims_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_claims("nonexistent.json")

    def test_verify_cpu_match(self):
        claims = {"cpu": "Intel Core i7-12700H"}
        results = [
            {
                "name": "cpu",
                "data": {"model": "12th Gen Intel(R) Core(TM) i7-12700H"},
            }
        ]
        verification = verify_specs(claims, results)
        assert len(verification) == 1
        assert verification[0].status == VerificationResult.MATCH

    def test_verify_cpu_mismatch(self):
        claims = {"cpu": "Intel Core i9-13900K"}
        results = [
            {
                "name": "cpu",
                "data": {"model": "Intel Core i7-12700H"},
            }
        ]
        verification = verify_specs(claims, results)
        assert verification[0].status == VerificationResult.MISMATCH

    def test_verify_ram_match(self):
        claims = {"ram": "16GB DDR5 4800MHz"}
        results = [
            {
                "name": "ram",
                "data": {"total_gb": 15.7, "type": "DDR5", "speed_mhz": 4800},
            }
        ]
        verification = verify_specs(claims, results)
        assert verification[0].status == VerificationResult.MATCH

    def test_verify_ram_mismatch(self):
        claims = {"ram": "32GB DDR5"}
        results = [
            {
                "name": "ram",
                "data": {"total_gb": 15.7, "type": "DDR5"},
            }
        ]
        verification = verify_specs(claims, results)
        assert verification[0].status == VerificationResult.MISMATCH

    def test_verify_storage_match_with_tolerance(self):
        claims = {"storage": "512GB NVMe SSD"}
        results = [
            {
                "name": "disk",
                "data": {
                    "physical_disks": [
                        {
                            "model": "Samsung 980 Pro",
                            "type": "NVMe SSD",
                            "size_gb": 476.9,
                            "size_readable": "476.9 GB",
                        }
                    ]
                },
            }
        ]
        verification = verify_specs(claims, results)
        # 512 vs 476.9, tolerance = 51.2 → match
        assert verification[0].status == VerificationResult.MATCH

    def test_verify_unknown_field(self):
        claims = {"webcam": "1080p"}
        results = []
        verification = verify_specs(claims, results)
        assert verification[0].status == VerificationResult.CANNOT_VERIFY

    def test_verification_result_icon(self):
        r = VerificationResult("cpu", "i7", "i7", VerificationResult.MATCH)
        assert r.icon == "✅"
        r2 = VerificationResult("cpu", "i7", "i5", VerificationResult.MISMATCH)
        assert r2.icon == "⚠️"
