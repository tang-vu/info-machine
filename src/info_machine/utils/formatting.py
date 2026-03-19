"""Rich terminal formatting utilities for info-machine."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()


def print_header(title: str, subtitle: str = "") -> None:
    """Print a styled header panel.

    Args:
        title: Main title text.
        subtitle: Optional subtitle.
    """
    text = Text(title, style="bold cyan")
    if subtitle:
        text.append(f"\n{subtitle}", style="dim")
    console.print(Panel(text, border_style="bright_blue", box=box.DOUBLE_EDGE, padding=(1, 2)))


def print_section(title: str) -> None:
    """Print a section header.

    Args:
        title: Section title.
    """
    console.print(f"\n[bold bright_yellow]━━━ {title} ━━━[/bold bright_yellow]")


def print_key_value(key: str, value: str, key_style: str = "bold white") -> None:
    """Print a key-value pair.

    Args:
        key: Label.
        value: Value to display.
        key_style: Rich style for the key.
    """
    console.print(f"  [{key_style}]{key}:[/{key_style}] {value}")


def create_table(title: str, columns: list[tuple[str, str]]) -> Table:
    """Create a styled Rich table.

    Args:
        title: Table title.
        columns: List of (name, style) tuples for columns.

    Returns:
        Configured Rich Table.
    """
    table = Table(
        title=title,
        box=box.ROUNDED,
        border_style="bright_blue",
        title_style="bold bright_cyan",
        header_style="bold bright_white",
        show_lines=True,
        padding=(0, 1),
    )
    for name, style in columns:
        table.add_column(name, style=style)
    return table


def health_bar(score: int) -> str:
    """Generate a colored health bar string.

    Args:
        score: Health score 0-100.

    Returns:
        Colored bar string for Rich console.
    """
    if score < 0:
        return "[dim]N/A[/dim]"

    filled = score // 5
    empty = 20 - filled

    if score >= 80:
        color = "bright_green"
        grade = "A"
    elif score >= 60:
        color = "bright_yellow"
        grade = "B"
    elif score >= 40:
        color = "yellow"
        grade = "C"
    elif score >= 20:
        color = "bright_red"
        grade = "D"
    else:
        color = "red"
        grade = "F"

    bar = f"[{color}]{'█' * filled}{'░' * empty}[/{color}]"
    return f"{bar} [{color}]{score}% ({grade})[/{color}]"


def health_grade(score: int) -> str:
    """Convert a health score to a letter grade.

    Args:
        score: Health score 0-100.

    Returns:
        Letter grade string (A-F) or "N/A".
    """
    if score < 0:
        return "N/A"
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"


def print_error(message: str) -> None:
    """Print an error message.

    Args:
        message: Error description.
    """
    console.print(f"[bold red]✗ Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print a success message.

    Args:
        message: Success description.
    """
    console.print(f"[bold bright_green]✓[/bold bright_green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message.

    Args:
        message: Warning description.
    """
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")
