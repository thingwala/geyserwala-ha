####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Diagnostics handler for Geyserwala integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# Fields that should be redacted from diagnostics for privacy
REDACT_FIELDS = {
    "host",
    "port",
    "username",
    "password",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    diagnostics_data: dict[str, Any] = {
        "entry": async_redact_data(entry.data, REDACT_FIELDS),
        "coordinator": {
            "name": coordinator.name,
            "last_update_success": coordinator.last_update_success,
            "last_update_attempt": coordinator.last_update_attempt.isoformat()
            if coordinator.last_update_attempt
            else None,
            "next_refresh": coordinator.async_request_refresh.__self__.last_update_interval.isoformat()
            if hasattr(coordinator, "async_request_refresh")
            else None,
        },
        "device_info": {},
    }

    if coordinator.data:
        # Extract device info from coordinator data
        device_data = {
            "id": coordinator.data.id if hasattr(coordinator.data, "id") else "Unknown",
            "name": coordinator.data.name if hasattr(coordinator.data, "name") else "Unknown",
            "hostname": coordinator.data.hostname
            if hasattr(coordinator.data, "hostname")
            else "Unknown",
        }
        diagnostics_data["device_info"] = device_data

    if coordinator.last_exception:
        diagnostics_data["last_error"] = {
            "type": type(coordinator.last_exception).__name__,
            "message": str(coordinator.last_exception),
        }

    return diagnostics_data
