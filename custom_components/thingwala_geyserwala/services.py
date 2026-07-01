####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Service handlers for Geyserwala integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.device_registry import async_get as async_get_device_registry

from .const import _LOGGER, DOMAIN


async def async_handle_set_boost(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle the set_boost service call."""
    device_id = call.data.get("device_id")
    enabled = call.data.get("enabled", False)
    duration_minutes = call.data.get("duration_minutes", 0)

    device_registry = async_get_device_registry(hass)
    device = device_registry.async_get(device_id)

    if not device:
        _LOGGER.error("[Geyserwala] Device not found: %s", device_id)
        return

    # Find the config entry for this device
    entry_id = None
    for config_entry_id in device.config_entries:
        if config_entry_id in hass.data[DOMAIN]:
            entry_id = config_entry_id
            break

    if not entry_id:
        _LOGGER.error("[Geyserwala] Config entry not found for device: %s", device_id)
        return

    coordinator = hass.data[DOMAIN][entry_id]
    gwc = coordinator.data

    try:
        if enabled:
            _LOGGER.debug(
                "[Geyserwala] Setting boost mode for device %s (duration: %s min)",
                device_id,
                duration_minutes,
            )
            # Note: The actual boost implementation depends on the thingwala client API
            # This is a placeholder that should be adapted based on actual client capabilities
            if hasattr(gwc, "set_boost"):
                await gwc.set_boost(enabled, duration_minutes)
            else:
                _LOGGER.warning("[Geyserwala] Device does not support set_boost: %s", device_id)
        else:
            _LOGGER.debug("[Geyserwala] Disabling boost mode for device %s", device_id)
            if hasattr(gwc, "set_boost"):
                await gwc.set_boost(False, 0)
            else:
                _LOGGER.warning("[Geyserwala] Device does not support set_boost: %s", device_id)
        await coordinator.async_request_refresh()
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.error("[Geyserwala] Error setting boost mode: %s", err)


async def async_handle_set_mode(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle the set_mode service call."""
    device_id = call.data.get("device_id")
    mode = call.data.get("mode")

    device_registry = async_get_device_registry(hass)
    device = device_registry.async_get(device_id)

    if not device:
        _LOGGER.error("[Geyserwala] Device not found: %s", device_id)
        return

    # Find the config entry for this device
    entry_id = None
    for config_entry_id in device.config_entries:
        if config_entry_id in hass.data[DOMAIN]:
            entry_id = config_entry_id
            break

    if not entry_id:
        _LOGGER.error("[Geyserwala] Config entry not found for device: %s", device_id)
        return

    coordinator = hass.data[DOMAIN][entry_id]
    gwc = coordinator.data

    try:
        _LOGGER.debug("[Geyserwala] Setting mode to %s for device %s", mode, device_id)
        if hasattr(gwc, "set_mode"):
            await gwc.set_mode(mode)
        else:
            _LOGGER.warning("[Geyserwala] Device does not support set_mode: %s", device_id)
        await coordinator.async_request_refresh()
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.error("[Geyserwala] Error setting mode: %s", err)


async def async_handle_read_error_codes(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle the read_error_codes service call."""
    device_id = call.data.get("device_id")

    device_registry = async_get_device_registry(hass)
    device = device_registry.async_get(device_id)

    if not device:
        _LOGGER.error("[Geyserwala] Device not found: %s", device_id)
        return

    # Find the config entry for this device
    entry_id = None
    for config_entry_id in device.config_entries:
        if config_entry_id in hass.data[DOMAIN]:
            entry_id = config_entry_id
            break

    if not entry_id:
        _LOGGER.error("[Geyserwala] Config entry not found for device: %s", device_id)
        return

    coordinator = hass.data[DOMAIN][entry_id]
    gwc = coordinator.data

    try:
        _LOGGER.debug("[Geyserwala] Reading error codes from device %s", device_id)
        if hasattr(gwc, "read_error_codes"):
            error_codes = await gwc.read_error_codes()
            _LOGGER.info("[Geyserwala] Device %s error codes: %s", device_id, error_codes)
        else:
            _LOGGER.warning("[Geyserwala] Device does not support read_error_codes: %s", device_id)
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.error("[Geyserwala] Error reading error codes: %s", err)


async def async_handle_clear_error_codes(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle the clear_error_codes service call."""
    device_id = call.data.get("device_id")

    device_registry = async_get_device_registry(hass)
    device = device_registry.async_get(device_id)

    if not device:
        _LOGGER.error("[Geyserwala] Device not found: %s", device_id)
        return

    # Find the config entry for this device
    entry_id = None
    for config_entry_id in device.config_entries:
        if config_entry_id in hass.data[DOMAIN]:
            entry_id = config_entry_id
            break

    if not entry_id:
        _LOGGER.error("[Geyserwala] Config entry not found for device: %s", device_id)
        return

    coordinator = hass.data[DOMAIN][entry_id]
    gwc = coordinator.data

    try:
        _LOGGER.debug("[Geyserwala] Clearing error codes for device %s", device_id)
        if hasattr(gwc, "clear_error_codes"):
            await gwc.clear_error_codes()
            _LOGGER.info("[Geyserwala] Error codes cleared for device %s", device_id)
        else:
            _LOGGER.warning("[Geyserwala] Device does not support clear_error_codes: %s", device_id)
        await coordinator.async_request_refresh()
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.error("[Geyserwala] Error clearing error codes: %s", err)


async def async_register_services(hass: HomeAssistant) -> None:
    """Register all custom services."""
    hass.services.async_register(
        DOMAIN,
        "set_boost",
        async_handle_set_boost,
        schema=None,  # Using service yaml schema
    )
    hass.services.async_register(
        DOMAIN,
        "set_mode",
        async_handle_set_mode,
        schema=None,  # Using service yaml schema
    )
    hass.services.async_register(
        DOMAIN,
        "read_error_codes",
        async_handle_read_error_codes,
        schema=None,  # Using service yaml schema
    )
    hass.services.async_register(
        DOMAIN,
        "clear_error_codes",
        async_handle_clear_error_codes,
        schema=None,  # Using service yaml schema
    )
    _LOGGER.debug("[Geyserwala] Custom services registered")
