####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala number platform."""

from dataclasses import dataclass

import voluptuous as vol
from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import GeyserwalaEntity
from .platform_setup import async_setup_platform_entry

NUMBER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("key"): cv.string,
        vol.Optional("device_class", default=None): vol.Any(None, cv.string),
        vol.Optional("icon", default="mdi:numeric"): cv.string,
        vol.Optional("visible", default=False): cv.boolean,
        vol.Optional("entity_category", default=None): vol.Any(None, cv.string),
        vol.Optional("min", default=0): vol.Coerce(int),
        vol.Optional("max", default=4294967296): vol.Coerce(int),
        vol.Optional("unit", default=None): vol.Any(None, cv.string),
    }
)


@dataclass
class Number:
    """Entity params."""

    name: str
    key: str
    device_class: str
    icon: str
    visible: bool
    min: int
    max: int
    unit: str
    entity_category: str | None = None


def _map_entity_category(value: str | None) -> EntityCategory | None:
    """Map optional entity category string to Home Assistant enum."""
    if value == "config":
        return EntityCategory.CONFIG
    if value == "diagnostic":
        return EntityCategory.DIAGNOSTIC
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geyserwala number entities using generic helper."""
    await async_setup_platform_entry(
        hass=hass,
        config_entry=config_entry,
        async_add_entities=async_add_entities,
        entity_domain="number",
        dc_class=Number,
        entity_class=GeyserwalaNumber,
        description_factory=lambda item: NumberEntityDescription(
            key=item.key,
            has_entity_name=True,
            name=item.name,
            entity_category=_map_entity_category(item.entity_category),
            device_class=item.device_class,
            native_min_value=item.min,
            native_max_value=item.max,
            native_step=1,
            native_unit_of_measurement=item.unit,
            icon=item.icon,
            entity_registry_visible_default=item.visible,
            entity_registry_enabled_default=True,
        ),
    )


class GeyserwalaNumber(GeyserwalaEntity, NumberEntity):
    """Geyserwala number entity."""

    @property
    def native_value(self) -> int:
        """Value."""
        return self.coordinator.data.get_value(self._gw_key)

    async def async_set_native_value(self, value: float) -> None:
        """Set value."""
        await self.coordinator.data.set_value(self._gw_key, value)
