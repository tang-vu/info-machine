"""Health scoring engine for system components."""

from __future__ import annotations

from typing import Any

from info_machine.utils.formatting import health_grade


def calculate_overall_health(inspector_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate overall system health from individual inspector results.

    Args:
        inspector_results: List of inspector result dicts (from to_dict()).

    Returns:
        Dict with overall score, grade, per-component scores, and summary.
    """
    scores = {}
    valid_scores = []

    for result in inspector_results:
        name = result.get("display_name", result.get("name", "Unknown"))
        score = result.get("health_score", -1)
        scores[name] = {
            "score": score,
            "grade": health_grade(score),
            "details": result.get("health_details", ""),
        }
        if score >= 0:
            valid_scores.append(score)

    overall_score = round(sum(valid_scores) / len(valid_scores)) if valid_scores else -1
    overall_grade = health_grade(overall_score)

    # Build summary
    warnings = []
    critical = []
    for name, info in scores.items():
        if info["score"] < 0:
            continue
        if info["score"] < 40:
            critical.append(f"🔴 {name}: {info['score']}% — {info['details']}")
        elif info["score"] < 70:
            warnings.append(f"🟡 {name}: {info['score']}% — {info['details']}")

    return {
        "overall_score": overall_score,
        "overall_grade": overall_grade,
        "components": scores,
        "component_count": len(valid_scores),
        "critical_issues": critical,
        "warnings": warnings,
        "summary": _build_summary(overall_score, overall_grade, critical, warnings),
    }


def _build_summary(
    score: int,
    grade: str,
    critical: list[str],
    warnings: list[str],
) -> str:
    """Build a human-readable health summary.

    Args:
        score: Overall health score.
        grade: Overall letter grade.
        critical: List of critical issue descriptions.
        warnings: List of warning descriptions.

    Returns:
        Multi-line health summary string.
    """
    lines = [f"Overall System Health: {score}% (Grade {grade})"]

    if not critical and not warnings:
        lines.append("✅ All components are in good condition.")
    else:
        if critical:
            lines.append(f"\n⚠️ Critical Issues ({len(critical)}):")
            lines.extend(f"  {c}" for c in critical)
        if warnings:
            lines.append(f"\n⚡ Warnings ({len(warnings)}):")
            lines.extend(f"  {w}" for w in warnings)

    return "\n".join(lines)
