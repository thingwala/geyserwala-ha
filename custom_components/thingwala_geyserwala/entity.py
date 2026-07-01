####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala entity."""

import dataclasses
import importlib
from collections.abc import Iterator, Mapping
from typing import Any

from homeassistant.helpers.entity import (
    DeviceInfo,
    EntityDescription,
    generate_entity_id,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

try:
    GeyserwalaClientAsync = importlib.import_module(
        "thingwala.geyserwala.aio.client"
    ).GeyserwalaClientAsync
except ModuleNotFoundError:  # pragma: no cover - lets local tests import the module.
    GeyserwalaClientAsync = Any  # type: ignore[assignment]

from .const import DOMAIN


class GeyserwalaEntity(CoordinatorEntity[Any]):
    """Geyserwala base entity."""

    def __init__(
        self,
        hass,
        entity_domain,
        coordinator: DataUpdateCoordinator[Any],
        description: EntityDescription,
        gw_key: str,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self.entity_description = description
        self._gw_key = gw_key
        self._attr_unique_id = f"{DOMAIN}.{self.coordinator.data.id}.{gw_key.replace('-', '_')}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.data.id)},
            manufacturer="Thingwala",
            model="Geyserwala",
            name=self.coordinator.data.name,
            sw_version=self.coordinator.data.version,
        )
        slug = self.coordinator.data.hostname.replace("-", "_").replace(".", "_").lower()
        self.entity_id = generate_entity_id(
            f"{entity_domain}.{{}}",
            f"{slug}_{self._gw_key}",
            hass=hass,
        )
        # Virtual entities are local-only and do not map to device keys.
        if not gw_key.startswith("__"):
            coordinator.data.subscribe(gw_key)

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from updates when removed if the API supports it."""
        await super().async_will_remove_from_hass()
        unsubscribe = getattr(self.coordinator.data, "unsubscribe", None)
        if callable(unsubscribe):
            unsubscribe(self._gw_key)


def gen_entity_dataclasses(
    entities: Mapping[str, list[dict[str, Any]]] | None,
    entity_type: str,
    dc_class: type | None,
) -> Iterator[Any]:
    """Yield dataclass instances for a given entity type from config payload."""
    if not entities or entity_type not in entities or dc_class is None:
        return

    field_names = {f.name for f in dataclasses.fields(dc_class)}
    for data_dict in entities[entity_type]:
        filtered_data = {k: v for k, v in data_dict.items() if k in field_names}
        yield dc_class(**filtered_data)
