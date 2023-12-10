####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala binary sensor platform."""
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import GeyserwalaEntity


@dataclass
class BinarySensor:
    """Entity params."""

    name: str
    id: str
    entity_category: str
    device_class: str
    icon_on: str
    icon_off: str
    visible: bool


BINARY_SENSORS = [
    BinarySensor("Pump", "pump_status", None, BinarySensorDeviceClass.RUNNING, "mdi:water-pump", "mdi:water-pump-off", False),
    BinarySensor("Element", "element_demand", None, BinarySensorDeviceClass.POWER, "mdi:radiator", "mdi:radiator-off", True),
]

BINARY_SENSOR_MAP = {s.id: s for s in BINARY_SENSORS}


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Geyserwala binary sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaBinarySensor(
            coordinator,
            BinarySensorEntityDescription(
                key=item.id,
                has_entity_name=True,
                name=item.name,
                entity_category=item.entity_category,
                device_class=item.device_class,
                entity_registry_visible_default=item.visible,
                entity_registry_enabled_default=True,
            ),
            item.id
        )
        for item in BINARY_SENSORS
    )


class GeyserwalaBinarySensor(GeyserwalaEntity, BinarySensorEntity):
    """Geyserwala binary sensor entity."""

    @property
    def is_on(self) -> bool:
        """State."""
        return getattr(self.coordinator.data, self._gw_id)

    @property
    def icon(self) -> str:
        """Icon."""
        if self.is_on:
            return BINARY_SENSOR_MAP[self._gw_id].icon_on
        return BINARY_SENSOR_MAP[self._gw_id].icon_off
