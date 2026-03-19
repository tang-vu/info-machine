"""Build script for creating standalone executable."""

import subprocess
import sys
from pathlib import Path


def build():
    """Build standalone executable with PyInstaller."""
    root = Path(__file__).parent
    entry = root / "src" / "info_machine" / "cli.py"
    src_path = root / "src"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name=info-machine",
        "--clean",
        "--noconfirm",
        # Add src/ to search path so PyInstaller finds info_machine
        f"--paths={src_path}",
        # Hidden imports that PyInstaller might miss
        "--hidden-import=info_machine",
        "--hidden-import=info_machine.inspectors",
        "--hidden-import=info_machine.inspectors.cpu",
        "--hidden-import=info_machine.inspectors.ram",
        "--hidden-import=info_machine.inspectors.disk",
        "--hidden-import=info_machine.inspectors.gpu",
        "--hidden-import=info_machine.inspectors.display",
        "--hidden-import=info_machine.inspectors.battery",
        "--hidden-import=info_machine.inspectors.network",
        "--hidden-import=info_machine.inspectors.motherboard",
        "--hidden-import=info_machine.core",
        "--hidden-import=info_machine.core.inspector",
        "--hidden-import=info_machine.core.health",
        "--hidden-import=info_machine.core.verifier",
        "--hidden-import=info_machine.core.reporter",
        "--hidden-import=info_machine.utils",
        "--hidden-import=info_machine.utils.system",
        "--hidden-import=info_machine.utils.formatting",
        "--hidden-import=wmi",
        "--hidden-import=win32com",
        "--hidden-import=win32api",
        "--hidden-import=pythoncom",
        "--hidden-import=cpuinfo",
        "--hidden-import=GPUtil",
        str(entry),
    ]

    print("Building standalone executable...")
    print(f"   Entry: {entry}")
    print(f"   Paths: {src_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
        raise SystemExit(result.returncode)
    print(f"\nBuild complete! Executable: dist/info-machine.exe")


if __name__ == "__main__":
    build()
