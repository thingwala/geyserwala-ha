####################################################################################
# Copyright (c) 2023 ThingWala                                                     #
####################################################################################
"""Geyserwala select platform."""
from dataclasses import dataclass
from typing import Dict, List

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from thingwala.geyserwala.const import (
    GEYSERWALA_MODES,
    GEYSERWALA_MODE_SETPOINT,
    GEYSERWALA_MODE_TIMER,
    GEYSERWALA_MODE_SOLAR,
    GEYSERWALA_MODE_HOLIDAY,
)

from .const import DOMAIN
from .entity import GeyserwalaEntity


@dataclass
class Select:
    """Entity params."""

    name: str
    id: str
    entity_category: str
    icon_map: Dict[str, str]
    options: List[str]
    visible: bool


SELECTS = [
    Select("Mode", "mode", None,
           {
               GEYSERWALA_MODE_SETPOINT: "mdi:thermostat-auto",
               GEYSERWALA_MODE_TIMER: "mdi:timer",
               GEYSERWALA_MODE_SOLAR: "mdi:solar-power-variant",
               GEYSERWALA_MODE_HOLIDAY: "mdi:airplane",
           },
           GEYSERWALA_MODES, True),
]

SELECT_MAP = {s.id: s for s in SELECTS}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala select entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        GeyserwalaSelect(
            coordinator,
            SelectEntityDescription(
                key=item.id,
                has_entity_name=True,
                name=item.name,
                entity_category=item.entity_category,
                device_class=None,
                options=item.options,
                unit_of_measurement=None,
                entity_registry_visible_default=item.visible,
                entity_registry_enabled_default=True,
            ),
            item.id,
        )
        for item in SELECTS
    )


class GeyserwalaSelect(GeyserwalaEntity, SelectEntity):
    """Geyserwala select entity."""

    @property
    def current_option(self) -> str:
        """Option."""
        return getattr(self.coordinator.data, self._gw_id)

    async def async_select_option(self, option: str) -> None:
        """Set option."""
        await getattr(self.coordinator.data, f"set_{self._gw_id}")(option)

    @property
    def icon(self) -> str:
        """Icon."""
        return SELECT_MAP[self._gw_id].icon_map[self.current_option]
