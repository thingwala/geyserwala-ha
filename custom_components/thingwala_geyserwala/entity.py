####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala entity."""
from homeassistant.helpers.entity import (
    DeviceInfo,
    EntityDescription
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
        coordinator: DataUpdateCoordinator[GeyserwalaClientAsync],
        description: EntityDescription,
        gw_id: str,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self.entity_description = description
        self._gw_id = gw_id
        self._attr_unique_id = f"{DOMAIN}.{self.coordinator.data.id}.{gw_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.data.id)},
            manufacturer="Thingwala",
            model="Geyserwala",
            name=self.coordinator.data.name,
            sw_version=self.coordinator.data.version,
        )
