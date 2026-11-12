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
    CONF_NAME,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import voluptuous as vol

from thingwala.geyserwala.const import (
    GEYSERWALA_SETPOINT_TEMP_MIN,
    GEYSERWALA_SETPOINT_TEMP_MAX,
)

from .const import DOMAIN
from .entity import GeyserwalaEntity, gen_entity_dataclasses
from .timers import GeyserwalaTimerEntity, timer_coordinator_key, timer_ids

NUMBER_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required('key'): cv.string,
    vol.Optional('device_class', default=None): vol.Any(None, cv.string),
    vol.Optional('icon', default='mdi:numeric'): cv.string,
    vol.Optional('visible', default=False): cv.boolean,
    vol.Optional('min', default=0): cv.positive_int,
    vol.Optional('max', default=4294967296): cv.positive_int,
    vol.Optional('unit', default=None): vol.Any(None, cv.string),
})


@dataclass
class Number:
    """Entity params."""

    name: str
    key: str
    device_class: str
    icon: str
    visible: bool
    min: int
    max: int
    unit: str


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala number entities."""

    entity_domain = 'number'
    numbers = []

    entities = hass.data.get(DOMAIN + '_ENTITIES')
    for dc in gen_entity_dataclasses(entities, entity_domain, Number):
        numbers.append(dc)

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaNumber(
            hass, entity_domain,
            coordinator,
            NumberEntityDescription(
                key=item.key,
                has_entity_name=True,
                name=item.name,
                entity_category=None,
                device_class=item.device_class,
                native_min_value=item.min,
                native_max_value=item.max,
                native_step=1,
                native_unit_of_measurement=item.unit,
                icon=item.icon,
                entity_registry_visible_default=item.visible,
                entity_registry_enabled_default=True,
            ),
            item.key,
        )
        for item in numbers
    )

    timer_coordinator = hass.data[DOMAIN][timer_coordinator_key(config_entry.entry_id)]
    async_add_entities(
        GeyserwalaTimerTemperature(
            hass, entity_domain,
            coordinator,
            timer_coordinator,
            NumberEntityDescription(
                key=f"timer_{timer_id}_temperature",
                has_entity_name=True,
                name=f"Timer {number} Temperature",
                device_class=NumberDeviceClass.TEMPERATURE,
                native_min_value=GEYSERWALA_SETPOINT_TEMP_MIN,
                native_max_value=GEYSERWALA_SETPOINT_TEMP_MAX,
                native_step=1,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                icon="mdi:thermometer-water",
                entity_registry_visible_default=True,
                entity_registry_enabled_default=True,
            ),
            timer_id,
            number,
            "temperature",
        )
        for number, timer_id in enumerate(timer_ids(timer_coordinator), start=1)
    )


class GeyserwalaNumber(GeyserwalaEntity, NumberEntity):
    """Geyserwala number entity."""

    @property
    def native_value(self) -> int:
        """Value."""
        return self.coordinator.data.get_value(self._gw_key)

    async def async_set_native_value(self, value: float) -> None:
        """Set value."""
        await self.coordinator.data.set_value(self._gw_key, value)


class GeyserwalaTimerTemperature(GeyserwalaTimerEntity, NumberEntity):
    """Target temperature of a Geyserwala timer."""

    @property
    def native_value(self) -> int | None:
        """Value."""
        timer = self.timer
        return None if timer is None else timer.get("temp")

    async def async_set_native_value(self, value: float) -> None:
        """Set value."""
        await self._async_update_timer(temp=int(value))
