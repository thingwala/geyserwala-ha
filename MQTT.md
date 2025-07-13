# Home Assistant - Custom MQTT Entity Configuration
An alternative way to add a Geyserwala Connect is to add custom MQTT entities which gives you the freedom to completely customise your integration. Below is some sample YAML that can be edited and pasted into the `configuration.yaml`. On Home Assistant OS the file can be found in `/root/config`.

## MQTT Client
You will first need the MQTT integration to be added. **Settings** -> **Devices & Services** -> **Integrations** -> **ADD INTEGRATION** -> **"MQTT"**. You can choose to either configure the built in Home Assistant MQTT broker or your own broker.

## Entity YAML

Before adding the entity YAML there are a few things to edit:
* Rename `mqtt.sensor.device.name` from "**Geyserwala MQTT**" to the name of your geyser.
* Rename all occurences of `08A6F7501D00` to the MAC address of your Geyserwala, which can be found on the System page of the Local app.
* If you have the **MAX** or **Delta T** model with solar collector then set `enabled_by_default: true` for `mqtt.sensor.name[Collector]` and `mqtt.binary_sensor.name[Pump]`. And change `mqtt.select.name[Mode]` to use `SOLAR` rather than `STANDBY`.
* Also set `enabled_by_default: true` for any of the `mqtt.sensor.name[E? ...]` Geyserwise error codes that you are interested in.
* If you have changed the topic template from `geyserwala/%prefix%/%mac%` then you will need to adjust `mqtt.*.state_topic` and `mqtt.*.command_topic` accordingly.

Use as much or as little of the YAML example below as you wish.

Once you have made the required edits past the YAML into your `configuration.yaml`. Then click on **Developer Tools** -> **YAML configuration reloading** -> **MANUALLY CONFIGURED MQTT ENTITIES** and then refresh your dashboard to view the changes. If there are errors, view the logs at: **Settings** -> **System** -> **Logs**. It is also a good idea to run **Developer Tools** -> **Check and restart** -> **CHECK CONFIGURATION** to ensure that Home Assistant can still restart.

Entities will not update immediately since MQTT values are only published on change, however the Geyserwala will periodically re-publish all values every few minutes.

