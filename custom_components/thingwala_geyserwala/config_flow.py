####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala config flow."""

from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.const import CONF_IP_ADDRESS, CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import (
    async_create_clientsession,
)
from homeassistant.util.network import is_ipv6_address

from thingwala.geyserwala.aio.client import GeyserwalaClientAsync
from thingwala.geyserwala.errors import GeyserwalaException, Unauthorized

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_USERNAME


class GeyserwalaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Geyserwala config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Init."""
        self._config: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}

    async def async_step_zeroconf(self, discovery_info: zeroconf.ZeroconfServiceInfo) -> FlowResult:
        """Handle zeroconf discovery."""
        properties = discovery_info.properties
        ip_address = discovery_info.host
        port = discovery_info.port
        if is_ipv6_address(ip_address):
            return self.async_abort(reason="ipv6_not_supported")
        uuid = properties["id"]
        await self.async_set_unique_id(uuid)
        self._abort_if_unique_id_configured(updates={CONF_IP_ADDRESS: ip_address, CONF_PORT: port})
        self._config.update({
            CONF_HOST: ip_address,
            CONF_PORT: port,
            CONF_USERNAME: None,
            CONF_PASSWORD: None,
        })
        return await self.async_step_user()

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle user input."""
        if user_input is not None:
            self._async_abort_entries_match(
                {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                }
            )
            self._config.update(user_input)
            return await self.async_step_validate()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=self._config.get(CONF_HOST, '')): str,
                vol.Required(CONF_PORT, default=self._config.get(CONF_PORT, DEFAULT_PORT)): int,
                vol.Required(CONF_USERNAME, default=self._config.get(CONF_USERNAME, None) or DEFAULT_USERNAME): str,
                vol.Optional(CONF_PASSWORD, default=""): str,
            }
        )

        return self.async_show_form(step_id="user",
                                    data_schema=data_schema,
                                    errors=self._errors,
                                    )

    async def async_step_validate(self) -> FlowResult:
        """Handle device validation."""
        session = async_create_clientsession(self.hass)
        api = GeyserwalaClientAsync(host=self._config[CONF_HOST],
                                    port=self._config[CONF_PORT],
                                    username=self._config[CONF_USERNAME],
                                    password=self._config[CONF_PASSWORD],
                                    session=session,
                                    )
        try:
            if not await api.update():
                return self.async_abort(reason="unreachable")
        except Unauthorized:
            self._errors['base'] = 'invalid_auth'
            return await self.async_step_user()
        except GeyserwalaException:
            self._errors['base'] = 'cannot_connect'
            return await self.async_step_user()
        self._config['id'] = api.id
        self._config['name'] = api.name

        return self.async_create_entry(
            title=self._config['name'],
            data=self._config
        )
