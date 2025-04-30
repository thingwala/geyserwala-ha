####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala switch platform."""

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
    SwitchDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import voluptuous as vol

from .const import DOMAIN
from .entity import GeyserwalaEntity, gen_entity_dataclasses

SWITCH_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required('key'): cv.string,
    vol.Optional('icon_on', default='mdi:toggle-switch'): cv.string,
    vol.Optional('icon_off', default='mdi:toggle-switch-off'): cv.string,
    vol.Optional('visible', default=False): cv.boolean,
})


@dataclass
class Switch:
    """Entity params."""

    name: str
    key: str
    icon_on: str
    icon_off: str
    visible: bool


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala switch entities."""

    entity_domain = 'switch'
    switches = []
    switch_map = {}

    entities = hass.data.get(DOMAIN + '_ENTITIES')
    for dc in gen_entity_dataclasses(entities, entity_domain, Switch):
        switches.append(dc)
        switch_map[dc.key] = dc

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaSwitch(
            hass, entity_domain,
            coordinator,
            SwitchEntityDescription(
                key=item.key,
                has_entity_name=True,
                name=item.name,
                entity_category=None,
                device_class=SwitchDeviceClass.SWITCH,
                entity_registry_visible_default=item.visible,
                entity_registry_enabled_default=True,
            ),
            item.key,
            switch_map
        )
        for item in switches
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
        if self.is_on:
            return self._switch_map[self._gw_key].icon_on
        return self._switch_map[self._gw_key].icon_off
