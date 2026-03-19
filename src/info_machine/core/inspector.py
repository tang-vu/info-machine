"""Base inspector class and registry for hardware inspectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseInspector(ABC):
    """Abstract base class for all hardware inspectors.

    Every inspector must implement:
        - collect(): gather hardware data
        - health_score(): return 0-100 health score
        - health_details(): human-readable health description

    Attributes:
        name: Machine-readable identifier (e.g., "cpu").
        display_name: Human-readable name (e.g., "CPU / Processor").
    """

    name: str = ""
    display_name: str = ""

    def __init__(self) -> None:
        self._data: dict[str, Any] | None = None
        self._error: str | None = None

    @abstractmethod
    def collect(self) -> dict[str, Any]:
        """Collect hardware information.

        Returns:
            Dict containing all discovered hardware data for this component.
        """

    @abstractmethod
    def health_score(self) -> int:
        """Calculate a health score for this component.

        Returns:
            Integer from 0 (critical) to 100 (perfect health).
        """

    @abstractmethod
    def health_details(self) -> str:
        """Provide a human-readable health assessment.

        Returns:
            Description of component health status.
        """

    def safe_collect(self) -> dict[str, Any]:
        """Collect data with error handling.

        Returns:
            Collected data dict, or error info if collection fails.
        """
        try:
            self._data = self.collect()
            return self._data
        except Exception as e:
            self._error = str(e)
            return {"error": self._error}

    def safe_health_score(self) -> int:
        """Get health score with error handling.

        Returns:
            Health score, or -1 if unavailable.
        """
        try:
            return self.health_score()
        except Exception:
            return -1

    def to_dict(self) -> dict[str, Any]:
        """Serialize inspector results to dict.

        Returns:
            Dict with name, data, health score, and health details.
        """
        data = self._data if self._data is not None else self.safe_collect()
        score = self.safe_health_score()
        return {
            "name": self.name,
            "display_name": self.display_name,
            "data": data,
            "health_score": score,
            "health_details": self.health_details() if score >= 0 else "Unable to assess",
            "error": self._error,
        }


class InspectorRegistry:
    """Registry that manages all available hardware inspectors."""

    def __init__(self) -> None:
        self._inspectors: dict[str, type[BaseInspector]] = {}

    def register(self, inspector_class: type[BaseInspector]) -> type[BaseInspector]:
        """Register an inspector class.

        Args:
            inspector_class: The inspector class to register.

        Returns:
            The same class (allows use as decorator).
        """
        self._inspectors[inspector_class.name] = inspector_class
        return inspector_class

    def get(self, name: str) -> type[BaseInspector] | None:
        """Get an inspector class by name."""
        return self._inspectors.get(name)

    def get_all(self) -> dict[str, type[BaseInspector]]:
        """Get all registered inspector classes."""
        return dict(self._inspectors)

    def create_all(self) -> list[BaseInspector]:
        """Create instances of all registered inspectors.

        Returns:
            List of inspector instances.
        """
        return [cls() for cls in self._inspectors.values()]

    def create(self, names: list[str] | None = None) -> list[BaseInspector]:
        """Create instances of selected inspectors.

        Args:
            names: List of inspector names. If None, creates all.

        Returns:
            List of inspector instances.
        """
        if names is None:
            return self.create_all()
        instances = []
        for name in names:
            cls = self._inspectors.get(name)
            if cls:
                instances.append(cls())
        return instances


# Global registry instance
registry = InspectorRegistry()
