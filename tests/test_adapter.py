"""Tests for adapter.py — BaseAdapter, AdapterConfig, InMemoryAdapter."""

import pytest
from dataclasses import asdict

from plato_adapters.adapter import (
    AdapterConfig,
    AdapterError,
    BaseAdapter,
    InMemoryAdapter,
)


# -- AdapterConfig ----------------------------------------------------------

class TestAdapterConfig:
    def test_valid_config(self):
        cfg = AdapterConfig(name="a", adapter_type="http")
        assert cfg.name == "a"
        assert cfg.adapter_type == "http"
        assert cfg.params == {}
        assert cfg.enabled is True

    def test_custom_params(self):
        cfg = AdapterConfig(name="b", adapter_type="file", params={"path": "/tmp/x"}, enabled=False)
        assert cfg.params["path"] == "/tmp/x"
        assert cfg.enabled is False

    def test_validate_empty_name(self):
        cfg = AdapterConfig(name="", adapter_type="http")
        with pytest.raises(AdapterError, match="name"):
            cfg.validate()

    def test_validate_whitespace_name(self):
        cfg = AdapterConfig(name="  ", adapter_type="http")
        with pytest.raises(AdapterError, match="name"):
            cfg.validate()

    def test_validate_empty_type(self):
        cfg = AdapterConfig(name="x", adapter_type="")
        with pytest.raises(AdapterError, match="type"):
            cfg.validate()


# -- BaseAdapter (abstract) -------------------------------------------------

class DummyAdapter(BaseAdapter):
    """Concrete stub for testing the abstract base."""

    def __init__(self, config: AdapterConfig) -> None:
        super().__init__(config)
        self._read_data: list[dict] = []
        self._written: list[dict] = []

    def read(self) -> list[dict]:
        return self.process_incoming(self._read_data)

    def write(self, tiles: list[dict]) -> int:
        out = self.process_outgoing(tiles)
        self._written.extend(out)
        return len(out)


class TestBaseAdapter:
    @pytest.fixture()
    def adapter(self):
        cfg = AdapterConfig(name="dummy", adapter_type="test")
        return DummyAdapter(cfg)

    def test_properties(self, adapter):
        assert adapter.name == "dummy"
        assert adapter.adapter_type == "test"
        assert adapter.is_connected is False

    def test_connect_disconnect(self, adapter):
        adapter.connect()
        assert adapter.is_connected is True
        adapter.disconnect()
        assert adapter.is_connected is False

    def test_validate_data_accepts_nonempty_dict(self, adapter):
        assert adapter.validate_data({"key": "val"}) is True

    def test_validate_data_rejects_empty_dict(self, adapter):
        assert adapter.validate_data({}) is False

    def test_validate_data_rejects_non_dict(self, adapter):
        assert adapter.validate_data("not a dict") is False  # type: ignore[arg-type]

    def test_process_incoming_filters_invalid(self, adapter):
        adapter._read_data = [{"a": 1}, {}, {"b": 2}]
        result = adapter.read()
        assert len(result) == 2

    def test_process_outgoing_filters_invalid(self, adapter):
        count = adapter.write([{"x": 1}, {}, {"y": 2}])
        assert count == 2

    def test_repr(self, adapter):
        r = repr(adapter)
        assert "DummyAdapter" in r
        assert "dummy" in r

    def test_params(self, adapter):
        assert adapter.params == {}

    def test_invalid_config_raises(self):
        with pytest.raises(AdapterError):
            DummyAdapter(AdapterConfig(name="", adapter_type="t"))


# -- InMemoryAdapter --------------------------------------------------------

class TestInMemoryAdapter:
    @pytest.fixture()
    def mem(self):
        cfg = AdapterConfig(name="mem", adapter_type="memory")
        return InMemoryAdapter(cfg)

    def test_empty_read(self, mem):
        assert mem.read() == []

    def test_seed_and_read(self, mem):
        mem.seed([{"id": 1}, {"id": 2}])
        result = mem.read()
        assert len(result) == 2

    def test_write_and_stored(self, mem):
        n = mem.write([{"val": "a"}, {"val": "b"}])
        assert n == 2
        assert len(mem.stored) == 2

    def test_clear(self, mem):
        mem.seed([{"x": 1}])
        mem.clear()
        assert mem.stored == []

    def test_write_filters_invalid(self, mem):
        n = mem.write([{"ok": True}, {}])
        assert n == 1
        assert len(mem.stored) == 1

    def test_process_incoming_applies_transform(self, mem):
        def uppercase_val(data):
            if "val" in data and isinstance(data["val"], str):
                data["val"] = data["val"].upper()
            return data
        mem.transform = uppercase_val
        mem.seed([{"val": "hello"}])
        result = mem.read()
        assert result[0]["val"] == "HELLO"
