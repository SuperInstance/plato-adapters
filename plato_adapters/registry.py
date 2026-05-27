"""Adapter registry — discover, register, and instantiate adapters."""

from __future__ import annotations

from typing import Type

from .adapter import BaseAdapter, AdapterConfig, AdapterError


class RegistryError(Exception):
    """Raised for registry lookup / registration issues."""


class AdapterRegistry:
    """Central registry mapping adapter type names to adapter classes.

    Usage::

        registry = AdapterRegistry()
        registry.register("memory", InMemoryAdapter)

        cfg = AdapterConfig(name="buf", adapter_type="memory")
        adapter = registry.create(cfg)
    """

    def __init__(self) -> None:
        self._types: dict[str, Type[BaseAdapter]] = {}

    # -- Registration ------------------------------------------------------

    def register(self, adapter_type: str, cls: Type[BaseAdapter]) -> None:
        """Register *cls* under *adapter_type*."""
        if not adapter_type or not adapter_type.strip():
            raise RegistryError("adapter_type must be a non-empty string")
        if not (isinstance(cls, type) and issubclass(cls, BaseAdapter)):
            raise RegistryError(f"{cls!r} must be a subclass of BaseAdapter")
        self._types[adapter_type] = cls

    def unregister(self, adapter_type: str) -> None:
        """Remove a registered adapter type."""
        if adapter_type not in self._types:
            raise RegistryError(f"Unknown adapter type: {adapter_type!r}")
        del self._types[adapter_type]

    # -- Lookup / creation -------------------------------------------------

    def get(self, adapter_type: str) -> Type[BaseAdapter]:
        """Return the class registered under *adapter_type*."""
        if adapter_type not in self._types:
            raise RegistryError(f"Unknown adapter type: {adapter_type!r}")
        return self._types[adapter_type]

    def create(self, config: AdapterConfig) -> BaseAdapter:
        """Instantiate the adapter for *config.adapter_type*."""
        cls = self.get(config.adapter_type)
        return cls(config)

    def has(self, adapter_type: str) -> bool:
        return adapter_type in self._types

    # -- Introspection -----------------------------------------------------

    @property
    def registered_types(self) -> list[str]:
        return sorted(self._types.keys())

    def __len__(self) -> int:
        return len(self._types)

    def __contains__(self, adapter_type: str) -> bool:
        return self.has(adapter_type)

    def __repr__(self) -> str:
        return f"<AdapterRegistry types={self.registered_types}>"
