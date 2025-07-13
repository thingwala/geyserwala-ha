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
* Type "*Geysewala*" into the search box.
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

# Contribution
Yes please! We want our Geyserwala integration with Home Assistant to be the best it can be for everyone. If you have Home Assistant development experience or have just noticed a niggly bug, feel free to fork this repo and submit a pull request.

See [Set up Development Environment](https://developers.home-assistant.io/docs/development_environment/) for more details. Checkout your fork to a convienient location (inside the container scope) and symlink the `thingwala_geyserwala` folder to `.../core/config/custom_components/thingwala_geyserwala`.

# License
In the spirit of the Hackers of the [Tech Model Railroad Club](https://en.wikipedia.org/wiki/Tech_Model_Railroad_Club) from the [Massachusetts Institute of Technology](https://en.wikipedia.org/wiki/Massachusetts_Institute_of_Technology), who gave us all so very much to play with. The license is [MIT](./LICENSE).
