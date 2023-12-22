####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala sensor platform."""

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import voluptuous as vol

from .const import DOMAIN
from .entity import GeyserwalaEntity, gen_entity_dataclasses

SENSOR_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required('key'): cv.string,
    vol.Optional('device_class', default=None): vol.Any(None, cv.string),
    vol.Optional('icon', default='mdi:gauge'): cv.string,
    vol.Optional('visible', default=False): cv.boolean,
    vol.Optional('unit', default=None): vol.Any(None, cv.string),
})


SENSORS = []
SENSOR_MAP = {}


@dataclass
class Sensor:
    """Entity params."""

    name: str
    key: str
    device_class: str
    icon: str
    visible: bool
    unit: str


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala sensor entities."""

    entities = hass.data.get(DOMAIN + '_ENTITIES')
    for dc in gen_entity_dataclasses(entities, 'sensor', Sensor):
        SENSORS.append(dc)
        SENSOR_MAP[dc.key] = dc

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaSensor(
            coordinator,
            SensorEntityDescription(
                key=item.key,
                has_entity_name=True,
                name=item.name,
                entity_category=None,
                device_class=item.device_class,
                native_unit_of_measurement=item.unit,
                state_class=SensorStateClass.MEASUREMENT,
                icon=item.icon,
                entity_registry_visible_default=item.visible,
                entity_registry_enabled_default=True,
            ),
            item.key,
        )
        for item in SENSORS
    )


class GeyserwalaSensor(GeyserwalaEntity, SensorEntity):
    """Geyserwala sensor entity."""

    @property
    def native_value(self) -> int:
        """Value."""
        return self.coordinator.data.get_value(self._gw_key)
