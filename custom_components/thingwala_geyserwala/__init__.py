####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala integration by Thingwala."""

from __future__ import annotations

import asyncio
import importlib
import json
from datetime import timedelta
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

try:
    GeyserwalaClientAsync = importlib.import_module(
        "thingwala.geyserwala.aio.client"
    ).GeyserwalaClientAsync
    geyserwala_errors = importlib.import_module("thingwala.geyserwala.errors")
    GeyserwalaException = geyserwala_errors.GeyserwalaException
    Unauthorized = geyserwala_errors.Unauthorized
except ModuleNotFoundError:  # pragma: no cover - lets local tests import the module.
    GeyserwalaClientAsync = Any  # type: ignore[assignment]

    class GeyserwalaException(Exception):
        """Fallback exception used when the external client package is unavailable."""

    class Unauthorized(Exception):
        """Fallback exception used when the external client package is unavailable."""


from .alerts import AlertEvaluator, AlertRule
from .binary_sensor import BINARY_SENSOR_SCHEMA
from .const import (
    _LOGGER,
    DEFAULT_UPDATE_INTERVAL_SECONDS,
    DOMAIN,
    MIN_UPDATE_INTERVAL_SECONDS,
)
from .entities import ENTITIES
from .number import NUMBER_SCHEMA
from .sensor import SENSOR_SCHEMA
from .services import async_register_services
from .switch import SWITCH_SCHEMA
from .text import TEXT_SCHEMA

MAX_UPDATE_RETRIES = 2

