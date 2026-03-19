# Architecture

## Overview

Info-Machine uses a **plugin-based architecture** where each hardware component is an independent inspector module.

## Data Flow

```
CLI Command → Inspector Registry → [Inspector 1, Inspector 2, ...] → Collect Data
                                                                        ↓
                                              Health Scoring ← Inspector Results
                                                    ↓
                                              Reporter / Verifier
                                                    ↓
                                              Output (Terminal / File)
```

## Key Components

### BaseInspector (Abstract)
All inspectors inherit from `BaseInspector` and implement:
- `collect()` → Returns hardware data as a dict
- `health_score()` → Returns 0-100 health score
- `health_details()` → Returns human-readable health description

### InspectorRegistry
Auto-discovers and manages inspector instances. Inspectors self-register via `@registry.register` decorator.

### Health Scoring
Aggregates per-component scores into an overall system health grade (A-F). Identifies critical issues and warnings.

### Spec Verifier
Loads seller claims from JSON and compares against actual hardware using smart matching:
- CPU: Model identifier matching (e.g., "i7-12700H")
- RAM: Capacity matching with tolerance (±1GB)
- Storage: Capacity with 10% tolerance (manufacturer vs actual)
- GPU: Model identifier matching
- Display: Resolution and refresh rate

### Reporter
Generates reports in JSON, Markdown, and HTML formats. HTML uses a dark-themed design with inline CSS.

## Adding a New Inspector

See `.agents/workflows/backend-dev.md` for step-by-step instructions.
