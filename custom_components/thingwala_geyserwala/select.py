####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala select platform."""

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from thingwala.geyserwala.const import (
    GEYSERWALA_MODE_SETPOINT,
    GEYSERWALA_MODE_TIMER,
    GEYSERWALA_MODE_SOLAR,
    GEYSERWALA_MODE_HOLIDAY,
    GEYSERWALA_MODE_STANDBY,
)

from .const import DOMAIN
from .entity import GeyserwalaEntity


ICON_MAP = {
    "mode": {
        GEYSERWALA_MODE_SETPOINT: "mdi:thermostat-box",
        GEYSERWALA_MODE_TIMER: "mdi:timer",
        GEYSERWALA_MODE_HOLIDAY: "mdi:airplane",
        GEYSERWALA_MODE_STANDBY: "mdi:power-standby",
        GEYSERWALA_MODE_SOLAR: "mdi:solar-power-variant",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala select entities."""
    entity_domain = 'select'

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [GeyserwalaSelect(
            hass, entity_domain,
            coordinator,
            SelectEntityDescription(
                key="mode",
                has_entity_name=True,
                name="Mode",
                entity_category=None,
                device_class=None,
                options=coordinator.data.modes,
                unit_of_measurement=None,
                entity_registry_visible_default=True,
                entity_registry_enabled_default=True,
            ),
            "mode",
        )]
    )


class GeyserwalaSelect(GeyserwalaEntity, SelectEntity):
    """Geyserwala select entity."""

    @property
    def current_option(self) -> str:
        """Option."""
        return self.coordinator.data.get_value(self._gw_key)

    async def async_select_option(self, option: str) -> None:
        """Set option."""
        await self.coordinator.data.set_value(self._gw_key, option)

    @property
    def icon(self) -> str:
        """Icon."""
        return ICON_MAP[self._gw_key][self.current_option]
