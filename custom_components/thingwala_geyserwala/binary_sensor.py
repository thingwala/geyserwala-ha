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

BINARY_SENSORS = []
BINARY_SENSOR_MAP = {}


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

    entities = hass.data.get(DOMAIN + '_ENTITIES')
    for dc in gen_entity_dataclasses(entities, 'binary_sensor', BinarySensor):
        BINARY_SENSORS.append(dc)
        BINARY_SENSOR_MAP[dc.key] = dc

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaBinarySensor(
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
            item.key
        )
        for item in BINARY_SENSORS
    )


class GeyserwalaBinarySensor(GeyserwalaEntity, BinarySensorEntity):
    """Geyserwala binary sensor entity."""

    @property
    def is_on(self) -> bool:
        """State."""
        return self.coordinator.data.get_value(self._gw_key)

    @property
    def icon(self) -> str:
        """Icon."""
        if self.is_on:
            return BINARY_SENSOR_MAP[self._gw_key].icon_on
        return BINARY_SENSOR_MAP[self._gw_key].icon_off
