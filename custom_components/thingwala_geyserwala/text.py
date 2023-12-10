####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala text platform."""
import asyncio
from dataclasses import dataclass

from homeassistant.components.text import (
    TextEntity,
    TextEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import GeyserwalaEntity


@dataclass
class Text:
    """Entity params."""

    name: str
    id: str
    entity_category: str
    icon: str
    visible: bool


TEXTS = [
    Text("Status", "status", None, "mdi:information-outline", True),
]

TEXT_MAP = {s.id: s for s in TEXTS}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala text entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaText(
            coordinator,
            TextEntityDescription(
                key=item.id,
                has_entity_name=True,
                name=item.name,
                entity_category=item.entity_category,
                icon=item.icon,
                entity_registry_visible_default=item.visible,
                # entity_registry_enabled_default=False,
                # native_max=0,
            ),
            item.id,
        )
        for item in TEXTS
    )


class GeyserwalaText(GeyserwalaEntity, TextEntity):
    """Geyserwala text entity."""

    @property
    def native_value(self) -> int:
        """Value."""
        return getattr(self.coordinator.data, self._gw_id)

    async def async_set_value(self, _value: str) -> None:
        """Set the text value."""
        await asyncio.sleep(1)
