####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala number platform."""
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from thingwala.geyserwala.const import (
    GEYSERWALA_SETPOINT_TEMP_MIN,
    GEYSERWALA_SETPOINT_TEMP_MAX,
)

from .const import DOMAIN
from .entity import GeyserwalaEntity


@dataclass
class Number:
    """Entity params."""

    name: str
    id: str
    entity_category: str
    icon: str
    visible: bool


SENSORS = [
    Number("Setpoint", "setpoint", None, "mdi:thermostat", True),
    Number("External Setpoint", "external_setpoint", None, "mdi:thermostat", False),
]

SENSOR_MAP = {s.id: s for s in SENSORS}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaNumber(
            coordinator,
            NumberEntityDescription(
                key=item.id,
                has_entity_name=True,
                name=item.name,
                entity_category=item.entity_category,
                device_class=NumberDeviceClass.TEMPERATURE,
                native_min_value=GEYSERWALA_SETPOINT_TEMP_MIN,
                native_max_value=GEYSERWALA_SETPOINT_TEMP_MAX,
                native_step=1,
                unit_of_measurement=UnitOfTemperature.CELSIUS,
                icon=item.icon,
                entity_registry_visible_default=item.visible,
                entity_registry_enabled_default=True,
            ),
            item.id,
        )
        for item in SENSORS
    )


class GeyserwalaNumber(GeyserwalaEntity, NumberEntity):
    """Geyserwala number entity."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def native_value(self) -> int:
        """Value."""
        return getattr(self.coordinator.data, self._gw_id)

    async def async_set_native_value(self, value: float) -> None:
        """Set value."""
        await getattr(self.coordinator.data, f"set_{self._gw_id}")(value)
