<!-- markdownlint-disable MD025 MD040 MD059 -->
Geyserwala - Home Assistant Integration <!-- omit in toc -->
===

***Home Assistant custom integration for Geyserwala***

# Installing into Home Assistant
At present this integration is a custom integration that consumes the HTTP REST interface,  a few steps are required to install it into your Home Assistant. If you would like consume the MQTT interface using your own custom entities see [MQTT.md](./MQTT.md)

To install it into your Home Assistant you have two options:

## Installing using [HACS](https://hacs.xyz/)

* Add this repo as an integration custom repo:
  * On the side bar menu select "**HACS**"..
  * Click the three dot menu in the top right.
  * Click on "**Custom repositories**".
  * Paste `https://github.com/thingwala/geyserwala-ha` into the "**Repository**" field.
  * Set the type to "**Integration**".
  * Click "**Add**".
* Search for "**Geyserwala**".
* Click on the integration.
* Click "**Download**" in the bottom right.
* Click "**Download**" in the popup.
* On the side bar menu select "**Developer Tools**".
* At the bottom left of the "**Check and Restart**" panel, click "**CHECK CONFIGURATION**".
* If you see "*Configuration will not prevent Home Assistant from starting!*", then click "**RESTART**" at the bottom right of the panel.

## Installing custom integration manually

