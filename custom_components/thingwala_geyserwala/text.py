####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala text platform."""

from dataclasses import dataclass

import voluptuous as vol
from homeassistant.components.text import (
    TextEntity,
    TextEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import GeyserwalaEntity
from .platform_setup import async_setup_platform_entry

TEXT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("key"): cv.string,
        vol.Optional("icon", default=None): vol.Any(None, cv.string),
        vol.Optional("visible", default=False): cv.boolean,
        vol.Optional("entity_category", default=None): vol.Any(None, cv.string),
    }
)


@dataclass
class Text:
    """Entity params."""

    name: str
    key: str
    visible: bool
    icon: str | None = None
    entity_category: str | None = None


def _map_entity_category(value: str | None) -> EntityCategory | None:
    """Map optional entity category string to Home Assistant enum."""
    if value == "config":
        return EntityCategory.CONFIG
    if value == "diagnostic":
        return EntityCategory.DIAGNOSTIC
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala text entities using generic helper."""
    await async_setup_platform_entry(
        hass=hass,
        config_entry=config_entry,
        async_add_entities=async_add_entities,
        entity_domain="text",
        dc_class=Text,
        entity_class=GeyserwalaText,
        description_factory=lambda item: TextEntityDescription(
            key=item.key,
            has_entity_name=True,
            name=item.name,
            entity_category=_map_entity_category(item.entity_category),
            icon=item.icon,
            entity_registry_visible_default=item.visible,
        ),
    )


class GeyserwalaText(GeyserwalaEntity, TextEntity):
    """Geyserwala text entity."""

    @property
    def native_value(self) -> str:
        """Value."""
        if self._gw_key.startswith("__"):
            return " "
        return self.coordinator.data.get_value(self._gw_key)

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        if self._gw_key.startswith("__"):
            return
        await self.coordinator.data.set_value(self._gw_key, value)
