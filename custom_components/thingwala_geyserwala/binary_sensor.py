####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala binary sensor platform."""

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
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

BINARY_SENSOR_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required('key'): cv.string,
    vol.Optional('device_class', default=None): vol.Any(None, cv.string),
    vol.Optional('icon_on', default='mdi:radiobox-marked'): cv.string,
    vol.Optional('icon_off', default='mdi:radiobox-blank'): cv.string,
    vol.Optional('visible', default=False): cv.boolean,
})


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
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Geyserwala binary sensor entities."""

    entity_domain = 'binary_sensor'
    binary_sensors = []
    binary_sensor_map = {}

    entities = hass.data.get(DOMAIN + '_ENTITIES')
    for dc in gen_entity_dataclasses(entities, entity_domain, BinarySensor):
        binary_sensors.append(dc)
        binary_sensor_map[dc.key] = dc

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaBinarySensor(
            hass, entity_domain,
            coordinator,
            BinarySensorEntityDescription(
                key=item.key,
                has_entity_name=True,
                name=item.name,
                entity_category=None,
                device_class=item.device_class,
                entity_registry_visible_default=item.visible,
                entity_registry_enabled_default=True,
            ),
            item.key,
            binary_sensor_map
        )
        for item in binary_sensors
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
        if self.is_on:
            return self._binary_sensor_map[self._gw_key].icon_on
        return self._binary_sensor_map[self._gw_key].icon_off