```
mqtt:

  sensor:
    - name: "Status"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
        name: "Geyserwala MQTT"
      unique_id: geyserwala_08A6F7501D00_status
      state_topic: "geyserwala/stat/08A6F7501D00/status"
      value_template: "{{ value }}"
      icon: mdi:information-outline

    - name: "Tank"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_tank_temp
      state_topic: "geyserwala/stat/08A6F7501D00/tank-temp"
      unit_of_measurement: "°C"
      device_class: temperature
      state_class: measurement
      value_template: "{{ value }}"
      icon: mdi:thermometer-water

    - name: "Collector"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_collector_temp
      state_topic: "geyserwala/stat/08A6F7501D00/tank-temp"
      unit_of_measurement: "°C"
      device_class: temperature
      state_class: measurement
      value_template: "{{ value }}"
      icon: mdi:sun-thermometer
      enabled_by_default: false

    - name: "E1 Earth Leakage"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_error_e1
      state_topic: "geyserwala/stat/08A6F7501D00/error/E1"
      value_template: >-
        {% if value == 'ON' %}ALERT{% else %}-{% endif %}
      icon: mdi:flash-alert
      enabled_by_default: false

    - name: "E2 Dry Burn Protection"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_error_e2
      state_topic: "geyserwala/stat/08A6F7501D00/error/E2"
      value_template: >-
        {% if value == 'ON' %}ALERT{% else %}-{% endif %}
      icon: mdi:fire-alert
      enabled_by_default: false

    - name: "E3 Tank probe failure"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_error_e3
      state_topic: "geyserwala/stat/08A6F7501D00/error/E3"
      value_template: >-
        {% if value == 'ON' %}ALERT{% else %}-{% endif %}
      icon: mdi:thermometer-alert
      enabled_by_default: false

    - name: "E4 Heating Failure"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_error_e4
      state_topic: "geyserwala/stat/08A6F7501D00/error/E4"
      value_template: >-
        {% if value == 'ON' %}ALERT{% else %}-{% endif %}
      icon: mdi:fire-alert
      enabled_by_default: false

    - name: "E5 Over Temperature"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_error_e5
      state_topic: "geyserwala/stat/08A6F7501D00/error/E5"
      value_template: >-
        {% if value == 'ON' %}ALERT{% else %}-{% endif %}
      icon: mdi:thermometer-alert
      enabled_by_default: false

    - name: "E6 Water Leak"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_error_e6
      state_topic: "geyserwala/stat/08A6F7501D00/error/E6"
      value_template: >-
        {% if value == 'ON' %}ALERT{% else %}-{% endif %}
      icon: mdi:water-alert
      enabled_by_default: false

    - name: "E7 Comms Failure"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_error_e7
      state_topic: "geyserwala/stat/08A6F7501D00/error/E7"
      value_template: >-
        {% if value == 'ON' %}ALERT{% else %}-{% endif %}
      icon: mdi:lan-disconnect
      enabled_by_default: false

    - name: "E8 Collector Probe Failure"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_error_e8
      state_topic: "geyserwala/stat/08A6F7501D00/error/E8"
      value_template: >-
        {% if value == 'ON' %}ALERT{% else %}-{% endif %}
      icon: mdi:weather-sunny-alert
      enabled_by_default: false

    - name: "E9 Pump Failure"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_error_e9
      state_topic: "geyserwala/stat/08A6F7501D00/error/E9"
      value_template: >-
        {% if value == 'ON' %}ALERT{% else %}-{% endif %}
      icon: mdi:pump-off
      enabled_by_default: false

  select:
    # If you have the MAX or Delta T with solar collector swap STANDY to SOLAR
    - name: "Mode"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_mode
      state_topic: "geyserwala/stat/08A6F7501D00/mode"
      command_topic: "geyserwala/cmnd/08A6F7501D00/mode"
      options:
        - STANDBY
        # - SOLAR
        - TIMER
        - HOLIDAY
        - SETPOINT
      value_template: "{{ value }}"
      icon: mdi:cog
  
  binary_sensor:
    - name: "Element"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_element_demand
      state_topic: "geyserwala/stat/08A6F7501D00/element-demand"
      payload_on: "ON"
      payload_off: "OFF"
      device_class: power
      icon: mdi:radiator

    - name: "Pump"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_pump_status
      state_topic: "geyserwala/stat/08A6F7501D00/pump-status"
      payload_on: "ON"
      payload_off: "OFF"
      device_class: running
      icon: mdi:pump
      enabled_by_default: false

  switch:
    - name: "Boost"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_boost_demand
      command_topic: "geyserwala/cmnd/08A6F7501D00/boost-demand"
      state_topic: "geyserwala/stat/08A6F7501D00/boost-demand"
      payload_on: "ON"
      payload_off: "OFF"
      state_on: "ON"
      state_off: "OFF"
      icon: mdi:fire

    - name: "External Demand"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_external_demand
      command_topic: "geyserwala/cmnd/08A6F7501D00/external-demand"
      state_topic: "geyserwala/stat/08A6F7501D00/external-demand"
      payload_on: "28800"
      payload_off: "OFF"
      state_off: "0"
      icon: mdi:fire
      enabled_by_default: false

    - name: "External Disable"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_external_disable
      command_topic: "geyserwala/cmnd/08A6F7501D00/external-disable"
      state_topic: "geyserwala/stat/08A6F7501D00/external-disable"
      payload_on: "28800"
      payload_off: "OFF"
      state_off: "0"
      icon: mdi:fire-off
      enabled_by_default: false

  number:
    - name: "Setpoint"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_setpoint
      command_topic: "geyserwala/cmnd/08A6F7501D00/setpoint"
      state_topic: "geyserwala/stat/08A6F7501D00/setpoint"
      device_class: temperature
      icon: mdi:thermostat
      min: 30
      max: 65
      unit_of_measurement: "°C"

    - name: "External Setpoint"
      device:
        identifiers: ["geyserwala_08A6F7501D00"]
      unique_id: geyserwala_08A6F7501D00_external_setpoint
      command_topic: "geyserwala/cmnd/08A6F7501D00/external-setpoint"
      state_topic: "geyserwala/stat/08A6F7501D00/external-setpoint"
      device_class: temperature
      icon: mdi:thermostat-auto
      min: 30
      max: 75
      unit_of_measurement: "°C"
      enabled_by_default: false
```

