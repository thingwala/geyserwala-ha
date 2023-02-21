####################################################################################
# Copyright (c) 2023 ThingWala                                                     #
####################################################################################
"""Geyserwala sensor platform."""
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import GeyserwalaEntity


@dataclass
class Sensor:
    """Entity params."""

    name: str
    id: str
    entity_category: str
    icon: str
    visible: bool


SENSORS = [
    Sensor("Water Temperature", "tank_temp", None, "mdi:thermometer-water", True),
    Sensor("Collector Temperature", "collector_temp", None, "mdi:sun-thermometer", False),
]

SENSOR_MAP = {s.id: s for s in SENSORS}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaSensor(
            coordinator,
            SensorEntityDescription(
                key=item.id,
                has_entity_name=True,
                name=item.name,
                entity_category=item.entity_category,
                device_class=SensorDeviceClass.TEMPERATURE,
                unit_of_measurement=UnitOfTemperature.CELSIUS,
                state_class=SensorStateClass.MEASUREMENT,
                icon=item.icon,
                entity_registry_visible_default=item.visible,
                entity_registry_enabled_default=True,
            ),
            item.id,
        )
        for item in SENSORS
    )


class GeyserwalaSensor(GeyserwalaEntity, SensorEntity):
    """Geyserwala sensor entity."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def native_value(self) -> int:
        """Value."""
        return getattr(self.coordinator.data, self._gw_id)
