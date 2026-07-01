####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Shared platform setup helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import gen_entity_dataclasses


async def async_setup_platform_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    entity_domain: str,
    dc_class: type,
    entity_class: type,
    description_factory: Callable[[Any], object],
    entity_map: dict[str, Any] | None = None,
) -> None:
    """Generic setup for Geyserwala platform entities."""
    entity_items = list(
        gen_entity_dataclasses(
            hass.data.get(f"{DOMAIN}_ENTITIES"),
            entity_domain,
            dc_class,
        )
    )
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    item_map = entity_map if entity_map is not None else None
    if item_map is not None:
        item_map.update({item.key: item for item in entity_items if hasattr(item, "key")})

    entities = []
    for item in entity_items:
        description = description_factory(item)
        if item_map is not None:
            entities.append(
                entity_class(hass, entity_domain, coordinator, description, item.key, item_map)
            )
        else:
            entities.append(entity_class(hass, entity_domain, coordinator, description, item.key))

    if entities:
        async_add_entities(entities)
