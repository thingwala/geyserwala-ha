####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala switch platform."""

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
    SwitchDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONF_NAME,
    EntityCategory,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import voluptuous as vol

from .const import DOMAIN
from .entity import GeyserwalaEntity, gen_entity_dataclasses
from .timers import (
    TIMER_DAYS,
    TIMER_DAY_NAMES,
    GeyserwalaTimerEntity,
    timer_coordinator_key,
    timer_ids,
)

SWITCH_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required('key'): cv.string,
    vol.Optional('icon_on', default='mdi:toggle-switch'): cv.string,
    vol.Optional('icon_off', default='mdi:toggle-switch-off'): cv.string,
    vol.Optional('visible', default=False): cv.boolean,
})


@dataclass
class Switch:
    """Entity params."""

    name: str
    key: str
    icon_on: str
    icon_off: str
    visible: bool


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala switch entities."""

    entity_domain = 'switch'
    switches = []
    switch_map = {}

    entities = hass.data.get(DOMAIN + '_ENTITIES')
    for dc in gen_entity_dataclasses(entities, entity_domain, Switch):
        switches.append(dc)
        switch_map[dc.key] = dc

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaSwitch(
            hass, entity_domain,
            coordinator,
            SwitchEntityDescription(
                key=item.key,
                has_entity_name=True,
                name=item.name,
                entity_category=None,
                device_class=SwitchDeviceClass.SWITCH,
                entity_registry_visible_default=item.visible,
                entity_registry_enabled_default=True,
            ),
            item.key,
            switch_map
        )
        for item in switches
    )

    timer_coordinator = hass.data[DOMAIN][timer_coordinator_key(config_entry.entry_id)]
    async_add_entities(
        GeyserwalaTimerDaySwitch(
            hass, entity_domain,
            coordinator,
            timer_coordinator,
            SwitchEntityDescription(
                key=f"timer_{timer_id}_{day}",
                has_entity_name=True,
                name=f"Timer {number} {day_name}",
                icon="mdi:calendar-week",
                entity_category=EntityCategory.CONFIG,
                entity_registry_visible_default=True,
                entity_registry_enabled_default=False,
            ),
            timer_id,
            number,
            day,
            day_index,
        )
        for number, timer_id in enumerate(timer_ids(timer_coordinator), start=1)
        for day_index, (day, day_name) in enumerate(zip(TIMER_DAYS, TIMER_DAY_NAMES))
    )


class GeyserwalaSwitch(GeyserwalaEntity, SwitchEntity):
    """Geyserwala switch entity."""
    def __init__(self, hass, entity_domain, coordinator, description, gw_key, switch_map):
        super().__init__(hass, entity_domain, coordinator, description, gw_key)
        self._switch_map = switch_map

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn on."""
        await self.coordinator.data.set_value(self._gw_key, True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn off."""
        await self.coordinator.data.set_value(self._gw_key, False)

    @property
    def is_on(self) -> bool:
        """State."""
        return self.coordinator.data.get_value(self._gw_key)

    @property
    def icon(self) -> str:
        """Icon."""
        if self.is_on:
            return self._switch_map[self._gw_key].icon_on
        return self._switch_map[self._gw_key].icon_off


class GeyserwalaTimerDaySwitch(GeyserwalaTimerEntity, SwitchEntity):
    """Whether a Geyserwala timer runs on one day of the week."""

    def __init__(self, hass, entity_domain, coordinator, timer_coordinator,
                 description, timer_id, timer_number, field, day_index):
        super().__init__(hass, entity_domain, coordinator, timer_coordinator,
                         description, timer_id, timer_number, field)
        self._day_index = day_index

    @property
    def is_on(self) -> bool | None:
        """State."""
        timer = self.timer
        try:
            return bool(timer["dow"][self._day_index])
        except (KeyError, TypeError, IndexError):
            return None

    async def _async_set_day(self, on: bool) -> None:
        timer = self.timer
        if timer is None:
            return
        dow = list(timer.get("dow") or [False] * 7)
        dow[self._day_index] = on
        await self._async_update_timer(dow=dow)

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn on."""
        await self._async_set_day(True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn off."""
        await self._async_set_day(False)
