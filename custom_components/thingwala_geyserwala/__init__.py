####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala integration by Thingwala."""

from datetime import timedelta
from typing import List

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import (
    # async_get_clientsession
    async_create_clientsession,
)
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

import voluptuous as vol

from thingwala.geyserwala.aio.client import GeyserwalaClientAsync
import thingwala.geyserwala.errors

from .const import DOMAIN, _LOGGER
from .entities import ENTITIES

from .sensor import SENSOR_SCHEMA
from .binary_sensor import BINARY_SENSOR_SCHEMA
from .switch import SWITCH_SCHEMA
from .number import NUMBER_SCHEMA

PLATFORMS: List[Platform] = [
    Platform.TEXT,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]

CONFIG_SCHEMA = vol.Schema({
    vol.Optional(DOMAIN): vol.Schema({
        vol.Optional('custom_entities'): vol.Schema({
            vol.Optional(Platform.SENSOR.value): vol.All(cv.ensure_list, [SENSOR_SCHEMA]),
            vol.Optional(Platform.BINARY_SENSOR.value): vol.All(cv.ensure_list, [BINARY_SENSOR_SCHEMA]),
            vol.Optional(Platform.SWITCH.value): vol.All(cv.ensure_list, [SWITCH_SCHEMA]),
            vol.Optional(Platform.NUMBER.value): vol.All(cv.ensure_list, [NUMBER_SCHEMA]),
        }),
    }),
}, extra=vol.ALLOW_EXTRA)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up as config entry."""
    async def _async_update_status():
        async with async_timeout.timeout(20):
            try:
                await gwc.update()
            except thingwala.geyserwala.errors.RequestError as ex:
                raise UpdateFailed(ex) from ex
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


async def async_setup(hass: HomeAssistant, config: dict):
    yaml_config = config.get(DOMAIN)
    if yaml_config and 'custom_entities' in yaml_config:
        for entity_type, entities in yaml_config['custom_entities'].items():
            if entity_type not in ENTITIES:
                ENTITIES[entity_type] = []
            ENTITIES[entity_type].extend(entities)
    hass.data[DOMAIN + '_ENTITIES'] = ENTITIES

    return True
