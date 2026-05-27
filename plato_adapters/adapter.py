"""Base adapter with transform/validate pipeline."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class AdapterError(Exception):
    """Base exception for adapter operations."""


@dataclass
class AdapterConfig:
    """Configuration for an adapter instance."""

    name: str
    adapter_type: str
    params: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def validate(self) -> None:
        """Validate config fields."""
        if not self.name or not self.name.strip():
            raise AdapterError("Adapter name must be a non-empty string")
        if not self.adapter_type or not self.adapter_type.strip():
            raise AdapterError("Adapter type must be a non-empty string")


class BaseAdapter(ABC):
    """Abstract base class for all PLATO adapters.

    Subclasses must implement ``read()`` and ``write()``.
    Optionally override ``validate_data()`` and ``transform()``.
    """

    def __init__(self, config: AdapterConfig) -> None:
        config.validate()
        self._config = config
        self._connected = False

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def adapter_type(self) -> str:
        return self._config.adapter_type

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def params(self) -> dict[str, Any]:
        return self._config.params

    # -- Lifecycle hooks --------------------------------------------------

    def connect(self) -> None:
        """Prepare the adapter (open connections, auth, etc.)."""
        self._connected = True

    def disconnect(self) -> None:
        """Tear down resources."""
        self._connected = False

    # -- Core interface ---------------------------------------------------

    @abstractmethod
    def read(self) -> list[dict[str, Any]]:
        """Pull data from an external source, return a list of tile dicts."""

    @abstractmethod
    def write(self, tiles: list[dict[str, Any]]) -> int:
        """Push tiles to an external system. Return count written."""

    # -- Pipeline helpers -------------------------------------------------

    def validate_data(self, data: dict[str, Any]) -> bool:
        """Return True if *data* looks like a valid tile dict."""
        return isinstance(data, dict) and len(data) > 0

    def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply adapter-specific transformations. Default is identity."""
        return data

    def process_incoming(self, raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Validate → transform pipeline for data arriving via ``read()``."""
        result: list[dict[str, Any]] = []
        for item in raw:
            if not self.validate_data(item):
                continue
            result.append(self.transform(item))
        return result

    def process_outgoing(self, tiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Validate → transform pipeline for data leaving via ``write()``."""
        validated: list[dict[str, Any]] = []
        for tile in tiles:
            if not self.validate_data(tile):
                continue
            validated.append(self.transform(tile))
        return validated

    # -- Dunder helpers ---------------------------------------------------

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} type={self.adapter_type!r}>"


class InMemoryAdapter(BaseAdapter):
    """Simple in-memory adapter useful for testing."""

    def __init__(self, config: AdapterConfig) -> None:
        super().__init__(config)
        self._store: list[dict[str, Any]] = []

    def seed(self, items: list[dict[str, Any]]) -> None:
        """Pre-load data for ``read()`` to return."""
        self._store.extend(items)

    def read(self) -> list[dict[str, Any]]:
        return self.process_incoming(list(self._store))

    def write(self, tiles: list[dict[str, Any]]) -> int:
        outgoing = self.process_outgoing(tiles)
        self._store.extend(outgoing)
        return len(outgoing)

    def clear(self) -> None:
        self._store.clear()

    @property
    def stored(self) -> list[dict[str, Any]]:
        return list(self._store)
