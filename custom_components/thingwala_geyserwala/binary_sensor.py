####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala binary sensor platform."""

from dataclasses import dataclass

import voluptuous as vol
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import GeyserwalaEntity
from .platform_setup import async_setup_platform_entry

BINARY_SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("key"): cv.string,
        vol.Optional("device_class", default=None): vol.Any(None, cv.string),
        vol.Optional("icon_on", default="mdi:radiobox-marked"): cv.string,
        vol.Optional("icon_off", default="mdi:radiobox-blank"): cv.string,
        vol.Optional("visible", default=False): cv.boolean,
    }
)


@dataclass
class BinarySensor:
    """Entity params."""

    name: str
    key: str
    device_class: str
    icon_on: str
    icon_off: str
    visible: bool


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala binary sensor entities using generic helper."""
    await async_setup_platform_entry(
        hass=hass,
        config_entry=config_entry,
        async_add_entities=async_add_entities,
        entity_domain="binary_sensor",
        dc_class=BinarySensor,
        entity_class=GeyserwalaBinarySensor,
        description_factory=lambda item: BinarySensorEntityDescription(
            key=item.key,
            has_entity_name=True,
            name=item.name,
            entity_category=None,
            device_class=item.device_class,
            entity_registry_visible_default=item.visible,
            entity_registry_enabled_default=True,
        ),
        entity_map={},
    )


class GeyserwalaBinarySensor(GeyserwalaEntity, BinarySensorEntity):
    """Geyserwala binary sensor entity."""

    def __init__(self, hass, entity_domain, coordinator, description, gw_key, binary_sensor_map):
        super().__init__(hass, entity_domain, coordinator, description, gw_key)
        self._binary_sensor_map = binary_sensor_map

    @property
    def is_on(self) -> bool:
        """State."""
        return self.coordinator.data.get_value(self._gw_key)

    @property
    def icon(self) -> str:
        """Icon."""
        mapped = self._binary_sensor_map.get(self._gw_key)
        if mapped is None:
            return "mdi:radiobox-marked"
        if self.is_on:
            return mapped.icon_on
        return mapped.icon_off
