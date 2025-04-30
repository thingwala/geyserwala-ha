####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala entity."""

import dataclasses

from homeassistant.helpers.entity import (
    DeviceInfo,
    EntityDescription,
    generate_entity_id,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from thingwala.geyserwala.aio.client import GeyserwalaClientAsync

from .const import DOMAIN


class GeyserwalaEntity(CoordinatorEntity[DataUpdateCoordinator[GeyserwalaClientAsync]]):
    """Geyserwala base entity."""

    def __init__(
        self,
        hass, entity_domain,
        coordinator: DataUpdateCoordinator[GeyserwalaClientAsync],
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
        coordinator.data.subscribe(gw_key)


def gen_entity_dataclasses(entities, entity_type, dc_class):
    if entities and entity_type in entities:
        for data_dict in entities[entity_type]:
            field_names = {f.name for f in dataclasses.fields(dc_class)}
            filtered_data = {k: v for k, v in data_dict.items() if k in field_names}
            yield dc_class(**filtered_data)
