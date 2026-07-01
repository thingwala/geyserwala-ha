####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala config flow."""

from __future__ import annotations

import asyncio
import importlib
import json
from datetime import UTC, datetime
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_IP_ADDRESS, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import (
    async_create_clientsession,
)

try:
    from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
except ImportError:  # pragma: no cover - fallback for very old Home Assistant builds.
    ZeroconfServiceInfo = Any  # type: ignore[assignment]

from homeassistant.util.network import is_ipv6_address

try:
    GeyserwalaClientAsync = importlib.import_module(
        "thingwala.geyserwala.aio.client"
    ).GeyserwalaClientAsync
    geyserwala_errors = importlib.import_module("thingwala.geyserwala.errors")
    GeyserwalaException = geyserwala_errors.GeyserwalaException
    Unauthorized = geyserwala_errors.Unauthorized
    _DEPENDENCY_AVAILABLE = True
    _DEPENDENCY_IMPORT_ERROR: Exception | None = None
except ModuleNotFoundError as err:  # pragma: no cover - depends on runtime package installation.
    GeyserwalaClientAsync = Any  # type: ignore[assignment]

    class GeyserwalaException(Exception):
        """Fallback exception used when the external client package is unavailable."""

    class Unauthorized(Exception):
        """Fallback exception used when the external client package is unavailable."""

    _DEPENDENCY_AVAILABLE = False
    _DEPENDENCY_IMPORT_ERROR = err
except Exception as err:  # pragma: no cover - defensive to avoid config flow import crashes.
    GeyserwalaClientAsync = Any  # type: ignore[assignment]

    class GeyserwalaException(Exception):
        """Fallback exception used when the external client package fails to load."""

    class Unauthorized(Exception):
        """Fallback exception used when the external client package fails to load."""

    _DEPENDENCY_AVAILABLE = False
    _DEPENDENCY_IMPORT_ERROR = err

from .const import (
    _LOGGER,
    DEFAULT_PORT,
    DEFAULT_UPDATE_INTERVAL_SECONDS,
    DEFAULT_USERNAME,
    DOMAIN,
    MIN_UPDATE_INTERVAL_SECONDS,
)

_DEPENDENCY_ERROR_LOGGED = False
_CONNECTION_KEYS = (CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD)
_DEVICE_STATUS_KEYS = (
    "status",
    "version",
    "wifi-status",
    "cloud-status",
    "mqtt-up",
    "unixtime",
)
_DEVICE_SETTING_KEYS = (
    "wifi-ssid",
    "wifi-pass",
    "cloud-token",
    "name",
    "hostname",
    "setpoint-max",
    "gw-diff",
    "gw-antifreeze",
    "dc-max-temp",
    "gw-ldr-min",
    "app-enable",
    "app-pass",
    "utc-offset",
    "ntp-host",
    "ntp-port",
    "mqtt-enable",
    "mqtt-host",
    "mqtt-port",
    "mqtt-user",
    "mqtt-pass",
    "mqtt-topic-tmpl",
    "mqtt-clientid",
    "ip-static",
    "ip-netmask",
    "ip-gateway",
    "ip-dns1",
    "ip-dns2",
    "update-auto",
    "usage-reporting",
)
_SECRET_DEVICE_KEYS = {
    "wifi-pass",
    "cloud-token",
    "app-pass",
    "mqtt-pass",
    CONF_PASSWORD,
}


def _display_value(value: Any) -> str:
    """Format device values for display in a settings summary."""
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "Online" if value else "Offline"
    if isinstance(value, (int, float)):
        if value > 10_000_000:
            return datetime.fromtimestamp(value, tz=UTC).strftime("%Y-%m-%d %H:%M:%SZ")
        return str(value)
    return str(value)


def _coerce_int(value: Any, default: int) -> int:
    """Coerce a device value to int with fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_bool(value: Any, default: bool = False) -> bool:
    """Coerce a device value to bool with fallback."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "on", "yes", "enabled"}:
            return True
        if normalized in {"0", "false", "off", "no", "disabled"}:
            return False
    if value is None:
        return default
    return bool(value)


def _secret_default(current_value: Any, fallback: str = "") -> str:
    """Return a safe default for secret fields."""
    if current_value in (None, "", "********", "none"):
        return fallback
    return str(current_value)


