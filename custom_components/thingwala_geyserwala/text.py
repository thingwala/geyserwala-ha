####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala text platform."""

from dataclasses import dataclass

import asyncio

from homeassistant.components.text import (
    TextEntity,
    TextEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import GeyserwalaEntity, gen_entity_dataclasses


TEXTS = []
TEXT_MAP = {}


@dataclass
class Text:
    """Entity params."""

    name: str
    key: str
    icon: str
    visible: bool


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala text entities."""

    entities = hass.data.get(DOMAIN + '_ENTITIES')
    for dc in gen_entity_dataclasses(entities, 'text', Text):
        TEXTS.append(dc)
        TEXT_MAP[dc.key] = dc

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaText(
            coordinator,
            TextEntityDescription(
                key=item.key,
                has_entity_name=True,
                name=item.name,
                entity_category=None,
                icon=item.icon,
                entity_registry_visible_default=item.visible,
                # entity_registry_enabled_default=False,
                # native_max=0,
            ),
            item.key,
        )
        for item in TEXTS
    )


class GeyserwalaText(GeyserwalaEntity, TextEntity):
    """Geyserwala text entity."""

    @property
    def native_value(self) -> int:
        """Value."""
        return self.coordinator.data.get_value(self._gw_key)

    async def async_set_value(self, _value: str) -> None:
        """Set the text value."""
        await asyncio.sleep(1)
