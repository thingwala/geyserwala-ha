####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala switch platform."""

from dataclasses import dataclass
from typing import Any

import voluptuous as vol
from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import GeyserwalaEntity
from .platform_setup import async_setup_platform_entry

SWITCH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("key"): cv.string,
        vol.Optional("icon_on", default="mdi:toggle-switch"): cv.string,
        vol.Optional("icon_off", default="mdi:toggle-switch-off"): cv.string,
        vol.Optional("visible", default=False): cv.boolean,
        vol.Optional("entity_category", default=None): vol.Any(None, cv.string),
    }
)


@dataclass
class Switch:
    """Entity params."""

    name: str
    key: str
    icon_on: str
    icon_off: str
    visible: bool
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
    """Set up Geyserwala switch entities using generic helper."""
    await async_setup_platform_entry(
        hass=hass,
        config_entry=config_entry,
        async_add_entities=async_add_entities,
        entity_domain="switch",
        dc_class=Switch,
        entity_class=GeyserwalaSwitch,
        description_factory=lambda item: SwitchEntityDescription(
            key=item.key,
            has_entity_name=True,
            name=item.name,
            entity_category=_map_entity_category(item.entity_category),
            device_class=SwitchDeviceClass.SWITCH,
            entity_registry_visible_default=item.visible,
            entity_registry_enabled_default=True,
        ),
        entity_map={},
    )


class GeyserwalaSwitch(GeyserwalaEntity, SwitchEntity):
    """Geyserwala switch entity."""

    def __init__(self, hass, entity_domain, coordinator, description, gw_key, switch_map):
        super().__init__(hass, entity_domain, coordinator, description, gw_key)
        self._switch_map = switch_map

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn on."""
        await self.coordinator.data.set_value(self._gw_key, True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn off."""
        await self.coordinator.data.set_value(self._gw_key, False)

    @property
    def is_on(self) -> bool:
        """State."""
        return self.coordinator.data.get_value(self._gw_key)

    @property
    def icon(self) -> str:
        """Icon."""
        mapped = self._switch_map.get(self._gw_key)
        if mapped is None:
            return "mdi:toggle-switch"
        if self.is_on:
            return mapped.icon_on
        return mapped.icon_off
