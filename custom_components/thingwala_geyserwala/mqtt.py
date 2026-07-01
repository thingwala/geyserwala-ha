####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""MQTT transport support for Geyserwala integration."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant, callback

from .const import _LOGGER

try:
    from homeassistant.components import mqtt
except ImportError:
    mqtt = None  # pragma: no cover


class GeyserwalaClientMQTT:
    """MQTT-based client for Geyserwala integration."""

    def __init__(
        self,
        hass: HomeAssistant,
        device_id: str,
        base_topic: str = "geyserwala",
    ) -> None:
        """Initialize MQTT client."""
        self.hass = hass
        self.device_id = device_id
        self.base_topic = base_topic
        self.device_topic = f"{base_topic}/{device_id}"

        # Device info properties
        self.id = device_id
        self.name = f"Geyserwala {device_id}"
        self.hostname = device_id
        self._data: dict[str, Any] = {}
        self._subscriptions: list[Callable[[], None]] = []

    async def async_connect(self) -> bool:
        """Connect to MQTT and subscribe to device topics."""
        if not mqtt:
            _LOGGER.warning(
                "[Geyserwala] MQTT component not available for device %s",
                self.device_id,
            )
            return False

        try:
            # Subscribe to device state topic using the MQTT helper
            remove_subscriber = await mqtt.async_subscribe(
                self.hass,
                f"{self.device_topic}/state",
                self._handle_state_update,
                qos=1,
            )
            self._subscriptions.append(remove_subscriber)
            _LOGGER.info(
                "[Geyserwala] MQTT client connected for device %s on topic %s",
                self.device_id,
                self.device_topic,
            )
            return True
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error(
                "[Geyserwala] Failed to connect MQTT client for device %s: %s",
                self.device_id,
                err,
            )
            return False

    async def async_disconnect(self) -> None:
        """Disconnect from MQTT."""
        for unsubscribe in self._subscriptions:
            unsubscribe()
        self._subscriptions.clear()
        _LOGGER.info("[Geyserwala] MQTT client disconnected for device %s", self.device_id)

    @callback
    def _handle_state_update(self, msg: Any) -> None:
        """Handle MQTT state update message."""
        try:
            payload = msg.payload
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")

            if isinstance(payload, str):
                self._data = json.loads(payload)
            else:
                self._data = payload

            _LOGGER.debug(
                "[Geyserwala] MQTT state update received for %s",
                self.device_id,
            )
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("[Geyserwala] Error parsing MQTT state update: %s", err)

    async def update(self) -> Any:
        """Fetch latest state (for MQTT, this is cached from subscriptions)."""
        if not mqtt:
            _LOGGER.warning("[Geyserwala] MQTT component not available")
            return self
        # For MQTT, we rely on subscribed messages; this is mostly a compatibility method
        if not self._data:
            # Try to request a state publish
            await mqtt.async_publish(
                self.hass,
                f"{self.device_topic}/command",
                json.dumps({"action": "get_state"}),
                qos=1,
                retain=False,
            )
        return self

    async def set_boost(self, enabled: bool, duration_minutes: int = 0) -> bool:
        """Send boost command via MQTT."""
        if not mqtt:
            _LOGGER.warning("[Geyserwala] MQTT component not available")
            return False
        try:
            payload = {
                "action": "set_boost",
                "enabled": enabled,
                "duration_minutes": duration_minutes,
            }
            await mqtt.async_publish(
                self.hass,
                f"{self.device_topic}/command",
                json.dumps(payload),
                qos=1,
                retain=False,
            )
            _LOGGER.debug("[Geyserwala] Sent set_boost command via MQTT: %s", payload)
            return True
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("[Geyserwala] Error sending set_boost via MQTT: %s", err)
            return False

    async def set_mode(self, mode: str) -> bool:
        """Send mode change command via MQTT."""
        if not mqtt:
            _LOGGER.warning("[Geyserwala] MQTT component not available")
            return False
        try:
            payload = {"action": "set_mode", "mode": mode}
            await mqtt.async_publish(
                self.hass,
                f"{self.device_topic}/command",
                json.dumps(payload),
                qos=1,
                retain=False,
            )
            _LOGGER.debug("[Geyserwala] Sent set_mode command via MQTT: %s", payload)
            return True
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("[Geyserwala] Error sending set_mode via MQTT: %s", err)
            return False

    async def read_error_codes(self) -> list[str]:
        """Request error codes via MQTT."""
        if not mqtt:
            _LOGGER.warning("[Geyserwala] MQTT component not available")
            return []
        try:
            payload = {"action": "read_error_codes"}
            await mqtt.async_publish(
                self.hass,
                f"{self.device_topic}/command",
                json.dumps(payload),
                qos=1,
                retain=False,
            )
            _LOGGER.debug("[Geyserwala] Sent read_error_codes command via MQTT")
            # Return cached error codes from last state update
            return self._data.get("error_codes", [])
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("[Geyserwala] Error reading error codes via MQTT: %s", err)
            return []

    async def clear_error_codes(self) -> bool:
        """Send clear error codes command via MQTT."""
        if not mqtt:
            _LOGGER.warning("[Geyserwala] MQTT component not available")
            return False
        try:
            payload = {"action": "clear_error_codes"}
            await mqtt.async_publish(
                self.hass,
                f"{self.device_topic}/command",
                json.dumps(payload),
                qos=1,
                retain=False,
            )
            _LOGGER.debug("[Geyserwala] Sent clear_error_codes command via MQTT")
            return True
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("[Geyserwala] Error clearing error codes via MQTT: %s", err)
            return False

    def __getattr__(self, name: str) -> Any:
        """Fallback for accessing device data attributes."""
        return self._data.get(name)
