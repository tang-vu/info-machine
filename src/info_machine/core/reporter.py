"""Report generation — export inspection results to JSON, Markdown, HTML."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from info_machine.utils.formatting import health_grade


def generate_report(
    inspector_results: list[dict[str, Any]],
    health_data: dict[str, Any],
    format: str = "json",
    output_path: str | None = None,
    verification_results: list[dict[str, str]] | None = None,
) -> str:
    """Generate a report in the specified format.

    Args:
        inspector_results: List of inspector result dicts.
        health_data: Overall health data from calculate_overall_health.
        format: Output format — "json", "markdown", or "html".
        output_path: Optional file path to save the report.
        verification_results: Optional verification results to include.

    Returns:
        The report content as a string.
    """
    timestamp = datetime.now().isoformat()

    report_data = {
        "timestamp": timestamp,
        "overall_health": health_data,
        "components": inspector_results,
    }
    if verification_results:
        report_data["verification"] = verification_results

    generators = {
        "json": _generate_json,
        "markdown": _generate_markdown,
        "md": _generate_markdown,
        "html": _generate_html,
    }

    generator = generators.get(format.lower())
    if not generator:
        raise ValueError(f"Unsupported format: {format}. Use: json, markdown, html")

    content = generator(report_data)

    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    return content


def _generate_json(data: dict) -> str:
    """Generate JSON report."""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def _generate_markdown(data: dict) -> str:
    """Generate Markdown report."""
    lines = [
        "# 🖥️ Info-Machine System Report",
        f"\n**Generated:** {data['timestamp']}",
        "",
    ]

    # Overall Health
    health = data.get("overall_health", {})
    score = health.get("overall_score", -1)
    grade = health.get("overall_grade", "N/A")
    lines.append(f"## Overall Health: {score}% (Grade {grade})")
    lines.append("")

    # Component summary table
    components = health.get("components", {})
    if components:
        lines.append("| Component | Score | Grade | Details |")
        lines.append("|---|---|---|---|")
        for name, info in components.items():
            s = info.get("score", -1)
            g = info.get("grade", "N/A")
            d = info.get("details", "")
            lines.append(f"| {name} | {s}% | {g} | {d} |")
        lines.append("")

    # Warnings & critical
    critical = health.get("critical_issues", [])
    warnings = health.get("warnings", [])
    if critical:
        lines.append("### 🔴 Critical Issues")
        for c in critical:
            lines.append(f"- {c}")
        lines.append("")
    if warnings:
        lines.append("### 🟡 Warnings")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    # Component details
    for result in data.get("components", []):
        name = result.get("display_name", result.get("name", "Unknown"))
        lines.append(f"## {name}")
        lines.append("")

        comp_data = result.get("data", {})
        if isinstance(comp_data, dict):
            for key, value in comp_data.items():
                if isinstance(value, (list, dict)):
                    lines.append(f"**{key}:**")
                    lines.append(f"```json\n{json.dumps(value, indent=2, default=str)}\n```")
                else:
                    lines.append(f"- **{key}:** {value}")
        lines.append("")

    # Verification
    verification = data.get("verification")
    if verification:
        lines.append("## 📋 Spec Verification")
        lines.append("")
        lines.append("| Field | Claimed | Actual | Status |")
        lines.append("|---|---|---|---|")
        for v in verification:
            icon = {"match": "✅", "mismatch": "⚠️", "cannot_verify": "❓"}.get(
                v.get("status", ""), "❓"
            )
            lines.append(
                f"| {v['field']} | {v['claimed']} | {v['actual']} | {icon} {v['status']} |"
            )
        lines.append("")

    return "\n".join(lines)


def _generate_html(data: dict) -> str:
    """Generate HTML report with inline CSS."""
    health = data.get("overall_health", {})
    score = health.get("overall_score", -1)
    grade = health.get("overall_grade", "N/A")

    # Color based on grade
    grade_colors = {
        "A": "#22c55e", "B": "#eab308", "C": "#f97316",
        "D": "#ef4444", "F": "#dc2626", "N/A": "#6b7280",
    }
    grade_color = grade_colors.get(grade, "#6b7280")

    html_parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Info-Machine System Report</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: #0f172a; color: #e2e8f0;
    padding: 2rem; line-height: 1.6;
  }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ color: #38bdf8; font-size: 1.8rem; margin-bottom: 0.5rem; }}
  h2 {{ color: #7dd3fc; font-size: 1.3rem; margin: 1.5rem 0 0.5rem; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }}
  .timestamp {{ color: #64748b; font-size: 0.85rem; margin-bottom: 1.5rem; }}
  .health-badge {{
    display: inline-flex; align-items: center; gap: 0.75rem;
    background: #1e293b; border: 1px solid #334155; border-radius: 12px;
    padding: 1rem 1.5rem; margin: 1rem 0;
  }}
  .health-score {{ font-size: 2.5rem; font-weight: 700; color: {grade_color}; }}
  .health-grade {{ font-size: 1.2rem; color: {grade_color}; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
  th {{ background: #1e293b; color: #94a3b8; text-align: left; padding: 0.75rem; font-size: 0.85rem; text-transform: uppercase; }}
  td {{ padding: 0.75rem; border-bottom: 1px solid #1e293b; }}
  tr:hover {{ background: #1e293b40; }}
  .match {{ color: #22c55e; }}
  .mismatch {{ color: #ef4444; }}
  .unknown {{ color: #6b7280; }}
  .component-card {{
    background: #1e293b; border: 1px solid #334155;
    border-radius: 8px; padding: 1rem 1.25rem; margin: 0.75rem 0;
  }}
  .kv {{ display: flex; gap: 0.5rem; padding: 0.25rem 0; }}
  .kv-key {{ color: #94a3b8; min-width: 180px; font-size: 0.9rem; }}
  .kv-val {{ color: #e2e8f0; font-size: 0.9rem; }}
  .alert {{ padding: 0.75rem 1rem; border-radius: 6px; margin: 0.5rem 0; }}
  .alert-critical {{ background: #7f1d1d30; border-left: 3px solid #ef4444; }}
  .alert-warning {{ background: #78350f30; border-left: 3px solid #eab308; }}
</style>
</head>
<body>
<div class="container">
<h1>🖥️ Info-Machine System Report</h1>
<div class="timestamp">Generated: {data['timestamp']}</div>

<div class="health-badge">
  <div class="health-score">{score}%</div>
  <div>
    <div class="health-grade">Grade {grade}</div>
    <div style="color:#64748b;font-size:0.85rem">Overall Health</div>
  </div>
</div>
"""]

    # Component health table
    components = health.get("components", {})
    if components:
        html_parts.append("<h2>Component Health</h2><table><tr><th>Component</th><th>Score</th><th>Grade</th><th>Details</th></tr>")
        for name, info in components.items():
            s = info.get("score", -1)
            g = info.get("grade", "N/A")
            gc = grade_colors.get(g, "#6b7280")
            d = info.get("details", "")
            html_parts.append(f'<tr><td>{name}</td><td style="color:{gc}">{s}%</td><td style="color:{gc}">{g}</td><td>{d}</td></tr>')
        html_parts.append("</table>")

    # Issues
    critical = health.get("critical_issues", [])
    warnings = health.get("warnings", [])
    if critical:
        html_parts.append("<h2>🔴 Critical Issues</h2>")
        for c in critical:
            html_parts.append(f'<div class="alert alert-critical">{c}</div>')
    if warnings:
        html_parts.append("<h2>🟡 Warnings</h2>")
        for w in warnings:
            html_parts.append(f'<div class="alert alert-warning">{w}</div>')

    # Component details
    for result in data.get("components", []):
        name = result.get("display_name", result.get("name", "Unknown"))
        html_parts.append(f'<h2>{name}</h2><div class="component-card">')
        comp_data = result.get("data", {})
        if isinstance(comp_data, dict):
            for key, value in comp_data.items():
                if isinstance(value, (list, dict)):
                    formatted = json.dumps(value, indent=2, default=str)
                    html_parts.append(f'<div class="kv"><span class="kv-key">{key}</span><pre class="kv-val" style="white-space:pre-wrap;font-size:0.8rem">{formatted}</pre></div>')
                else:
                    html_parts.append(f'<div class="kv"><span class="kv-key">{key}</span><span class="kv-val">{value}</span></div>')
        html_parts.append("</div>")

    # Verification
    verification = data.get("verification")
    if verification:
        html_parts.append("<h2>📋 Spec Verification</h2><table><tr><th>Field</th><th>Claimed</th><th>Actual</th><th>Status</th></tr>")
        for v in verification:
            status = v.get("status", "")
            css = "match" if status == "match" else "mismatch" if status == "mismatch" else "unknown"
            icon = "✅" if status == "match" else "⚠️" if status == "mismatch" else "❓"
            html_parts.append(f'<tr><td>{v["field"]}</td><td>{v["claimed"]}</td><td>{v["actual"]}</td><td class="{css}">{icon} {status}</td></tr>')
        html_parts.append("</table>")

    html_parts.append("</div></body></html>")
    return "\n".join(html_parts)
