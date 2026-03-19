"""Unit tests for CLI commands."""

from click.testing import CliRunner

from info_machine.cli import main


class TestCli:
    """Tests for CLI commands."""

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "info-machine" in result.output

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "scan" in result.output
        assert "health" in result.output
        assert "verify" in result.output
        assert "report" in result.output
        assert "info" in result.output

    def test_scan_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["scan", "--help"])
        assert result.exit_code == 0
        assert "--component" in result.output

    def test_verify_missing_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["verify", "nonexistent.json"])
        assert result.exit_code != 0
