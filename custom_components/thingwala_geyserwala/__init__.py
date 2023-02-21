####################################################################################
# Copyright (c) 2023 ThingWala                                                     #
####################################################################################
"""Geyserwala integration by ThingWala."""

from datetime import timedelta
from typing import List

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import (
    # async_get_clientsession
    async_create_clientsession,
)
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from thingwala.geyserwala.aio.client import GeyserwalaClientAsync

from .const import DOMAIN, _LOGGER


PLATFORMS: List[Platform] = [
    Platform.TEXT,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up as config entry."""
    async def _async_update_status():
        async with async_timeout.timeout(20):
            try:
                await gwc.update_status()
            except Exception as ex:
                _LOGGER.exception("GeyserwalaClientAsync.update_status")
                raise UpdateFailed(ex) from ex
        return gwc

    # session=async_get_clientsession(hass)
    session = async_create_clientsession(hass)

    gwc = GeyserwalaClientAsync(
        host=entry.data['host'],
        port=entry.data['port'],
        username=entry.data['username'],
        password=entry.data['password'],
        session=session,
    )

    coordinator = DataUpdateCoordinator[GeyserwalaClientAsync](
        hass,
        _LOGGER,
        name=DOMAIN.title(),
        update_method=_async_update_status,
        update_interval=timedelta(seconds=2),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=gwc.id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