* Download this repository as a ZIP file by clicking this [link](https://github.com/thingwala/geyserwala-ha/zipball/main).
* Uncompress the ZIP file, and browse into it.
* Move/copy the `thingwala_geyserwala` folder to `.../homeassistant/core/config/custom_components/thingwala_geyserwala`.
* On the side bar menu select "**Developer Tools**".
* At the bottom left of the "**Check and Restart**" panel, click "**CHECK CONFIGURATION**".
* If you see "*Configuration will not prevent Home Assistant from starting!*", then click "**RESTART**" at the bottom right of the panel.

An example using the Terminal Add-on on Home Assistant OS:

```
wget https://github.com/thingwala/geyserwala-ha/archive/refs/tags/v0.0.9.zip
unzip v0.0.9.zip
mkdir -p /config/custom_components/
cp -r geyserwala-ha-0.0.9/custom_components/thingwala_geyserwala /config/custom_components/
# Then test config and restart
```

# Multiple Devices
The Home Assistant entity IDs are derived from the Geyserwala "Hostname", so for cleaner entity IDs be sure to configure each Geyserwala with a unique hostname before adding the device.

# Adding your Geyserwala
The integration is written to allow Home Assistant to discover your Geyserwala on your network using Zeroconf. However if you do not get a notification:
* On the side bar menu select "**Settings**".
* Then select "**Devices & Services**"
* Then click "**+ ADD INTEGRATION**" at the bottom right of your browser.
* Type "*Geyserwala*" into the search box.
* "*Geyserwala*" should show up in the list, click it.
* Enter the device details.
  * You can use your Geyserwala `IP` address as the `Host`, which you can find by looking on the device menus. Press SET 4 times, "Info" page 1.
* Click "**SUBMIT**", and then "**FINISH**".
* Your Geyserwala should now be available to your Home Assistant dashboard.

Note the integration includes advanced entities which are hidden by default. To change this: go to "**Settings**" -> "**Devices & Services**" -> Click the Geyserwala "*entities*" -> Adjust filters to show hidden entities -> Select the desired entites -> Click "**ENABLE SELECTED**" -> Edit the entities "*Advanced settings*". (If you find the Entity Status selection is disabled, first hide the entity.)

# Custom Entities
It is possible to configure additional entities to access more advanced Geyserwala values by adding an entry to `configuration.yaml`, e.g.:

```
thingwala_geyserwala:
  custom_entities:
    sensor:
    - name: Element Runtime
      key: element-seconds
      device_class: duration
      icon: mdi:heating-coil
      visible: True
      unit: s
    - name: Element Cycles
      key: element-cycles
      icon: mdi:heating-coil
      visible: True
    - name: Pump Runtime
      key: pump-seconds
      device_class: duration
      icon: mdi:pump
      visible: True
      unit: s
    - name: Pump Cycles
      key: pump-cycles
      icon: mdi:pump
      visible: True
```

Entity types `binary_sensor`, `number`, `sensor`, `switch` and `text` are supported. The schema for each type is defined in the Python file of the same name in the source.

# Polling Interval Options
The integration includes an options flow to tune polling in Home Assistant:

* Go to "**Settings**" -> "**Devices & Services**".
* Open your Geyserwala integration card and select "**Configure**".
* Set "**Update interval (seconds)**".

Notes:
* The integration enforces a safe minimum interval of 5 seconds.
* The default interval is 10 seconds.

# Updating Device Connection Settings
If you need to change the device connection settings (host, port, username, or password), you can reconfigure the integration:

## Reconfiguring Device Settings

1. Go to "**Settings**" -> "**Devices & Services**".
2. Find your Geyserwala device (not the integration, but the actual device listed under your integration).
3. Click the device to open its details page.
4. Click the "**⋮**" (three dots) menu in the top right.
5. Click "**Reconfigure**".
6. Update the device connection settings:
   * **Host**: IP address or hostname of the Geyserwala device
   * **Port**: Port number (default: 8080)
   * **Username**: Device username
   * **Password**: Device password
7. Click "**Submit**".
8. The integration will validate the new settings and automatically reload with the updated configuration.

**Notes:**
* The device will be validated before applying changes to ensure the connection is working.
* The integration will reload automatically after successful reconfiguration.
* If validation fails, you'll be returned to the reconfiguration form to correct the settings.
* To find your device's IP address, press SET 4 times on the device to view the "Info" page.

# Configuration Flow and Feature Management

The integration provides a comprehensive configuration UI for managing polling and enabling/disabling features. Your feature configurations are **always preserved** - disabling and re-enabling a feature restores your previous settings.

## Accessing Configuration

1. Go to "**Settings**" -> "**Devices & Services**".
2. Find your Geyserwala integration and click "**Configure**".

## Step 1: Integration Settings & Features

This step allows you to configure the polling interval and enable/disable features:

### Polling Configuration
* **Update interval (seconds)**: How often the integration polls the device
  * Minimum: 5 seconds
  * Maximum: 600 seconds
  * Default: 10 seconds

### Feature Toggles

Enable or disable the following features:

* **Enable Custom Services**: Provides services to control boost, mode, and error codes
  * Default: **Enabled**
  * Services: `set_boost`, `set_mode`, `read_error_codes`, `clear_error_codes`

* **Enable MQTT Transport**: Use MQTT for device communication instead of HTTP
  * Default: **Disabled**
  * Requires: Home Assistant MQTT broker configured

* **Enable Sensor Calibration**: Apply per-entity offset and multiplier adjustments
  * Default: **Disabled**
  * Use case: Correct sensor drift or scale conversions

* **Enable Alert Rules**: Create threshold and state-change alerts
  * Default: **Disabled**
  * Supports: Multiple alert conditions and severity levels

## Step 2: Configure Enabled Features

After enabling features, you'll see a second configuration step with settings for each enabled feature.

### MQTT Transport Configuration
**Only shown if MQTT Transport is enabled.**

- **Transport Protocol**: Select `http` or `mqtt`
- **MQTT Base Topic**: Root topic for device communication (default: `geyserwala`)

### Sensor Calibration Configuration
**Only shown if Sensor Calibration is enabled.**

- **Sensor Calibrations**: JSON object with per-entity calibration settings
  ```json
  {
    "sensor.geyserwala_temperature": {"offset": 0, "multiplier": 1},
    "sensor.geyserwala_humidity": {"offset": 5, "multiplier": 0.95}
  }
  ```

### Alert Rules Configuration
**Only shown if Alert Rules is enabled.**

* **Alert Rules**: JSON array of alert rule definitions
  ```json
  [
    {
      "rule_id": "temp_threshold",
      "entity_key": "temperature",
      "condition_type": "threshold",
      "condition_value": 60,
      "severity": "warning",
      "message_template": "Temperature is too high: {value}°C",
      "enabled": true
    }
  ]
  ```

## Feature Persistence

**Important**: Feature configurations are saved to your Home Assistant configuration, even when a feature is disabled. If you:
1. Enable a feature and configure it
2. Disable the feature
3. Re-enable the same feature later

Your previous configuration will be restored automatically. This allows you to temporarily disable features without losing your settings.

# MQTT Transport Support
The integration now supports both HTTP and MQTT transport modes, allowing you to choose the communication method that best suits your network.

## Enabling MQTT Transport

1. Go to "**Settings**" -> "**Devices & Services**".
2. Open your Geyserwala integration card and select "**Configure**".
3. In the **Integration Settings & Features** step, toggle "**Enable MQTT Transport**" to **ON**.
4. Click "**Submit**" to proceed to feature configuration.
5. In the **Configure Enabled Features** step:
   * Select "**mqtt**" from the **Transport Protocol** dropdown.
   * Set **MQTT Base Topic** (default: `geyserwala`).
   * Click "**Submit**".
6. Ensure your Home Assistant MQTT broker is properly configured.

## MQTT Topic Structure

The integration will use the following MQTT topics:
* **State subscription**: `{base_topic}/{device_id}/state` - Receives device state as JSON
* **Command publishing**: `{base_topic}/{device_id}/command` - Sends device commands

Example state payload:
```json
{
  "temperature": 45.5,
  "humidity": 60.0,
  "error_codes": [],
  "mode": "Manual"
}
```

Example command payload:
```json
{
  "action": "set_boost",
  "enabled": true,
  "duration_minutes": 30
}
```

# Device Diagnostics
The integration exposes device diagnostics for troubleshooting. Device Diagnostics are **automatically enabled** - no configuration required.

To access diagnostics:

1. Go to "**Settings**" -> "**Devices & Services**".
2. Select your Geyserwala device.
3. Click the "**Device Support**" menu (three dots icon).
4. Select "**Download Diagnostics**".

The diagnostics report includes:
* Coordinator state (last update, success/failure status)
* Device information (ID, name, hostname)
* Last error details (if any)
* Update timing information

# Custom Services
The integration provides services for advanced device control and automation. Custom Services are **enabled by default** - no configuration required. They are available via the Developer Tools or in automations.

## Enabling/Disabling Custom Services

To disable custom services:
1. Go to "**Settings**" -> "**Devices & Services**".
2. Open your Geyserwala integration card and select "**Configure**".
3. In the **Integration Settings & Features** step, toggle "**Enable Custom Services**" to **OFF**.
4. Click "**Submit**".

Services will be disabled immediately. To re-enable, toggle the feature back on in configuration.

## Available Services

### set_boost
Enable or disable boost mode with optional duration.

**Service**: `thingwala_geyserwala.set_boost`

**Parameters**:
* `device_id`: The Geyserwala device ID (required)
* `enabled`: true/false (required)
* `duration_minutes`: 0-480 minutes (optional, 0 = device default)

**Example automation**:
```yaml
automation:
  - alias: "Boost geyser for 30 minutes"
    trigger:
      platform: time
      at: "06:00:00"
    action:
      service: thingwala_geyserwala.set_boost
      data:
        device_id: device_xyz
        enabled: true
        duration_minutes: 30
```

### set_mode
Change the geyser operating mode.

**Service**: `thingwala_geyserwala.set_mode`

**Parameters**:
* `device_id`: The Geyserwala device ID (required)
* `mode`: Mode name, e.g., "Manual", "Scheduled", "Hybrid" (required)

**Example**:
```yaml
service: thingwala_geyserwala.set_mode
data:
  device_id: device_xyz
  mode: "Scheduled"
```

### read_error_codes
Retrieve all active error codes from the device.

**Service**: `thingwala_geyserwala.read_error_codes`

**Parameters**:
* `device_id`: The Geyserwala device ID (required)

### clear_error_codes
Clear all error codes from the device.

**Service**: `thingwala_geyserwala.clear_error_codes`

**Parameters**:
* `device_id`: The Geyserwala device ID (required)

# Sensor Calibration
Adjust sensor values with per-entity offset and multiplier settings to correct sensor drift or calibration errors.

## Enabling Sensor Calibration

1. Go to "**Settings**" -> "**Devices & Services**".
2. Open your Geyserwala integration card and select "**Configure**".
3. In the **Integration Settings & Features** step, toggle "**Enable Sensor Calibration**" to **ON**.
4. Click "**Submit**" to proceed to feature configuration.
5. In the **Configure Enabled Features** step, enter your calibration JSON in **Sensor Calibrations** field.
6. Click "**Submit**".

## Calibration Formula

Each entity's sensor value is adjusted as follows:
```
adjusted_value = (original_value * multiplier) + offset
```

## Configuring Calibration

Sensor calibrations are configured by entering a JSON object with per-entity settings:

```json
{
  "sensor.geyserwala_temperature": {
    "offset": 2.5,
    "multiplier": 1.1
  },
  "sensor.geyserwala_humidity": {
    "offset": 0.0,
    "multiplier": 0.95
  }
}
```

**Example**: If your temperature sensor reads 45°C with calibration `{"multiplier": 1.1, "offset": 2.5}`, it will show as `(45 * 1.1) + 2.5 = 52.0°C`

# Alert and Notification Rules
Set up alert rules to monitor device conditions and trigger automations when thresholds are exceeded.

## Enabling Alert Rules

1. Go to "**Settings**" -> "**Devices & Services**".
2. Open your Geyserwala integration card and select "**Configure**".
3. In the **Integration Settings & Features** step, toggle "**Enable Alert Rules**" to **ON**.
4. Click "**Submit**" to proceed to feature configuration.
5. In the **Configure Enabled Features** step, enter your alert rules JSON in **Alert Rules** field.
6. Click "**Submit**".

## Configuring Alert Rules

Alert rules are configured by entering a JSON array of rule definitions:

```json
[
  {
    "rule_id": "high_temp_alert",
    "entity_key": "temperature",
    "condition_type": "threshold",
    "condition_value": 50.0,
    "severity": "warning",
    "message_template": "Temperature is high: {value}°C",
    "enabled": true
  },
  {
    "rule_id": "error_detected",
    "entity_key": "error_codes",
    "condition_type": "error_code",
    "condition_value": "E001",
    "severity": "critical",
    "message_template": "Error E001 detected",
    "enabled": true
  },
  {
    "rule_id": "mode_error",
    "entity_key": "mode",
    "condition_type": "state_change",
    "condition_value": "Error",
    "severity": "error",
    "message_template": "Mode changed to Error",
    "enabled": true
  }
]
```

## Alert Types

### Threshold Alerts
Triggers when a sensor value exceeds a specified threshold.
* `condition_type`: `threshold`
* `condition_value`: numeric threshold value

### Error Code Alerts
Triggers when a specific error code appears in the error_codes list.
* `condition_type`: `error_code`
* `condition_value`: error code string (e.g., "E001")

### State Change Alerts
Triggers when an entity changes to a specific state.
* `condition_type`: `state_change`
* `condition_value`: target state value

## Using Alert Events

Alert rules fire Home Assistant events that can be used in automations:

```yaml
automation:
  - alias: "React to high temperature alert"
    trigger:
      platform: event
      event_type: thingwala_geyserwala_alert
      event_data:
        rule_id: high_temp_alert
    action:
      service: notify.mobile_app_your_phone
      data:
        message: "High temperature alert triggered"
```


This integration uses Home Assistant's `DataUpdateCoordinator` with production-focused behavior:

* Bounded retries with small exponential-style backoff during transient failures.
* Timeout protection for network I/O.
* Authentication failure escalation for config-entry reauth handling.
* Safer entity setup and icon fallback behavior for custom/unknown device values.

# Troubleshooting
If entities stop updating or appear unavailable:

* Check Home Assistant logs: **Settings** -> **System** -> **Logs**.
* Verify host/port/credentials in integration settings.
* Increase polling interval via options if your network is congested.
* Run "**Check configuration**" and restart Home Assistant.

# Development and CI
Local quality commands:

```bash
make setup
make check
make test
```

CI runs on GitHub Actions and includes:

* `hassfest` and HACS validation.
* Python linting (`ruff`).
* Unit tests (`pytest`).

# Contribution
Yes please! We want our Geyserwala integration with Home Assistant to be the best it can be for everyone. If you have Home Assistant development experience or have just noticed a niggly bug, feel free to fork this repo and submit a pull request.

See [Set up Development Environment](https://developers.home-assistant.io/docs/development_environment/) for more details. Checkout your fork to a convienient location (inside the container scope) and symlink the `thingwala_geyserwala` folder to `.../core/config/custom_components/thingwala_geyserwala`.

# License
In the spirit of the Hackers of the [Tech Model Railroad Club](https://en.wikipedia.org/wiki/Tech_Model_Railroad_Club) from the [Massachusetts Institute of Technology](https://en.wikipedia.org/wiki/Massachusetts_Institute_of_Technology), who gave us all so very much to play with. The license is [MIT](./LICENSE).
