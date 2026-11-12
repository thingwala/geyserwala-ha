"""Config flow: zeroconf rediscovery at a new address updates the entry."""
from ipaddress import ip_address
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry

import custom_components.thingwala_geyserwala  # noqa: F401  (so it can be patched)

DOMAIN = "thingwala_geyserwala"


async def test_zeroconf_updates_host(hass: HomeAssistant):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"host": "192.168.1.10", "port": 80, "username": "admin", "password": ""},
        unique_id="ABC123",
    )
    entry.add_to_hass(hass)

    info = ZeroconfServiceInfo(
        ip_address=ip_address("192.168.1.99"),
        ip_addresses=[ip_address("192.168.1.99")],
        port=80,
        hostname="geyserwala.local.",
        type="_geyserwala._tcp.local.",
        name="geyserwala._geyserwala._tcp.local.",
        properties={"id": "ABC123"},
    )
    with patch(f"custom_components.{DOMAIN}.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF}, data=info)
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data["host"] == "192.168.1.99"
    assert "ip_address" not in entry.data
