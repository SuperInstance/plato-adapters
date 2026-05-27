"""Tests for transform.py — MessageTransform pipeline."""

import pytest
from plato_adapters.transform import MessageTransform, TransformError


class TestMessageTransformBasic:
    def test_empty_pipeline_returns_copy(self):
        t = MessageTransform()
        original = {"a": 1}
        result = t.apply(original)
        assert result == {"a": 1}
        assert result is not original

    def test_custom_step(self):
        t = MessageTransform().add_step(lambda d: {**d, "added": True})
        assert t.apply({"x": 1}) == {"x": 1, "added": True}


class TestAddField:
    def test_adds_field(self):
        t = MessageTransform().add_field("status", "ok")
        assert t.apply({}) == {"status": "ok"}

    def test_overwrites_existing(self):
        t = MessageTransform().add_field("x", 42)
        assert t.apply({"x": 0}) == {"x": 42}


class TestRenameField:
    def test_rename_present(self):
        t = MessageTransform().rename_field("old", "new")
        assert t.apply({"old": 1}) == {"new": 1}

    def test_rename_absent_noop(self):
        t = MessageTransform().rename_field("old", "new")
        assert t.apply({"other": 1}) == {"other": 1}


class TestRemoveField:
    def test_remove_present(self):
        t = MessageTransform().remove_field("secret")
        assert t.apply({"secret": "x", "keep": 1}) == {"keep": 1}

    def test_remove_absent_noop(self):
        t = MessageTransform().remove_field("nosuchkey")
        assert t.apply({"a": 1}) == {"a": 1}


class TestRequireFields:
    def test_all_present_passes(self):
        t = MessageTransform().require_fields("a", "b")
        assert t.apply({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    def test_missing_raises(self):
        t = MessageTransform().require_fields("a", "b")
        with pytest.raises(TransformError, match="Missing"):
            t.apply({"a": 1})


class TestSetDefaults:
    def test_adds_missing(self):
        t = MessageTransform().set_defaults({"a": 0, "b": "x"})
        assert t.apply({"a": 1}) == {"a": 1, "b": "x"}

    def test_no_overwrite(self):
        t = MessageTransform().set_defaults({"x": 10})
        assert t.apply({"x": 5}) == {"x": 5}


class TestCoerceTypes:
    def test_coerce_int(self):
        t = MessageTransform().coerce_types({"count": int})
        assert t.apply({"count": "42"}) == {"count": 42}

    def test_coerce_float(self):
        t = MessageTransform().coerce_types({"val": float})
        assert t.apply({"val": "3.14"}) == {"val": pytest.approx(3.14)}

    def test_coerce_failure_raises(self):
        t = MessageTransform().coerce_types({"count": int})
        with pytest.raises(TransformError, match="Cannot coerce"):
            t.apply({"count": "not_a_number"})

    def test_coerce_missing_field_skipped(self):
        t = MessageTransform().coerce_types({"count": int})
        assert t.apply({}) == {}


class TestChaining:
    def test_chain_multiple_steps(self):
        t = (
            MessageTransform()
            .rename_field("name", "title")
            .add_field("source", "test")
            .set_defaults({"priority": 0})
        )
        result = t.apply({"name": "hello"})
        assert result == {"title": "hello", "source": "test", "priority": 0}


class TestApplyAll:
    def test_apply_all_success(self):
        t = MessageTransform().add_field("ok", True)
        results = t.apply_all([{"a": 1}, {"b": 2}])
        assert len(results) == 2
        assert all(r["ok"] is True for r in results)

    def test_apply_all_skips_failures(self):
        t = MessageTransform().require_fields("id")
        items = [{"id": 1}, {"no_id": True}, {"id": 2}]
        results = t.apply_all(items)
        assert len(results) == 2


class TestClear:
    def test_clear_removes_steps(self):
        t = MessageTransform().add_field("x", 1).clear()
        assert t.apply({"a": 1}) == {"a": 1}


class TestBadStep:
    def test_exception_wrapped(self):
        def bad(data):
            raise RuntimeError("boom")

        t = MessageTransform().add_step(bad)
        with pytest.raises(TransformError, match="Transform failed"):
            t.apply({})
