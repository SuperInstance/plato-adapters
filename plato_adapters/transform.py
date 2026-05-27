"""Message transform utilities for normalising tile data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


class TransformError(Exception):
    """Raised when a transform step fails."""


# Type alias for a transform function: dict in → dict out
TransformFn = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass
class MessageTransform:
    """Compose a chain of transform functions and apply them to tile dicts.

    Built-in helpers (``add_field``, ``rename_field``, ``remove_field``,
    ``require_fields``, ``set_defaults``, ``coerce_types``) push callable
    steps onto the pipeline.  Call ``apply()`` to run all steps.
    """

    steps: list[TransformFn] = field(default_factory=list)

    # -- Composition helpers -----------------------------------------------

    def add_step(self, fn: TransformFn) -> "MessageTransform":
        """Append an arbitrary transform step."""
        self.steps.append(fn)
        return self

    def add_field(self, key: str, value: Any) -> "MessageTransform":
        """Add a static field to every tile."""
        def _step(data: dict[str, Any]) -> dict[str, Any]:
            data[key] = value
            return data
        self.steps.append(_step)
        return self

    def rename_field(self, old: str, new: str) -> "MessageTransform":
        """Rename *old* key to *new* if present."""
        def _step(data: dict[str, Any]) -> dict[str, Any]:
            if old in data:
                data[new] = data.pop(old)
            return data
        self.steps.append(_step)
        return self

    def remove_field(self, key: str) -> "MessageTransform":
        """Remove *key* from the tile if present."""
        def _step(data: dict[str, Any]) -> dict[str, Any]:
            data.pop(key, None)
            return data
        self.steps.append(_step)
        return self

    def require_fields(self, *keys: str) -> "MessageTransform":
        """Raise ``TransformError`` if any *key* is missing."""
        def _step(data: dict[str, Any]) -> dict[str, Any]:
            missing = [k for k in keys if k not in data]
            if missing:
                raise TransformError(f"Missing required fields: {missing}")
            return data
        self.steps.append(_step)
        return self

    def set_defaults(self, defaults: dict[str, Any]) -> "MessageTransform":
        """Set default values for keys not already present."""
        def _step(data: dict[str, Any]) -> dict[str, Any]:
            for k, v in defaults.items():
                data.setdefault(k, v)
            return data
        self.steps.append(_step)
        return self

    def coerce_types(self, type_map: dict[str, type]) -> "MessageTransform":
        """Cast specified fields to the given types."""
        def _step(data: dict[str, Any]) -> dict[str, Any]:
            for k, t in type_map.items():
                if k in data:
                    try:
                        data[k] = t(data[k])
                    except (ValueError, TypeError) as exc:
                        raise TransformError(
                            f"Cannot coerce {k!r} to {t.__name__}: {exc}"
                        ) from exc
            return data
        self.steps.append(_step)
        return self

    # -- Application -------------------------------------------------------

    def apply(self, data: dict[str, Any]) -> dict[str, Any]:
        """Run every step in order, returning the transformed dict."""
        result = dict(data)  # shallow copy
        for step in self.steps:
            try:
                result = step(result)
            except TransformError:
                raise
            except Exception as exc:
                raise TransformError(f"Transform failed: {exc}") from exc
        return result

    def apply_all(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply to a list of dicts; skip items that fail."""
        results: list[dict[str, Any]] = []
        for item in items:
            try:
                results.append(self.apply(item))
            except TransformError:
                continue
        return results

    def clear(self) -> "MessageTransform":
        """Remove all steps."""
        self.steps.clear()
        return self