PLATFORMS: list[Platform] = [
    Platform.TEXT,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(DOMAIN): vol.Schema(
            {
                vol.Optional("custom_entities"): vol.Schema(
                    {
                        vol.Optional(Platform.SENSOR.value): vol.All(
                            cv.ensure_list, [SENSOR_SCHEMA]
                        ),
                        vol.Optional(Platform.BINARY_SENSOR.value): vol.All(
                            cv.ensure_list, [BINARY_SENSOR_SCHEMA]
                        ),
                        vol.Optional(Platform.SWITCH.value): vol.All(
                            cv.ensure_list, [SWITCH_SCHEMA]
                        ),
                        vol.Optional(Platform.NUMBER.value): vol.All(
                            cv.ensure_list, [NUMBER_SCHEMA]
                        ),
                        vol.Optional(Platform.TEXT.value): vol.All(cv.ensure_list, [TEXT_SCHEMA]),
                    }
                ),
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


def get_update_interval(entry: ConfigEntry) -> timedelta:
    """Get the poll interval from options with safe bounds and fallback."""
    seconds = entry.options.get("update_interval", DEFAULT_UPDATE_INTERVAL_SECONDS)
    try:
        parsed = max(int(seconds), MIN_UPDATE_INTERVAL_SECONDS)
    except (TypeError, ValueError):
        parsed = DEFAULT_UPDATE_INTERVAL_SECONDS
    return timedelta(seconds=parsed)


def _parse_calibrations(entry: ConfigEntry) -> dict[str, Any]:
    """Parse calibration configurations from options, supporting both dict and JSON string formats."""
    calibrations = entry.options.get("calibrations", {})

    # If calibrations_json is provided (new format from config flow), parse it
    calibrations_json = entry.options.get("calibrations_json", "").strip()
    if calibrations_json:
        try:
            parsed = json.loads(calibrations_json)
            if isinstance(parsed, dict):
                _LOGGER.debug("[Geyserwala] Loaded calibrations from JSON")
                return parsed
        except json.JSONDecodeError as err:
            _LOGGER.warning("[Geyserwala] Invalid calibrations JSON: %s", err)

    # Use dict format (backward compatibility or already converted)
    return calibrations if isinstance(calibrations, dict) else {}


def _parse_alert_rules(entry: ConfigEntry) -> list[AlertRule]:
    """Parse alert rule configurations from options, supporting both list and JSON string formats."""
    alert_rules_data = entry.options.get("alert_rules", [])

    # If alert_rules_json is provided (new format from config flow), parse it
    alert_rules_json = entry.options.get("alert_rules_json", "").strip()
    if alert_rules_json:
        try:
            parsed = json.loads(alert_rules_json)
            if isinstance(parsed, list):
                _LOGGER.debug("[Geyserwala] Loaded %d alert rules from JSON", len(parsed))
                return [AlertRule.from_dict(rule_data) for rule_data in parsed]
        except (json.JSONDecodeError, ValueError, KeyError) as err:
            _LOGGER.warning("[Geyserwala] Invalid alert rules JSON: %s", err)

    # Use list format (backward compatibility or already converted)
    if isinstance(alert_rules_data, list):
        return [AlertRule.from_dict(rule_data) for rule_data in alert_rules_data]
    return []


def _merge_custom_entities(hass: HomeAssistant, config: dict[str, Any]) -> None:
    """Merge optional YAML-defined custom entities into the default entity map."""
    yaml_config = config.get(DOMAIN)
    merged = {key: list(value) for key, value in ENTITIES.items()}

    if yaml_config and "custom_entities" in yaml_config:
        for entity_type, entities in yaml_config["custom_entities"].items():
            merged.setdefault(entity_type, [])
            merged[entity_type].extend(entities)

    hass.data[f"{DOMAIN}_ENTITIES"] = merged


async def _async_update_status(gwc: Any, entry: ConfigEntry) -> Any:
    """Update device status with bounded retries and clearer failures."""
    host = entry.data["host"]
    port = entry.data["port"]

    for attempt in range(1, MAX_UPDATE_RETRIES + 2):
        try:
            async with asyncio.timeout(20):
                updated = await gwc.update()

            if not updated:
                raise UpdateFailed("Device did not return updated data")

            return gwc
        except Unauthorized as err:
            _LOGGER.error("[Geyserwala] Authentication failed for %s:%s", host, port)
            raise ConfigEntryAuthFailed from err
        except (TimeoutError, GeyserwalaException, OSError) as err:
            if attempt > MAX_UPDATE_RETRIES:
                raise UpdateFailed(
                    f"Update failed after {MAX_UPDATE_RETRIES + 1} attempts: {err}"
                ) from err
            delay = attempt * 0.5
            _LOGGER.warning(
                "[Geyserwala] Update attempt %s/%s failed for %s:%s (%s). Retrying in %.1fs",
                attempt,
                MAX_UPDATE_RETRIES + 1,
                host,
                port,
                err,
                delay,
            )
            await asyncio.sleep(delay)

    raise UpdateFailed("Unexpected update loop termination")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Geyserwala from a config entry."""
    session = async_create_clientsession(hass)
    gwc = GeyserwalaClientAsync(
        host=entry.data["host"],
        port=entry.data["port"],
        username=entry.data["username"],
        password=entry.data["password"],
        session=session,
    )

    coordinator = DataUpdateCoordinator[Any](
        hass,
        _LOGGER,
        config_entry=entry,
        name=DOMAIN.title(),
        update_method=lambda: _async_update_status(gwc, entry),
        update_interval=get_update_interval(entry),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Feature flags - determine which features are enabled
    enable_calibration = entry.options.get("enable_calibration", False)
    enable_alerts = entry.options.get("enable_alerts", False)
    enable_services = entry.options.get("enable_services", True)

    # Store calibration settings for this entry (only if enabled)
    if enable_calibration:
        calibrations = _parse_calibrations(entry)
        _LOGGER.debug(
            "[Geyserwala] Calibration feature enabled with %d entity calibrations",
            len(calibrations),
        )
    else:
        calibrations = {}
        _LOGGER.debug("[Geyserwala] Calibration feature disabled")

    hass.data.setdefault(f"{DOMAIN}_calibrations", {})[entry.entry_id] = calibrations

    # Set up alert evaluator for this entry (only if enabled)
    if enable_alerts:
        alert_evaluator = AlertEvaluator(hass)
        hass.data.setdefault(f"{DOMAIN}_alert_evaluators", {})[entry.entry_id] = alert_evaluator

        # Load alert rules from options
        alert_rules = _parse_alert_rules(entry)
        _LOGGER.debug("[Geyserwala] Alert feature enabled with %d rules", len(alert_rules))
        hass.data.setdefault(f"{DOMAIN}_alert_rules", {})[entry.entry_id] = alert_rules
    else:
        _LOGGER.debug("[Geyserwala] Alert feature disabled")
        hass.data.setdefault(f"{DOMAIN}_alert_evaluators", {})[entry.entry_id] = None
        hass.data.setdefault(f"{DOMAIN}_alert_rules", {})[entry.entry_id] = []

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=gwc.id)

    entry.async_on_unload(entry.add_update_listener(_async_handle_options_update))

    # Register services only once and only if enabled (when first entry is added)
    if enable_services and len(hass.data[DOMAIN]) == 1:
        _LOGGER.debug("[Geyserwala] Registering custom services")
        await async_register_services(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        hass.data.get(f"{DOMAIN}_calibrations", {}).pop(entry.entry_id, None)
        hass.data.get(f"{DOMAIN}_alert_evaluators", {}).pop(entry.entry_id, None)
        hass.data.get(f"{DOMAIN}_alert_rules", {}).pop(entry.entry_id, None)
    return unload_ok


async def _async_handle_options_update(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry after options changes."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up integration from YAML for custom entities support."""
    _merge_custom_entities(hass, config)
    return True