def _device_option_value(
    device_data: dict[str, Any], options: dict[str, Any], key: str, fallback: Any
) -> Any:
    """Prefer stored option values, then live device data, then fallback."""
    if key in options and options[key] not in (None, ""):
        return options[key]
    if key in device_data and device_data[key] not in (None, ""):
        return device_data[key]
    return fallback


class GeyserwalaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Geyserwala config flow."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> GeyserwalaOptionsFlow:
        """Return the options flow handler."""
        return GeyserwalaOptionsFlow()

    def __init__(self) -> None:
        """Init."""
        self._config: dict[str, Any] = {}
        self._errors: dict[str, str] = {}

    def _dependency_ready(self) -> bool:
        """Check whether runtime client dependency is available for validation calls."""
        global _DEPENDENCY_ERROR_LOGGED

        if _DEPENDENCY_AVAILABLE:
            return True

        if not _DEPENDENCY_ERROR_LOGGED:
            if isinstance(_DEPENDENCY_IMPORT_ERROR, ModuleNotFoundError):
                _LOGGER.error(
                    "[Geyserwala] Missing dependency 'thingwala-geyserwala' while loading config flow. "
                    "Home Assistant should install this automatically from manifest requirements. "
                    "Restart Home Assistant and check dependency installation logs. error=%s",
                    _DEPENDENCY_IMPORT_ERROR,
                )
            else:
                _LOGGER.error(
                    "[Geyserwala] Failed to load dependency 'thingwala-geyserwala' while loading config flow: %r",
                    _DEPENDENCY_IMPORT_ERROR,
                    exc_info=_DEPENDENCY_IMPORT_ERROR,
                )
            _DEPENDENCY_ERROR_LOGGED = True

        if isinstance(_DEPENDENCY_IMPORT_ERROR, ModuleNotFoundError):
            self._errors["base"] = "dependency_not_installed"
        else:
            self._errors["base"] = "dependency_load_failed"
        return False

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        properties = discovery_info.properties
        ip_address = discovery_info.host
        port = discovery_info.port
        if is_ipv6_address(ip_address):
            return self.async_abort(reason="ipv6_not_supported")
        uuid = properties["id"]
        await self.async_set_unique_id(uuid)
        self._abort_if_unique_id_configured(updates={CONF_IP_ADDRESS: ip_address, CONF_PORT: port})
        self._config.update(
            {
                CONF_HOST: ip_address,
                CONF_PORT: port,
                CONF_USERNAME: None,
                CONF_PASSWORD: None,
            }
        )
        return await self.async_step_user()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle user input."""
        if user_input is not None:
            self._async_abort_entries_match(
                {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                }
            )
            self._config.update(user_input)
            return await self.async_step_validate()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=self._config.get(CONF_HOST, "")): str,
                vol.Required(CONF_PORT, default=self._config.get(CONF_PORT, DEFAULT_PORT)): int,
                vol.Required(
                    CONF_USERNAME, default=self._config.get(CONF_USERNAME, None) or DEFAULT_USERNAME
                ): str,
                vol.Optional(CONF_PASSWORD, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=self._errors,
        )

    async def async_step_validate(self) -> ConfigFlowResult:
        """Handle device validation with detailed logging."""
        if not self._dependency_ready():
            return await self.async_step_user()

        session = async_create_clientsession(self.hass)
        host = self._config[CONF_HOST]
        port = self._config[CONF_PORT]
        username = self._config[CONF_USERNAME]
        _LOGGER.debug(
            "[Geyserwala] Starting validation for host=%s port=%s username=%s", host, port, username
        )
        api = GeyserwalaClientAsync(
            host=host,
            port=port,
            username=username,
            password=self._config[CONF_PASSWORD],
            session=session,
        )
        try:
            async with asyncio.timeout(20):
                connected = await api.update()
            if not connected:
                _LOGGER.error("[Geyserwala] Device unreachable at %s:%s", host, port)
                return self.async_abort(reason="unreachable")
        except Unauthorized as ex:
            _LOGGER.error("[Geyserwala] Unauthorized for %s:%s - %s", host, port, ex)
            self._errors["base"] = "invalid_auth"
            return await self.async_step_user()
        except GeyserwalaException as ex:
            _LOGGER.error("[Geyserwala] Cannot connect to %s:%s - %s", host, port, ex)
            self._errors["base"] = "cannot_connect"
            return await self.async_step_user()
        except TimeoutError:
            _LOGGER.error("[Geyserwala] Timeout while validating %s:%s", host, port)
            self._errors["base"] = "cannot_connect"
            return await self.async_step_user()
        except Exception:
            _LOGGER.exception(
                "[Geyserwala] Unexpected error during validation for %s:%s", host, port
            )
            self._errors["base"] = "cannot_connect"
            return await self.async_step_user()
        self._config["id"] = api.id
        self._config["name"] = api.name
        self._config["hostname"] = api.hostname

        _LOGGER.info("[Geyserwala] Successfully validated device at %s:%s", host, port)
        return self.async_create_entry(title=self._config["name"], data=self._config)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of device connection settings."""
        config_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if config_entry is None:
            return self.async_abort(reason="reconfigure_failed")

        if user_input is not None:
            if not self._dependency_ready():
                return await self.async_step_reconfigure()

            # Validate new connection settings
            session = async_create_clientsession(self.hass)
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            username = user_input[CONF_USERNAME]
            password = user_input.get(CONF_PASSWORD, config_entry.data.get(CONF_PASSWORD, ""))

            _LOGGER.debug(
                "[Geyserwala] Starting reconfiguration validation for host=%s port=%s username=%s",
                host,
                port,
                username,
            )

            api = GeyserwalaClientAsync(
                host=host,
                port=port,
                username=username,
                password=password,
                session=session,
            )

            try:
                async with asyncio.timeout(20):
                    connected = await api.update()
                if not connected:
                    _LOGGER.error("[Geyserwala] Device unreachable at %s:%s", host, port)
                    return self.async_abort(reason="unreachable")
            except Unauthorized as ex:
                _LOGGER.error("[Geyserwala] Unauthorized for %s:%s - %s", host, port, ex)
                self._errors["base"] = "invalid_auth"
                return await self.async_step_reconfigure()
            except GeyserwalaException as ex:
                _LOGGER.error("[Geyserwala] Cannot connect to %s:%s - %s", host, port, ex)
                self._errors["base"] = "cannot_connect"
                return await self.async_step_reconfigure()
            except TimeoutError:
                _LOGGER.error("[Geyserwala] Timeout while validating %s:%s", host, port)
                self._errors["base"] = "cannot_connect"
                return await self.async_step_reconfigure()
            except Exception:
                _LOGGER.exception(
                    "[Geyserwala] Unexpected error during reconfiguration validation for %s:%s",
                    host,
                    port,
                )
                self._errors["base"] = "cannot_connect"
                return await self.async_step_reconfigure()

            # Validation successful - update config entry
            new_data = {
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_USERNAME: username,
                CONF_PASSWORD: password,
                "id": api.id,
                "name": api.name,
                "hostname": api.hostname,
            }
            self.hass.config_entries.async_update_entry(config_entry, data=new_data)
            await self.hass.config_entries.async_reload(config_entry.entry_id)
            _LOGGER.info("[Geyserwala] Device reconfigured successfully at %s:%s", host, port)
            return self.async_abort(reason="reconfigure_successful")

        # Load current configuration
        current_host = config_entry.data.get(CONF_HOST, "")
        current_port = config_entry.data.get(CONF_PORT, DEFAULT_PORT)
        current_username = config_entry.data.get(CONF_USERNAME, DEFAULT_USERNAME)
        current_password = config_entry.data.get(CONF_PASSWORD, "")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current_host): str,
                vol.Required(CONF_PORT, default=current_port): int,
                vol.Required(CONF_USERNAME, default=current_username): str,
                vol.Optional(CONF_PASSWORD, default=current_password): str,
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=data_schema,
            errors=self._errors,
            description_placeholders={
                "device_name": config_entry.data.get("name", "Geyserwala"),
            },
        )


class GeyserwalaOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Geyserwala integration."""

    async def _async_validate_connection(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
    ) -> str | None:
        """Validate connection settings from options flow."""
        if not _DEPENDENCY_AVAILABLE:
            if isinstance(_DEPENDENCY_IMPORT_ERROR, ModuleNotFoundError):
                return "dependency_not_installed"
            return "dependency_load_failed"

        session = async_create_clientsession(self.hass)
        api = GeyserwalaClientAsync(
            host=host,
            port=port,
            username=username,
            password=password,
            session=session,
        )
        try:
            async with asyncio.timeout(20):
                connected = await api.update()
            if not connected:
                return "cannot_connect"
        except Unauthorized:
            return "invalid_auth"
        except (GeyserwalaException, TimeoutError):
            return "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception(
                "[Geyserwala] Unexpected error while validating connection changes in options flow"
            )
            return "cannot_connect"
        return None

    async def _async_fetch_device_snapshot(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
    ) -> dict[str, Any]:
        """Fetch the current device state and settings for the settings screen."""
        if not _DEPENDENCY_AVAILABLE:
            return {}

        session = async_create_clientsession(self.hass)
        api = GeyserwalaClientAsync(
            host=host,
            port=port,
            username=username,
            password=password,
            session=session,
        )

        for key in _DEVICE_STATUS_KEYS + _DEVICE_SETTING_KEYS:
            api.subscribe(key)

        snapshot: dict[str, Any] = {}
        try:
            async with asyncio.timeout(20):
                await api.update()
            for key in _DEVICE_STATUS_KEYS + _DEVICE_SETTING_KEYS:
                snapshot[key] = api.get_value(key)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("[Geyserwala] Failed to fetch live device settings snapshot")
        finally:
            await api.close()
        return snapshot

    def _async_device_placeholders(self, snapshot: dict[str, Any]) -> dict[str, str]:
        """Build display placeholders for live device status values."""
        return {
            "device_status": _display_value(snapshot.get("status")),
            "device_version": _display_value(snapshot.get("version")),
            "wifi_status": _display_value(snapshot.get("wifi-status")),
            "cloud_status": _display_value(snapshot.get("cloud-status")),
            "mqtt_status": _display_value(snapshot.get("mqtt-up")),
            "device_time": _display_value(snapshot.get("unixtime")),
        }

    def _build_device_schema(
        self,
        snapshot: dict[str, Any],
        options: dict[str, Any],
    ) -> vol.Schema:
        """Build the full device settings schema."""
        return vol.Schema(
            {
                vol.Optional(
                    "wifi-ssid", default=_device_option_value(snapshot, options, "wifi-ssid", "")
                ): str,
                vol.Optional(
                    "wifi-pass",
                    default=_secret_default(
                        options.get("wifi-pass"), snapshot.get("wifi-pass", "")
                    ),
                ): str,
                vol.Optional(
                    "cloud-token",
                    default=_secret_default(
                        options.get("cloud-token"), snapshot.get("cloud-token", "")
                    ),
                ): str,
                vol.Optional(
                    "name",
                    default=_device_option_value(
                        snapshot,
                        options,
                        "name",
                        self.config_entry.data.get(CONF_HOST, "Geyserwala"),
                    ),
                ): str,
                vol.Optional(
                    "hostname",
                    default=_device_option_value(
                        snapshot, options, "hostname", self.config_entry.data.get(CONF_HOST, "")
                    ),
                ): str,
                vol.Optional(
                    "setpoint-max",
                    default=_coerce_int(
                        _device_option_value(snapshot, options, "setpoint-max", 55), 55
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=80)),
                vol.Optional(
                    "gw-diff",
                    default=_coerce_int(_device_option_value(snapshot, options, "gw-diff", 7), 7),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=30)),
                vol.Optional(
                    "gw-antifreeze",
                    default=_coerce_int(
                        _device_option_value(snapshot, options, "gw-antifreeze", 10), 10
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=30)),
                vol.Optional(
                    "dc-max-temp",
                    default=_coerce_int(
                        _device_option_value(snapshot, options, "dc-max-temp", 60), 60
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=90)),
                vol.Optional(
                    "gw-ldr-min",
                    default=_coerce_int(
                        _device_option_value(snapshot, options, "gw-ldr-min", 0), 0
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=1000)),
                vol.Optional(
                    "app-enable",
                    default=_coerce_bool(
                        _device_option_value(snapshot, options, "app-enable", False)
                    ),
                ): bool,
                vol.Optional(
                    "app-pass",
                    default=_secret_default(options.get("app-pass"), snapshot.get("app-pass", "")),
                ): str,
                vol.Optional(
                    "utc-offset",
                    default=_coerce_int(
                        _device_option_value(snapshot, options, "utc-offset", 0), 0
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=-720, max=840)),
                vol.Optional(
                    "ntp-host",
                    default=_device_option_value(snapshot, options, "ntp-host", "pool.ntp.org"),
                ): str,
                vol.Optional(
                    "ntp-port",
                    default=_coerce_int(
                        _device_option_value(snapshot, options, "ntp-port", 123), 123
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
                vol.Optional(
                    "mqtt-enable",
                    default=_coerce_bool(
                        _device_option_value(snapshot, options, "mqtt-enable", False)
                    ),
                ): bool,
                vol.Optional(
                    "mqtt-host", default=_device_option_value(snapshot, options, "mqtt-host", "")
                ): str,
                vol.Optional(
                    "mqtt-port",
                    default=_coerce_int(
                        _device_option_value(snapshot, options, "mqtt-port", 1883), 1883
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
                vol.Optional(
                    "mqtt-user", default=_device_option_value(snapshot, options, "mqtt-user", "")
                ): str,
                vol.Optional(
                    "mqtt-pass",
                    default=_secret_default(
                        options.get("mqtt-pass"), snapshot.get("mqtt-pass", "")
                    ),
                ): str,
                vol.Optional(
                    "mqtt-topic-tmpl",
                    default=_device_option_value(
                        snapshot, options, "mqtt-topic-tmpl", "geyserwala/%prefix%/%mac%"
                    ),
                ): str,
                vol.Optional(
                    "mqtt-clientid",
                    default=_device_option_value(
                        snapshot, options, "mqtt-clientid", "geyserwala-%mac%"
                    ),
                ): str,
                vol.Optional(
                    "ip-static", default=_device_option_value(snapshot, options, "ip-static", "")
                ): str,
                vol.Optional(
                    "ip-netmask", default=_device_option_value(snapshot, options, "ip-netmask", "")
                ): str,
                vol.Optional(
                    "ip-gateway", default=_device_option_value(snapshot, options, "ip-gateway", "")
                ): str,
                vol.Optional(
                    "ip-dns1", default=_device_option_value(snapshot, options, "ip-dns1", "")
                ): str,
                vol.Optional(
                    "ip-dns2", default=_device_option_value(snapshot, options, "ip-dns2", "")
                ): str,
                vol.Optional(
                    "update-auto",
                    default=_coerce_bool(
                        _device_option_value(snapshot, options, "update-auto", False)
                    ),
                ): bool,
                vol.Optional(
                    "usage-reporting",
                    default=_coerce_bool(
                        _device_option_value(snapshot, options, "usage-reporting", False)
                    ),
                ): bool,
                vol.Optional("transport", default=options.get("transport", "http")): vol.In(
                    ["http", "mqtt"]
                ),
                vol.Optional(
                    "mqtt_base_topic", default=options.get("mqtt_base_topic", "geyserwala")
                ): str,
                vol.Optional(
                    "calibrations_json", default=options.get("calibrations_json", "")
                ): str,
                vol.Optional("alert_rules_json", default=options.get("alert_rules_json", "")): str,
            }
        )

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage integration options - polling and feature selection."""
        current_data = self.config_entry.data
        current_options = self.config_entry.options

        current_host = current_data.get(CONF_HOST, "")
        current_port = current_data.get(CONF_PORT, DEFAULT_PORT)
        current_username = current_data.get(CONF_USERNAME, DEFAULT_USERNAME)
        current_password = current_data.get(CONF_PASSWORD, "")

        default_interval = current_options.get("update_interval", DEFAULT_UPDATE_INTERVAL_SECONDS)
        enable_mqtt = current_options.get("enable_mqtt", False)
        enable_calibration = current_options.get("enable_calibration", False)
        enable_alerts = current_options.get("enable_alerts", False)
        enable_services = current_options.get(
            "enable_services", True
        )  # Services enabled by default

        schema = vol.Schema(
            {
                # Device Connection Configuration
                vol.Required(CONF_HOST, default=current_host): str,
                vol.Required(CONF_PORT, default=current_port): int,
                vol.Required(CONF_USERNAME, default=current_username): str,
                vol.Optional(CONF_PASSWORD, default=current_password): str,
                # Polling Configuration
                vol.Required("update_interval", default=default_interval): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_UPDATE_INTERVAL_SECONDS, max=600),
                ),
                # Feature Toggles
                vol.Required("enable_services", default=enable_services): bool,
                vol.Required("enable_mqtt", default=enable_mqtt): bool,
                vol.Required("enable_calibration", default=enable_calibration): bool,
                vol.Required("enable_alerts", default=enable_alerts): bool,
            }
        )

        if user_input is not None:
            updated_host = user_input[CONF_HOST]
            updated_port = user_input[CONF_PORT]
            updated_username = user_input[CONF_USERNAME]
            updated_password = user_input.get(CONF_PASSWORD, current_password)

            connection_changed = any(
                (
                    updated_host != current_host,
                    updated_port != current_port,
                    updated_username != current_username,
                    updated_password != current_password,
                )
            )

            if connection_changed:
                validation_error = await self._async_validate_connection(
                    host=updated_host,
                    port=updated_port,
                    username=updated_username,
                    password=updated_password,
                )
                if validation_error:
                    return self.async_show_form(
                        step_id="init",
                        data_schema=schema,
                        errors={"base": validation_error},
                        description_placeholders={
                            "services_info": "Set boost, mode, read/clear error codes",
                            "mqtt_info": "Use MQTT transport instead of HTTP",
                            "calibration_info": "Per-entity offset and multiplier adjustments",
                            "alerts_info": "Threshold and state-change notifications",
                        },
                    )

            updated_data = dict(current_data)
            updated_data[CONF_HOST] = updated_host
            updated_data[CONF_PORT] = updated_port
            updated_data[CONF_USERNAME] = updated_username
            updated_data[CONF_PASSWORD] = updated_password

            if updated_data != dict(current_data):
                self.hass.config_entries.async_update_entry(self.config_entry, data=updated_data)

            final_options = dict(current_options)
            final_options.update(
                {
                    "update_interval": user_input["update_interval"],
                    "enable_services": user_input["enable_services"],
                    "enable_mqtt": user_input["enable_mqtt"],
                    "enable_calibration": user_input["enable_calibration"],
                    "enable_alerts": user_input["enable_alerts"],
                }
            )

            return self.async_create_entry(title="", data=final_options)

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={
                "services_info": "Set boost, mode, read/clear error codes",
                "mqtt_info": "Use MQTT transport instead of HTTP",
                "calibration_info": "Per-entity offset and multiplier adjustments",
                "alerts_info": "Threshold and state-change notifications",
            },
        )

    async def async_step_device(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Configure the mirrored device settings from the controller web UI."""
        base_state = self.hass.data.get("_geyserwala_config_flow_state", {}).get(
            self.config_entry.entry_id, {}
        )
        snapshot = base_state.get("_device_snapshot", {})
        schema = self._build_device_schema(snapshot=snapshot, options=self.config_entry.options)

        if user_input is not None:
            errors: dict[str, str] = {}

            calibrations_json = user_input.get("calibrations_json", "").strip()
            if calibrations_json:
                try:
                    parsed_calibrations = json.loads(calibrations_json)
                    if not isinstance(parsed_calibrations, dict):
                        errors["calibrations_json"] = "invalid_calibrations_json"
                except json.JSONDecodeError:
                    errors["calibrations_json"] = "invalid_calibrations_json"

            alert_rules_json = user_input.get("alert_rules_json", "").strip()
            if alert_rules_json:
                try:
                    parsed_alert_rules = json.loads(alert_rules_json)
                    if not isinstance(parsed_alert_rules, list):
                        errors["alert_rules_json"] = "invalid_alert_rules_json"
                except json.JSONDecodeError:
                    errors["alert_rules_json"] = "invalid_alert_rules_json"

            if errors:
                return self.async_show_form(
                    step_id="device",
                    data_schema=schema,
                    errors=errors,
                    description_placeholders={
                        **self._async_device_placeholders(snapshot),
                        "settings_help": "Edit the local device configuration mirrored from the Geyserwala Settings screen.",
                    },
                )

            final_options = dict(self.config_entry.options)

            for key, value in user_input.items():
                if key in _CONNECTION_KEYS:
                    continue
                if key in _SECRET_DEVICE_KEYS and value == "" and key in final_options:
                    continue
                final_options[key] = value

            self.hass.data.get("_geyserwala_config_flow_state", {}).pop(
                self.config_entry.entry_id, None
            )

            updated_data = dict(self.config_entry.data)
            for key in _CONNECTION_KEYS:
                if key in base_state and base_state[key] not in (None, ""):
                    updated_data[key] = base_state[key]

            if updated_data != dict(self.config_entry.data):
                self.hass.config_entries.async_update_entry(self.config_entry, data=updated_data)

            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=final_options)

        return self.async_show_form(
            step_id="device",
            data_schema=schema,
            description_placeholders={
                **self._async_device_placeholders(snapshot),
                "settings_help": "Edit the local device configuration mirrored from the Geyserwala Settings screen.",
            },
        )
