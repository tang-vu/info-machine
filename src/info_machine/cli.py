"""CLI entry point for info-machine."""

from __future__ import annotations

import sys

import click
from rich.progress import Progress, SpinnerColumn, TextColumn

from info_machine import __version__
from info_machine.utils.formatting import (
    console,
    create_table,
    health_bar,
    print_error,
    print_header,
    print_key_value,
    print_section,
    print_success,
    print_warning,
)


def _run_inspectors(names: list[str] | None = None) -> list:
    """Import inspectors and run them with a progress bar.

    Args:
        names: Optional list of inspector names to run. None = all.

    Returns:
        List of inspector result dicts.
    """
    # Import here to trigger registration
    import info_machine.inspectors  # noqa: F401
    from info_machine.core.inspector import registry

    inspectors = registry.create(names)
    results = []

    with Progress(
        SpinnerColumn(style="bright_cyan"),
        TextColumn("[bold bright_white]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning hardware...", total=len(inspectors))

        for inspector in inspectors:
            progress.update(task, description=f"Inspecting {inspector.display_name}...")
            inspector.safe_collect()
            result = inspector.to_dict()
            results.append(result)
            progress.advance(task)

    return results


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="info-machine")
@click.pass_context
def main(ctx):
    """🖥️ Info-Machine — PC/Laptop Hardware Inspector

    Inspect hardware specs, evaluate component health,
    and verify configurations against seller claims.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(info)


@main.command()
@click.option(
    "--component",
    "-c",
    multiple=True,
    help="Specific component(s) to scan: cpu, ram, disk, gpu, display,"
    " battery, network, motherboard. Default: all.",
)
@click.option("--json-output", "-j", is_flag=True, help="Output raw JSON data.")
def scan(component: tuple[str, ...], json_output: bool):
    """🔍 Scan hardware and display detailed specs."""
    import json as json_mod

    print_header("Info-Machine Scanner", f"v{__version__}")
    console.print()

    names = list(component) if component else None
    results = _run_inspectors(names)

    if json_output:
        console.print_json(json_mod.dumps(list(results), indent=2, default=str))
        return

    for result in results:
        name = result.get("display_name", result.get("name", "Unknown"))
        error = result.get("error")
        data = result.get("data", {})

        print_section(f"🔹 {name}")

        if error:
            print_error(f"Failed to inspect: {error}")
            continue

        for key, value in data.items():
            if isinstance(value, list):
                console.print(f"  [bold white]{key}:[/bold white]")
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        console.print(f"    [dim]#{i + 1}[/dim]")
                        for k, v in item.items():
                            print_key_value(f"      {k}", str(v), key_style="dim white")
                    else:
                        console.print(f"    - {item}")
            elif isinstance(value, dict):
                console.print(f"  [bold white]{key}:[/bold white]")
                for k, v in value.items():
                    print_key_value(f"    {k}", str(v), key_style="dim white")
            else:
                print_key_value(key, str(value))

    console.print()
    print_success("Scan complete!")


@main.command()
@click.option(
    "--component",
    "-c",
    multiple=True,
    help="Specific component(s) to check. Default: all.",
)
def health(component: tuple[str, ...]):
    """❤️ Check system health scores for all components."""
    from info_machine.core.health import calculate_overall_health

    print_header("System Health Check", f"v{__version__}")
    console.print()

    names = list(component) if component else None
    results = _run_inspectors(names)
    health_data = calculate_overall_health(results)

    # Overall health
    overall = health_data["overall_score"]
    console.print(f"\n  [bold]Overall System Health:[/bold]  {health_bar(overall)}\n")

    # Component health table
    table = create_table(
        "Component Health",
        [
            ("Component", "bright_white"),
            ("Score", ""),
            ("Grade", ""),
            ("Details", "dim"),
        ],
    )

    for name, info in health_data["components"].items():
        score = info["score"]
        grade = info["grade"]

        if score >= 80:
            score_style = "bright_green"
        elif score >= 60:
            score_style = "bright_yellow"
        elif score >= 40:
            score_style = "yellow"
        elif score >= 0:
            score_style = "bright_red"
        else:
            score_style = "dim"

        table.add_row(
            name,
            f"[{score_style}]{score}%[/{score_style}]" if score >= 0 else "[dim]N/A[/dim]",
            f"[{score_style}]{grade}[/{score_style}]",
            info["details"],
        )

    console.print(table)

    # Print warnings and critical issues
    if health_data["critical_issues"]:
        console.print("\n[bold red]🔴 Critical Issues:[/bold red]")
        for issue in health_data["critical_issues"]:
            console.print(f"  {issue}")

    if health_data["warnings"]:
        console.print("\n[bold yellow]🟡 Warnings:[/bold yellow]")
        for warning in health_data["warnings"]:
            console.print(f"  {warning}")

    if not health_data["critical_issues"] and not health_data["warnings"]:
        console.print()
        print_success("All components are in good condition!")


@main.command()
@click.argument("claims_file", type=click.Path(exists=True))
def verify(claims_file: str):
    """📋 Verify specs against seller claims.

    CLAIMS_FILE: Path to a JSON file with seller's claimed specifications.

    Example claims.json:
    {"cpu": "Intel i7-12700H", "ram": "16GB DDR5", "storage": "512GB NVMe SSD"}
    """
    from info_machine.core.verifier import load_claims, verify_specs

    print_header("Spec Verification", "Compare actual hardware vs seller claims")
    console.print()

    try:
        claims = load_claims(claims_file)
    except Exception as e:
        print_error(f"Failed to load claims file: {e}")
        raise SystemExit(1) from e

    console.print(f"  [dim]Claims file:[/dim] {claims_file}")
    console.print(f"  [dim]Fields to verify:[/dim] {len(claims)}")
    console.print()

    results = _run_inspectors()
    verification = verify_specs(claims, results)

    # Results table
    table = create_table(
        "Verification Results",
        [
            ("Field", "bright_white"),
            ("Claimed", "bright_cyan"),
            ("Actual", "bright_yellow"),
            ("Status", ""),
        ],
    )

    match_count = 0
    mismatch_count = 0
    unknown_count = 0

    for v in verification:
        if v.status == "match":
            status_str = "[bright_green]✅ Match[/bright_green]"
            match_count += 1
        elif v.status == "mismatch":
            status_str = "[bright_red]⚠️ Mismatch[/bright_red]"
            mismatch_count += 1
        else:
            status_str = "[dim]❓ Cannot Verify[/dim]"
            unknown_count += 1

        table.add_row(v.field, v.claimed, v.actual, status_str)

    console.print(table)

    # Summary
    console.print(
        f"\n  ✅ Match: [bright_green]{match_count}[/bright_green]  |  "
        f"⚠️ Mismatch: [bright_red]{mismatch_count}[/bright_red]  |  "
        f"❓ Unknown: [dim]{unknown_count}[/dim]"
    )

    if mismatch_count > 0:
        console.print()
        print_warning(
            f"Found {mismatch_count} mismatch(es)! "
            "The seller's claims may not match your actual hardware."
        )
        for v in verification:
            if v.status == "mismatch" and v.note:
                console.print(f"  [dim]• {v.field}: {v.note}[/dim]")
    elif match_count > 0:
        console.print()
        print_success("All verified specs match the seller's claims!")


@main.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown", "html"], case_sensitive=False),
    default="json",
    help="Report format.",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path.")
@click.option(
    "--claims",
    type=click.Path(exists=True),
    help="Optional claims file for verification.",
)
def report(format: str, output: str | None, claims: str | None):
    """📄 Generate a detailed system report.

    Export full hardware inspection results to JSON, Markdown, or HTML.
    """
    from info_machine.core.health import calculate_overall_health
    from info_machine.core.reporter import generate_report

    print_header("Report Generator", f"Format: {format.upper()}")
    console.print()

    results = _run_inspectors()
    health_data = calculate_overall_health(results)

    verification_data = None
    if claims:
        from info_machine.core.verifier import load_claims, verify_specs

        claims_data = load_claims(claims)
        verification = verify_specs(claims_data, results)
        verification_data = [v.to_dict() for v in verification]

    # Default output filename
    if not output:
        ext = {"json": "json", "markdown": "md", "html": "html"}.get(format, format)
        output = f"info-machine-report.{ext}"

    content = generate_report(
        inspector_results=results,
        health_data=health_data,
        format=format,
        output_path=output,
        verification_results=verification_data,
    )

    print_success(f"Report saved to: {output}")
    console.print(f"  [dim]Format: {format.upper()} | Size: {len(content)} bytes[/dim]")


@main.command()
def info():
    """ℹ️ Quick system overview summary."""
    from info_machine.utils.system import get_os_info

    print_header("System Overview", f"Info-Machine v{__version__}")
    console.print()

    # OS Info
    os_info = get_os_info()
    print_section("🖥️ Operating System")
    print_key_value("System", f"{os_info['system']} {os_info['release']}")
    print_key_value("Version", os_info["version"])
    print_key_value("Architecture", os_info["architecture"])
    print_key_value("Hostname", os_info["hostname"])
    print_key_value("Python", os_info["python_version"])

    # Quick hardware scan
    results = _run_inspectors()

    for result in results:
        name = result.get("display_name", result.get("name", "Unknown"))
        data = result.get("data", {})
        score = result.get("health_score", -1)
        error = result.get("error")

        print_section(f"{'🔹'} {name}")

        if error:
            print_error(f"Could not inspect: {error}")
            continue

        # Show key summary data based on inspector type
        inspector_name = result.get("name", "")
        _print_summary(inspector_name, data, score)

    console.print()


def _print_summary(name: str, data: dict, score: int) -> None:
    """Print a concise summary for each inspector type."""
    if name == "cpu":
        print_key_value("Model", data.get("model", "Unknown"))
        cores = data.get("physical_cores", "?")
        logical = data.get("logical_cores", "?")
        print_key_value("Cores", f"{cores} physical / {logical} logical")
        freq = data.get("frequency_max_mhz") or data.get("frequency_current_mhz")
        if freq:
            print_key_value("Frequency", f"{freq} MHz")
    elif name == "ram":
        print_key_value("Total", data.get("total_readable", "Unknown"))
        print_key_value("Usage", f"{data.get('usage_percent', '?')}%")
        if data.get("type"):
            print_key_value("Type", f"{data.get('type')} {data.get('speed_mhz', '')}MHz")
    elif name == "disk":
        for disk in data.get("physical_disks", []):
            size = disk.get("size_readable", "N/A")
            print_key_value("Drive", f"{disk['model']} ({disk['type']}, {size})")
    elif name == "gpu":
        for gpu in data.get("gpus", []):
            vram = gpu.get("vram_total_mb")
            vram_str = f" ({vram}MB VRAM)" if vram else ""
            print_key_value("GPU", f"{gpu.get('name', 'Unknown')}{vram_str}")
    elif name == "display":
        print_key_value("Resolution", data.get("resolution", "Unknown"))
        refresh = data.get("refresh_rate_hz")
        if refresh:
            print_key_value("Refresh Rate", f"{refresh}Hz")
    elif name == "battery":
        if data.get("present"):
            health_pct = data.get("battery_health_percent")
            health_str = f" (Health: {health_pct}%)" if health_pct else ""
            print_key_value("Battery", f"{data.get('percent', '?')}%{health_str}")
            cycles = data.get("cycle_count")
            if cycles:
                print_key_value("Cycle Count", str(cycles))
        else:
            print_key_value("Battery", "Not present (desktop PC)")
    elif name == "network":
        adapters = data.get("adapters", [])
        active = [a for a in adapters if a.get("is_up")]
        print_key_value("Adapters", f"{len(adapters)} total, {len(active)} active")
    elif name == "motherboard":
        mfg = data.get("system_manufacturer") or data.get("manufacturer", "Unknown")
        model = data.get("system_model") or data.get("model", "Unknown")
        print_key_value("System", f"{mfg} {model}")
        bios = data.get("bios_version")
        if bios:
            print_key_value("BIOS", bios)

    if score >= 0:
        print_key_value("Health", health_bar(score))


def _is_frozen() -> bool:
    """Check if running as a PyInstaller bundled EXE."""
    return getattr(sys, "frozen", False)


def run():
    """Entry point that pauses before exit when running as EXE."""
    try:
        main(standalone_mode=False)
    except SystemExit:
        pass
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        if _is_frozen():
            console.print("\n[dim]Press Enter to exit...[/dim]")
            input()


if __name__ == "__main__":
    run()
