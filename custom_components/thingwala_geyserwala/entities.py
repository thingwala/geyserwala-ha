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

try:
    from thingwala.geyserwala.const import (
        GEYSERWALA_SETPOINT_TEMP_MAX,
        GEYSERWALA_SETPOINT_TEMP_MIN,
    )
except ModuleNotFoundError:  # pragma: no cover - lets local tests import the module.
    GEYSERWALA_SETPOINT_TEMP_MIN = 30
    GEYSERWALA_SETPOINT_TEMP_MAX = 80

# Invisible sort prefixes keep config items grouped in the Home Assistant UI
# without adding visible numbering or text prefixes to entity names.
_S_CFG = "\u200b"
_S_WIFI = "\u200b\u200b"
_S_CLOUD = "\u200b\u200b\u200b"
_S_DEVICE = "\u200b\u200b\u200b\u200b"
_S_THRESH = "\u200b\u200b\u200b\u200b\u200b"
_S_APP = "\u200b\u200b\u200b\u200b\u200b\u200b"
_S_TIME = "\u200b\u200b\u200b\u200b\u200b\u200b\u200b"
_S_MQTT = "\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b"
_S_NET = "\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b"
_S_REPORTQ = "\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b"

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
        {
            "name": f"{_S_THRESH}Thresholds: Setpoint Max",
            "key": "setpoint-max",
            "device_class": NumberDeviceClass.TEMPERATURE,
            "icon": "mdi:thermostat-high",
            "visible": True,
            "entity_category": "config",
            "min": 30,
            "max": 80,
            "unit": UnitOfTemperature.CELSIUS,
        },
        {
            "name": f"{_S_THRESH}\u200bThresholds: Differential",
            "key": "gw-diff",
            "device_class": None,
            "icon": "mdi:delta",
            "visible": True,
            "entity_category": "config",
            "min": 1,
            "max": 30,
            "unit": None,
        },
        {
            "name": f"{_S_THRESH}\u200b\u200bThresholds: Antifreeze",
            "key": "gw-antifreeze",
            "device_class": NumberDeviceClass.TEMPERATURE,
            "icon": "mdi:snowflake-thermometer",
            "visible": True,
            "entity_category": "config",
            "min": 0,
            "max": 30,
            "unit": UnitOfTemperature.CELSIUS,
        },
        {
            "name": f"{_S_THRESH}\u200b\u200b\u200bThresholds: DC Max Temp",
            "key": "dc-max-temp",
            "device_class": NumberDeviceClass.TEMPERATURE,
            "icon": "mdi:thermometer-alert",
            "visible": True,
            "entity_category": "config",
            "min": 30,
            "max": 90,
            "unit": UnitOfTemperature.CELSIUS,
        },
        {
            "name": f"{_S_THRESH}\u200b\u200b\u200b\u200bThresholds: LDR Min",
            "key": "gw-ldr-min",
            "device_class": None,
            "icon": "mdi:brightness-5",
            "visible": True,
            "entity_category": "config",
            "min": 0,
            "max": 1000,
            "unit": None,
        },
        {
            "name": f"{_S_TIME}Time: UTC Offset (min)",
            "key": "utc-offset",
            "device_class": None,
            "icon": "mdi:clock-time-eight-outline",
            "visible": True,
            "entity_category": "config",
            "min": -720,
            "max": 840,
            "unit": None,
        },
        {
            "name": f"{_S_TIME}\u200b\u200bTime: NTP Port",
            "key": "ntp-port",
            "device_class": None,
            "icon": "mdi:numeric",
            "visible": True,
            "entity_category": "config",
            "min": 1,
            "max": 65535,
            "unit": None,
        },
        {
            "name": f"{_S_MQTT}\u200b\u200bMQTT: Port",
            "key": "mqtt-port",
            "device_class": None,
            "icon": "mdi:numeric",
            "visible": True,
            "entity_category": "config",
            "min": 1,
            "max": 65535,
            "unit": None,
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
        {
            "name": f"{_S_APP}Local App: Enable",
            "key": "app-enable",
            "icon_on": "mdi:application-cog",
            "icon_off": "mdi:application-off",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_MQTT}MQTT: Enable",
            "key": "mqtt-enable",
            "icon_on": "mdi:access-point-network",
            "icon_off": "mdi:access-point-network-off",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_REPORTQ}Reporting and Quality: Auto Update Firmware",
            "key": "update-auto",
            "icon_on": "mdi:update",
            "icon_off": "mdi:update-off",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_REPORTQ}\u200bReporting and Quality: Report Usage Statistics",
            "key": "usage-reporting",
            "icon_on": "mdi:chart-line",
            "icon_off": "mdi:chart-line-variant",
            "visible": True,
            "entity_category": "config",
        },
    ],
    "text": [
        {
            "name": "Status",
            "key": "status",
            "icon": "mdi:information-outline",
            "visible": True,
        },
        {
            "name": f"{_S_CFG}Configuration",
            "key": "__header_00_configuration",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_WIFI}WiFi",
            "key": "__header_10_wifi",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_WIFI}WiFi: Name",
            "key": "wifi-ssid",
            "icon": "mdi:wifi-cog",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_WIFI}WiFi: Password",
            "key": "wifi-pass",
            "icon": "mdi:form-textbox-password",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_CLOUD}Cloud",
            "key": "__header_20_cloud",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_CLOUD}Cloud: Token",
            "key": "cloud-token",
            "icon": "mdi:cloud-lock",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_DEVICE}Device",
            "key": "__header_30_device",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_DEVICE}Device: Name",
            "key": "name",
            "icon": "mdi:rename-box",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_DEVICE}\u200bDevice: Hostname",
            "key": "hostname",
            "icon": "mdi:identifier",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_THRESH}Thresholds",
            "key": "__header_40_thresholds",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_APP}Local App",
            "key": "__header_50_local_app",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_APP}Local App: Password",
            "key": "app-pass",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_TIME}Time",
            "key": "__header_60_time",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_TIME}\u200bTime: NTP Host",
            "key": "ntp-host",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_MQTT}MQTT",
            "key": "__header_70_mqtt",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_MQTT}\u200bMQTT: Host",
            "key": "mqtt-host",
            "icon": "mdi:server",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_MQTT}\u200b\u200b\u200bMQTT: Username",
            "key": "mqtt-user",
            "icon": "mdi:account",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_MQTT}\u200b\u200b\u200b\u200bMQTT: Password",
            "key": "mqtt-pass",
            "icon": "mdi:form-textbox-password",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_MQTT}\u200b\u200b\u200b\u200b\u200bMQTT: Topic Template",
            "key": "mqtt-topic-tmpl",
            "icon": "mdi:pound",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_MQTT}\u200b\u200b\u200b\u200b\u200b\u200bMQTT: Client ID",
            "key": "mqtt-clientid",
            "icon": "mdi:identifier",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_NET}Network",
            "key": "__header_80_network",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_NET}Network: Static IP",
            "key": "ip-static",
            "icon": "mdi:ip-network",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_NET}\u200bNetwork: Static Netmask",
            "key": "ip-netmask",
            "icon": "mdi:ip-outline",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_NET}\u200b\u200bNetwork: Static Gateway",
            "key": "ip-gateway",
            "icon": "mdi:router-network",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_NET}\u200b\u200b\u200bNetwork: Primary DNS",
            "key": "ip-dns1",
            "icon": "mdi:dns",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_NET}\u200b\u200b\u200b\u200bNetwork: Secondary DNS",
            "key": "ip-dns2",
            "icon": "mdi:dns-outline",
            "visible": True,
            "entity_category": "config",
        },
        {
            "name": f"{_S_REPORTQ}Reporting and Quality",
            "key": "__header_90_reporting",
            "visible": True,
            "entity_category": "config",
        },
    ],
}
