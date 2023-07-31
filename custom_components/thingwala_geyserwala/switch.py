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
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import GeyserwalaEntity


@dataclass
class Switch:
    """Entity params."""

    name: str
    id: str
    entity_category: str
    icon_on: str
    icon_off: str
    visible: bool


SWITCHES = [
    Switch("Boost", "boost_demand", None, "mdi:fire", "mdi:fire-off", True),
    Switch("External Demand", "external_demand", None, "mdi:fire", "mdi:fire-off", False),
    Switch("Low Power Enable", "lowpower_enable", None, "mdi:fire", "mdi:fire-off", False),
]

SWITCH_MAP = {s.id: s for s in SWITCHES}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala switch entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaSwitch(
            coordinator,
            SwitchEntityDescription(
                key=item.id,
                has_entity_name=True,
                name=item.name,
                entity_category=item.entity_category,
                device_class=SwitchDeviceClass.SWITCH,
                entity_registry_visible_default=item.visible,
                entity_registry_enabled_default=True,
            ),
            item.id,
        )
        for item in SWITCHES
    )


class GeyserwalaSwitch(GeyserwalaEntity, SwitchEntity):
    """Geyserwala switch entity."""

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn on."""
        await getattr(self.coordinator.data, f"set_{self._gw_id}")(True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn off."""
        await getattr(self.coordinator.data, f"set_{self._gw_id}")(False)

    @property
    def is_on(self) -> bool:
        """State."""
        return getattr(self.coordinator.data, self._gw_id)

    @property
    def icon(self) -> str:
        """Icon."""
        if self.is_on:
            return SWITCH_MAP[self._gw_id].icon_on
        return SWITCH_MAP[self._gw_id].icon_off
