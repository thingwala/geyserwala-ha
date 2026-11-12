####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala time platform: timer start and end times."""

from datetime import time

from homeassistant.components.time import (
    TimeEntity,
    TimeEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .timers import GeyserwalaTimerEntity, timer_coordinator_key, timer_ids

TIMER_TIME_FIELDS = {
    # field: (timer key, name, icon)
    "start": ("begin", "Start", "mdi:clock-start"),
    "end": ("end", "End", "mdi:clock-end"),
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala timer start/end entities."""

    entity_domain = 'time'
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    timer_coordinator = hass.data[DOMAIN][timer_coordinator_key(config_entry.entry_id)]

    async_add_entities(
        GeyserwalaTimerTime(
            hass, entity_domain,
            coordinator,
            timer_coordinator,
            TimeEntityDescription(
                key=f"timer_{timer_id}_{field}",
                has_entity_name=True,
                name=f"Timer {number} {name}",
                icon=icon,
                entity_registry_visible_default=True,
                entity_registry_enabled_default=True,
            ),
            timer_id,
            number,
            field,
            timer_key,
        )
        for number, timer_id in enumerate(timer_ids(timer_coordinator), start=1)
        for field, (timer_key, name, icon) in TIMER_TIME_FIELDS.items()
    )


class GeyserwalaTimerTime(GeyserwalaTimerEntity, TimeEntity):
    """Start or end time of a Geyserwala timer."""

    def __init__(self, hass, entity_domain, coordinator, timer_coordinator,
                 description, timer_id, timer_number, field, timer_key):
        super().__init__(hass, entity_domain, coordinator, timer_coordinator,
                         description, timer_id, timer_number, field)
        self._timer_key = timer_key

    @property
    def native_value(self) -> time | None:
        """Value."""
        timer = self.timer
        if timer is None:
            return None
        try:
            hour, minute = timer[self._timer_key][:2]
            return time(int(hour), int(minute))
        except (KeyError, TypeError, ValueError):
            return None

    async def async_set_value(self, value: time) -> None:
        """Set the time (minutes resolution)."""
        await self._async_update_timer(**{self._timer_key: [value.hour, value.minute]})
