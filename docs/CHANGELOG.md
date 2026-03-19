# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-19

### Added
- Initial CLI with 5 commands: `scan`, `health`, `verify`, `report`, `info`
- 8 hardware inspectors: CPU, RAM, Disk, GPU, Display, Battery, Network, Motherboard
- Health scoring system with 0-100 scores and A-F grades
- Spec verification against seller claims (JSON input)
- Report export in JSON, Markdown, and HTML formats
- Rich terminal UI with colored output, tables, and progress bars
- Development team workflows (Project Lead, Backend Dev, QA, DevOps, Tech Writer)
- CI/CD with GitHub Actions (lint, test, release)
- Comprehensive test suite with mocked system calls
