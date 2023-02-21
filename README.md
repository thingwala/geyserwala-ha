Geyserwala - Home Assistant Integration <!-- omit in toc -->
===

***Home Assistant custom integration for Geyserwala***

# Installing into Home Assistant
At present this integration is a custom integration, a few steps are required to install it into your Home Assistant:
* Download this repository as a ZIP file by clicking this [link](https://github.com/thingwala/geyserwala-ha/zipball/main).
* Uncompress the ZIP file, and browse into it.
* Move/copy the `thingwala_geyserwala` folder to `.../homeassistant/core/config/custom_components/thingwala_geyserwala`.
* On the side bar menu select "**Developer Tools**".
* At the bottom left of the "**Check and Restart**" panel, click "**CHECK CONFIGURATION**".
* If you see "*Configuration will not prevent Home Assistant from starting!*", then click "**RESTART**" at the bottom right of the panel.

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

Note the integration includes advanced entities which are hidden by default. To change this: go to "**Setings**" -> "**Devices & Services**" -> Click the Geyserwala "*entities*" -> Adjust filters to show hidden entities -> Select the desired entites -> Click "**ENABLE SELECTED**" -> Edit the entities "*Advanced settings*". (If you find the Entity Status selection is disabled, first hide the entity.)

# Contribution
Yes please! We want our Geyserwala integration with Home Assistant to be the best it can be for everyone. If you have Home Assistant development experience or have just noticed a niggly bug, feel free to fork this repo and submit a pull request.

See [Set up Development Environment](https://developers.home-assistant.io/docs/development_environment/) for more details. Checkout your fork to a convienient location (inside the container scope) and symlink the `thingwala_geyserwala` folder to `.../core/config/custom_components/thingwala_geyserwala`.

# License
In the spirit of the Hackers of the [Tech Model Railroad Club](https://en.wikipedia.org/wiki/Tech_Model_Railroad_Club) from the [Massachusetts Institute of Technology](https://en.wikipedia.org/wiki/Massachusetts_Institute_of_Technology), who gave us all so very much to play with. The license is [MIT](./LICENSE).
