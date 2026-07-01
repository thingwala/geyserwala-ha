"""Tests for entity helper utilities."""

from __future__ import annotations

from dataclasses import dataclass

from custom_components.thingwala_geyserwala.entity import gen_entity_dataclasses


@dataclass
class DemoEntity:
    """Simple dataclass for testing filtering behavior."""

    name: str
    key: str


def test_gen_entity_dataclasses_filters_unknown_fields() -> None:
    """Only matching dataclass fields should be passed through."""
    entities = {"sensor": [{"name": "A", "key": "a", "ignored": True}]}
    result = list(gen_entity_dataclasses(entities, "sensor", DemoEntity))
    assert len(result) == 1
    assert result[0].name == "A"
    assert result[0].key == "a"


def test_gen_entity_dataclasses_handles_none_dc_class() -> None:
    """Generator should be empty when no dataclass type is provided."""
    entities = {"sensor": [{"name": "A", "key": "a"}]}
    result = list(gen_entity_dataclasses(entities, "sensor", None))
    assert result == []
