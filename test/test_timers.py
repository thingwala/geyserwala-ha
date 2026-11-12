"""Timer entities, against a fake Geyserwala client."""
from copy import deepcopy
from datetime import time
from unittest.mock import patch


import custom_components.thingwala_geyserwala  # noqa: F401  (so it can be patched)

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

DOMAIN = "thingwala_geyserwala"

TIMERS = [
    {"id": 3, "begin": [8, 0], "end": [9, 45], "temp": 45, "dow": [True] * 7},
    {"id": 7, "begin": [13, 30], "end": [16, 0], "temp": 60, "dow": [True] * 5 + [False] * 2},
]


class FakeClient:
    """Stands in for GeyserwalaClientAsync."""

    def __init__(self, *args, timers=None, **kwargs):
        self._values = {
            "id": "ABC123", "name": "Geyserwala", "hostname": "geyserwala",
            "version": "1.0", "features": {}, "status": "Idle", "mode": "TIMER",
            "tank-temp": 50, "element-demand": False,
        }
        self.timers = deepcopy(TIMERS) if timers is None else timers
        self.updated = []

    id = property(lambda s: s._values["id"])
    name = property(lambda s: s._values["name"])
    hostname = property(lambda s: s._values["hostname"])
    version = property(lambda s: s._values["version"])
    modes = property(lambda s: ["SETPOINT", "TIMER", "STANDBY", "HOLIDAY"])
    mode = property(lambda s: s._values["mode"])

    def subscribe(self, key):
        pass

    def get_value(self, key):
        return self._values.get(key)

    async def update(self):
        return True

    async def list_timers(self):
        if isinstance(self.timers, Exception):
            raise self.timers
        return deepcopy(self.timers)

    async def update_timer(self, timer):
        self.updated.append(deepcopy(timer))
        for i, t in enumerate(self.timers):
            if t["id"] == timer["id"]:
                self.timers[i] = deepcopy(timer)
        return timer


async def _setup(hass: HomeAssistant, client: FakeClient, reload_after=None):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"host": "1.2.3.4", "port": 80, "username": "admin", "password": ""},
        unique_id="ABC123",
    )
    entry.add_to_hass(hass)
    with patch(f"custom_components.{DOMAIN}.GeyserwalaClientAsync", return_value=client):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        if reload_after:
            reload_after(hass)
            await hass.config_entries.async_reload(entry.entry_id)
            await hass.async_block_till_done()
    return entry


async def test_timer_entities(hass: HomeAssistant):
    client = FakeClient()
    await _setup(hass, client)

    s = hass.states.get("sensor.geyserwala_timer_1_summary")
    assert s.state == "08:00-09:45 45°C Every day"
    assert s.attributes["days"][0] == "monday"
    assert hass.states.get("sensor.geyserwala_timer_2_summary").state == "13:30-16:00 60°C Mon-Fri"
    assert hass.states.get("time.geyserwala_timer_1_start").state == "08:00:00"
    assert hass.states.get("time.geyserwala_timer_2_end").state == "16:00:00"
    assert float(hass.states.get("number.geyserwala_timer_1_temperature").state) == 45

    # Day switches exist but are disabled by default.
    reg = er.async_get(hass)
    day = reg.async_get("switch.geyserwala_timer_2_saturday")
    assert day is not None and day.disabled_by is not None

    await hass.services.async_call(
        "time", "set_value",
        {"entity_id": "time.geyserwala_timer_1_start", "time": time(7, 30)}, blocking=True)
    assert client.updated[-1]["begin"] == [7, 30]
    assert client.updated[-1]["end"] == [9, 45]

    await hass.services.async_call(
        "number", "set_value",
        {"entity_id": "number.geyserwala_timer_1_temperature", "value": 50}, blocking=True)
    assert client.updated[-1]["temp"] == 50
    await hass.async_block_till_done()
    assert hass.states.get("sensor.geyserwala_timer_1_summary").state == "07:30-09:45 50°C Every day"


async def test_day_switch(hass: HomeAssistant):
    client = FakeClient()
    await _setup(hass, client, reload_after=lambda h: er.async_get(h).async_update_entity(
        "switch.geyserwala_timer_2_saturday", disabled_by=None))

    assert hass.states.get("switch.geyserwala_timer_2_saturday").state == "off"
    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": "switch.geyserwala_timer_2_saturday"}, blocking=True)
    assert client.updated[-1]["dow"] == [True] * 6 + [False]


async def test_no_timers_still_loads(hass: HomeAssistant):
    from thingwala.geyserwala.errors import RequestError
    client = FakeClient(timers=RequestError())
    entry = await _setup(hass, client)
    assert entry.state.value == "loaded"
    assert len(hass.states.async_entity_ids("sensor")) >= 1
    assert not [e for e in hass.states.async_entity_ids() if "timer" in e]
    assert hass.states.get("sensor.geyserwala_timer_1_summary") is None
