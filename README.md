# 🖥️ Info-Machine

[![CI](https://github.com/tang-vu/info-machine/actions/workflows/ci.yml/badge.svg)](https://github.com/tang-vu/info-machine/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**CLI tool to inspect PC/laptop hardware, evaluate component health, and verify seller specifications.**

Ever bought a used laptop and wondered if the specs match what the seller claimed? Info-Machine scans your hardware, scores component health, and compares actual specs against seller claims — all from the command line.

## ✨ Features

- 🔍 **Hardware Scanning** — CPU, RAM, Disk, GPU, Display, Battery, Network, Motherboard
- ❤️ **Health Scoring** — 0-100 score per component with A-F grades
- 📋 **Spec Verification** — Compare actual hardware vs seller claims (JSON)
- 📄 **Report Export** — JSON, Markdown, and beautiful dark-themed HTML reports
- 🎨 **Rich Terminal UI** — Colorful tables, progress bars, and health bars

## 📦 Installation

```bash
# From source (recommended for now)
git clone https://github.com/tang-vu/info-machine.git
cd info-machine
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Scan All Hardware
```bash
info-machine scan
```

### Check System Health
```bash
info-machine health
```

### Quick System Overview
```bash
info-machine info
```

### Verify Seller Claims
Create a `claims.json` file:
```json
{
  "cpu": "Intel Core i7-12700H",
  "ram": "16GB DDR5 4800MHz",
  "storage": "512GB NVMe SSD",
  "gpu": "NVIDIA RTX 3060 6GB",
  "display": "1920x1080 144Hz",
  "battery": "76Wh"
}
```

Then verify:
```bash
info-machine verify claims.json
```

### Generate Report
```bash
# JSON report
info-machine report -f json -o report.json

# Markdown report
info-machine report -f markdown -o report.md

# HTML report (beautiful dark theme)
info-machine report -f html -o report.html

# Include verification in report
info-machine report -f html -o report.html --claims claims.json
```

### Scan Specific Components
```bash
info-machine scan -c cpu -c ram -c disk
info-machine health -c battery -c disk
```

## 🏗️ Architecture

```
src/info_machine/
├── cli.py                  # CLI entry point (Click)
├── core/
│   ├── inspector.py        # Base inspector + registry
│   ├── health.py           # Health scoring engine
│   ├── verifier.py         # Spec verification
│   └── reporter.py         # Report generation
├── inspectors/
│   ├── cpu.py              # CPU inspector
│   ├── ram.py              # RAM inspector
│   ├── disk.py             # Disk/Storage inspector
│   ├── gpu.py              # GPU inspector
│   ├── display.py          # Display inspector
│   ├── battery.py          # Battery inspector
│   ├── network.py          # Network inspector
│   └── motherboard.py      # Motherboard/BIOS inspector
└── utils/
    ├── formatting.py       # Rich terminal formatting
    └── system.py           # OS detection, WMI helpers
```

## 🧪 Development

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=info_machine

# Lint
ruff check src/

# Format
black src/ tests/
```

## 📋 Supported Components

| Component | Data Collected |
|---|---|
| **CPU** | Model, cores, threads, frequency, cache, usage, temperature |
| **RAM** | Total, available, speed, DDR type, slots, manufacturer |
| **Disk** | Model, capacity, type (SSD/HDD/NVMe), usage, status |
| **GPU** | Model, VRAM, driver, temperature, utilization |
| **Display** | Resolution, refresh rate, color depth, monitor model |
| **Battery** | Charge, health%, wear level, cycle count, design capacity |
| **Network** | Adapters, MAC, speed, IPs, connection status |
| **Motherboard** | Model, serial, BIOS version/date, system manufacturer |

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.
