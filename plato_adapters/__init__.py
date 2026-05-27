"""plato-adapters — Adapter implementations for PLATO rooms."""

from .adapter import BaseAdapter, AdapterError, AdapterConfig
from .transform import MessageTransform, TransformError
from .registry import AdapterRegistry, RegistryError

__all__ = [
    "BaseAdapter",
    "AdapterError",
    "AdapterConfig",
    "MessageTransform",
    "TransformError",
    "AdapterRegistry",
    "RegistryError",
]

__version__ = "0.1.0"
