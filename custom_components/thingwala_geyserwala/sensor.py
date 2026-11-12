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
from .timers import (
    TIMER_DAYS,
    GeyserwalaTimerEntity,
    days_text,
    hm_text,
    timer_coordinator_key,
    timer_ids,
)

SENSOR_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required('key'): cv.string,
    vol.Optional('device_class', default=None): vol.Any(None, cv.string),
    vol.Optional('icon', default='mdi:gauge'): cv.string,
    vol.Optional('visible', default=False): cv.boolean,
    vol.Optional('unit', default=None): vol.Any(None, cv.string),
})


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

    entity_domain = 'sensor'
    sensors = []

    entities = hass.data.get(DOMAIN + '_ENTITIES')
    for dc in gen_entity_dataclasses(entities, entity_domain, Sensor):
        sensors.append(dc)

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaSensor(
            hass, entity_domain,
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
        for item in sensors
    )

    timer_coordinator = hass.data[DOMAIN][timer_coordinator_key(config_entry.entry_id)]
    async_add_entities(
        GeyserwalaTimerSensor(
            hass, entity_domain,
            coordinator,
            timer_coordinator,
            SensorEntityDescription(
                key=f"timer_{timer_id}",
                has_entity_name=True,
                name=f"Timer {number}",
                icon="mdi:timer-outline",
                entity_registry_visible_default=True,
                entity_registry_enabled_default=True,
            ),
            timer_id,
            number,
            "summary",
        )
        for number, timer_id in enumerate(timer_ids(timer_coordinator), start=1)
    )


class GeyserwalaSensor(GeyserwalaEntity, SensorEntity):
    """Geyserwala sensor entity."""

    @property
    def native_value(self) -> int:
        """Value."""
        return self.coordinator.data.get_value(self._gw_key)


class GeyserwalaTimerSensor(GeyserwalaTimerEntity, SensorEntity):
    """Summary of a Geyserwala timer, e.g. "08:00-09:45 45°C Mon-Fri"."""

    @property
    def native_value(self) -> str | None:
        """Value."""
        timer = self.timer
        if timer is None:
            return None
        return (
            f"{hm_text(timer.get('begin'))}-{hm_text(timer.get('end'))} "
            f"{timer.get('temp', '?')}°C {days_text(timer.get('dow'))}"
        )

    @property
    def extra_state_attributes(self):
        """Timer fields, for automations and templates."""
        timer = self.timer
        if timer is None:
            return None
        dow = timer.get("dow") or []
        return {
            "timer_id": timer.get("id"),
            "start": hm_text(timer.get("begin")),
            "end": hm_text(timer.get("end")),
            "temperature": timer.get("temp"),
            "days": [d for d, on in zip(TIMER_DAYS, dow) if on],
        }
