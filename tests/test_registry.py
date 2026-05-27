"""Tests for registry.py — AdapterRegistry."""

import pytest

from plato_adapters.adapter import AdapterConfig, BaseAdapter, InMemoryAdapter
from plato_adapters.registry import AdapterRegistry, RegistryError


class TestAdapterRegistry:
    @pytest.fixture()
    def registry(self):
        return AdapterRegistry()

    def test_empty(self, registry):
        assert len(registry) == 0
        assert registry.registered_types == []

    def test_register_and_has(self, registry):
        registry.register("memory", InMemoryAdapter)
        assert registry.has("memory")
        assert "memory" in registry
        assert len(registry) == 1

    def test_get(self, registry):
        registry.register("memory", InMemoryAdapter)
        assert registry.get("memory") is InMemoryAdapter

    def test_get_unknown_raises(self, registry):
        with pytest.raises(RegistryError, match="Unknown"):
            registry.get("nope")

    def test_unregister(self, registry):
        registry.register("memory", InMemoryAdapter)
        registry.unregister("memory")
        assert not registry.has("memory")

    def test_unregister_unknown_raises(self, registry):
        with pytest.raises(RegistryError, match="Unknown"):
            registry.unregister("nope")

    def test_register_empty_type_raises(self, registry):
        with pytest.raises(RegistryError, match="non-empty"):
            registry.register("", InMemoryAdapter)

    def test_register_wrong_class_raises(self, registry):
        with pytest.raises(RegistryError, match="BaseAdapter"):
            registry.register("bad", dict)  # type: ignore[arg-type]

    def test_create(self, registry):
        registry.register("memory", InMemoryAdapter)
        cfg = AdapterConfig(name="buf", adapter_type="memory", params={"size": 10})
        adapter = registry.create(cfg)
        assert isinstance(adapter, InMemoryAdapter)
        assert adapter.name == "buf"
        assert adapter.params["size"] == 10

    def test_create_unknown_raises(self, registry):
        cfg = AdapterConfig(name="x", adapter_type="unknown")
        with pytest.raises(RegistryError):
            registry.create(cfg)

    def test_registered_types_sorted(self, registry):
        registry.register("z-type", InMemoryAdapter)
        registry.register("a-type", InMemoryAdapter)
        registry.register("m-type", InMemoryAdapter)
        assert registry.registered_types == ["a-type", "m-type", "z-type"]

    def test_repr(self, registry):
        registry.register("memory", InMemoryAdapter)
        r = repr(registry)
        assert "AdapterRegistry" in r
        assert "memory" in r

    def test_register_overwrite(self, registry):
        """Re-registering replaces the previous class."""

        class OtherMemory(InMemoryAdapter):
            pass

        registry.register("memory", InMemoryAdapter)
        registry.register("memory", OtherMemory)
        assert registry.get("memory") is OtherMemory
