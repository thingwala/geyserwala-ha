####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala entities."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
)

from homeassistant.components.number import (
    NumberDeviceClass,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
)

from homeassistant.const import (
    UnitOfTemperature,
)

from thingwala.geyserwala.const import (
    GEYSERWALA_SETPOINT_TEMP_MIN,
    GEYSERWALA_SETPOINT_TEMP_MAX,
)

ENTITIES = {
    "binary_sensor": [
        {
            "name": "Pump",
            "key": "pump-status",
            "device_class": BinarySensorDeviceClass.RUNNING,
            "icon_on": "mdi:water-pump",
            "icon_off": "mdi:water-pump-off",
            "visible": False,
        },
        {
            "name": "Element",
            "key": "element-demand",
            "device_class": BinarySensorDeviceClass.POWER,
            "icon_on": "mdi:radiator",
            "icon_off": "mdi:radiator-off",
            "visible": True,
        },
    ],
    "number": [
        {
            "name": "Setpoint",
            "key": "setpoint",
            "device_class": NumberDeviceClass.TEMPERATURE,
            "icon": "mdi:thermostat",
            "visible": True,
            "min": GEYSERWALA_SETPOINT_TEMP_MIN,
            "max": GEYSERWALA_SETPOINT_TEMP_MAX,
            "unit": UnitOfTemperature.CELSIUS,
        },
        {
            "name": "External Setpoint",
            "key": "external-setpoint",
            "device_class": NumberDeviceClass.TEMPERATURE,
            "icon": "mdi:thermostat-auto",
            "visible": True,
            "min": GEYSERWALA_SETPOINT_TEMP_MIN,
            "max": GEYSERWALA_SETPOINT_TEMP_MAX,
            "unit": UnitOfTemperature.CELSIUS,
        },
    ],
    "sensor": [
        {
            "name": "Water Temperature",
            "key": "tank-temp",
            "device_class": SensorDeviceClass.TEMPERATURE,
            "icon": "mdi:thermometer-water",
            "visible": True,
            "unit": UnitOfTemperature.CELSIUS,
        },
        {
            "name": "Collector Temperature",
            "key": "collector-temp",
            "device_class": SensorDeviceClass.TEMPERATURE,
            "icon": "mdi:sun-thermometer",
            "visible": False,
            "unit": UnitOfTemperature.CELSIUS,
        },
    ],
    "switch": [
        {
            "name": "Boost",
            "key": "boost-demand",
            "icon_on": "mdi:fire",
            "icon_off": "mdi:fire-off",
            "visible": True,
        },
        {
            "name": "External Demand",
            "key": "external-demand",
            "icon_on": "mdi:fire",
            "icon_off": "mdi:fire-off",
            "visible": True,
        },
        {
            "name": "External Disable",
            "key": "external-disable",
            "icon_on": "mdi:water-boiler-off",
            "icon_off": "mdi:water-boiler",
            "visible": True,
        },
    ],
    'text': [
        {
            'name': "Status",
            'key': "status",
            'icon': "mdi:information-outline",
            'visible': True,
        }
    ],
}
