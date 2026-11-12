####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala timer (schedule) support.

Timers are read with a separate, slower coordinator so the 2 second value
poll is unchanged. Entities are created per timer; when a timer is added or
deleted on the device the integration reloads itself to match.
"""

from copy import deepcopy
from datetime import timedelta

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityDescription, generate_entity_id
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from thingwala.geyserwala.aio.client import GeyserwalaClientAsync
import thingwala.geyserwala.errors

from .const import DOMAIN, _LOGGER

TIMER_UPDATE_INTERVAL = timedelta(seconds=60)

# Order of the "dow" (day of week) array in a timer.
TIMER_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
TIMER_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TIMER_DAY_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def timer_coordinator_key(entry_id: str) -> str:
    """hass.data[DOMAIN] key of an entry's timer coordinator."""
    return f"{entry_id}_timers"


def create_timer_coordinator(
    hass: HomeAssistant, entry: ConfigEntry, gwc: GeyserwalaClientAsync
) -> DataUpdateCoordinator:
    """Coordinator holding the list of timers."""

    async def _async_update_timers():
        async with async_timeout.timeout(20):
            try:
                timers = await gwc.list_timers()
            except thingwala.geyserwala.errors.RequestError as ex:
                raise UpdateFailed(ex) from ex
            except Exception as ex:
                _LOGGER.exception("GeyserwalaClientAsync.list_timers")
                raise UpdateFailed(ex) from ex
        if not isinstance(timers, list):
            raise UpdateFailed(f"Unexpected timer list: {timers!r}")
        return timers

    return DataUpdateCoordinator[list](
        hass,
        _LOGGER,
        config_entry=entry,
        name=f"{DOMAIN.title()} timers",
        update_method=_async_update_timers,
        update_interval=TIMER_UPDATE_INTERVAL,
    )


def timer_ids(timer_coordinator: DataUpdateCoordinator) -> list:
    """Timer ids in the order the device lists them."""
    return [t["id"] for t in (timer_coordinator.data or []) if "id" in t]


def hm_text(value) -> str:
    """[hour, minute] as HH:MM."""
    try:
        return f"{int(value[0]):02d}:{int(value[1]):02d}"
    except (TypeError, ValueError, IndexError):
        return "?"


def days_text(dow) -> str:
    """Short text for the active days, e.g. 'Mon-Fri', 'Every day'."""
    if not isinstance(dow, list) or len(dow) != 7:
        return "?"
    if all(dow):
        return "Every day"
    if not any(dow):
        return "No days"
    if dow == [True] * 5 + [False] * 2:
        return "Mon-Fri"
    if dow == [False] * 5 + [True] * 2:
        return "Weekends"
    return ", ".join(d for d, on in zip(TIMER_DAY_SHORT, dow) if on)


class GeyserwalaTimerEntity(CoordinatorEntity[DataUpdateCoordinator[list]]):
    """Base entity for one setting of one Geyserwala timer."""

    def __init__(
        self,
        hass: HomeAssistant,
        entity_domain: str,
        coordinator: DataUpdateCoordinator,
        timer_coordinator: DataUpdateCoordinator,
        description: EntityDescription,
        timer_id: int,
        timer_number: int,
        field: str,
    ) -> None:
        """Init."""
        super().__init__(timer_coordinator)
        self.entity_description = description
        self._gwc: GeyserwalaClientAsync = coordinator.data
        self._timer_id = timer_id
        self._field = field
        self._attr_unique_id = f"{DOMAIN}.{self._gwc.id}.timer_{timer_id}_{field}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, self._gwc.id)})
        slug = self._gwc.hostname.replace("-", "_").replace(".", "_").lower()
        self.entity_id = generate_entity_id(
            f"{entity_domain}.{{}}",
            f"{slug}_timer_{timer_number}_{field}",
            hass=hass,
        )

    @property
    def timer(self):
        """This entity's timer, or None if it no longer exists."""
        for timer in self.coordinator.data or []:
            if timer.get("id") == self._timer_id:
                return timer
        return None

    @property
    def available(self) -> bool:
        """Available while the timer exists on the device."""
        return super().available and self.timer is not None

    async def _async_update_timer(self, **changes) -> None:
        """Write changed fields of this timer to the device."""
        timer = self.timer
        if timer is None:
            return
        timer = deepcopy(timer)
        timer.update(changes)
        try:
            ret = await self._gwc.update_timer(timer)
        except Exception:
            await self.coordinator.async_request_refresh()
            raise
        # Show the change straight away; the next poll confirms it.
        if isinstance(ret, dict) and ret.get("id") == self._timer_id:
            timer = ret
        self.coordinator.async_set_updated_data([
            timer if t.get("id") == self._timer_id else t
            for t in self.coordinator.data or []
        ])
