####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Tests for Geyserwala integration features."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from custom_components.thingwala_geyserwala.alerts import (
    AlertEvaluator,
    AlertRule,
    AlertSeverity,
)
from custom_components.thingwala_geyserwala.calibration import (
    SensorCalibration,
    apply_calibration_to_value,
    get_entity_calibration,
)


class TestSensorCalibration:
    """Test sensor calibration functionality."""

    def test_calibration_init_defaults(self):
        """Test calibration initialization with defaults."""
        calib = SensorCalibration()
        assert calib.offset == 0.0
        assert calib.multiplier == 1.0
        assert calib.is_default()

    def test_calibration_with_offset(self):
        """Test calibration with offset."""
        calib = SensorCalibration(offset=5.0)
        assert calib.offset == 5.0
        assert calib.multiplier == 1.0
        assert not calib.is_default()

    def test_calibration_with_multiplier(self):
        """Test calibration with multiplier."""
        calib = SensorCalibration(multiplier=2.0)
        assert calib.offset == 0.0
        assert calib.multiplier == 2.0
        assert not calib.is_default()

    def test_apply_calibration(self):
        """Test applying calibration to values."""
        calib = SensorCalibration(offset=5.0, multiplier=2.0)
        result = calib.apply(10.0)
        assert result == 25.0  # (10 * 2) + 5

    def test_apply_calibration_with_none(self):
        """Test applying calibration to None."""
        calib = SensorCalibration(offset=5.0, multiplier=2.0)
        result = calib.apply(None)
        assert result is None

    def test_apply_calibration_with_int(self):
        """Test applying calibration to integer."""
        calib = SensorCalibration(offset=1.0, multiplier=1.5)
        result = calib.apply(10)
        assert result == 16.0  # (10 * 1.5) + 1

    def test_calibration_to_dict(self):
        """Test serializing calibration to dict."""
        calib = SensorCalibration(offset=2.5, multiplier=1.5)
        result = calib.to_dict()
        assert result == {"offset": 2.5, "multiplier": 1.5}

    def test_calibration_from_dict(self):
        """Test deserializing calibration from dict."""
        data = {"offset": 3.0, "multiplier": 2.0}
        calib = SensorCalibration.from_dict(data)
        assert calib.offset == 3.0
        assert calib.multiplier == 2.0

    def test_calibration_from_none_dict(self):
        """Test deserializing calibration from None dict."""
        calib = SensorCalibration.from_dict(None)
        assert calib.offset == 0.0
        assert calib.multiplier == 1.0

    def test_get_entity_calibration(self):
        """Test getting calibration for a specific entity."""
        calibrations = {
            "temp_sensor": {"offset": 1.0, "multiplier": 1.1},
            "humidity_sensor": {"offset": 0.0, "multiplier": 1.0},
        }
        calib = get_entity_calibration("temp_sensor", calibrations)
        assert calib.offset == 1.0
        assert calib.multiplier == 1.1

    def test_get_entity_calibration_missing(self):
        """Test getting calibration for missing entity."""
        calibrations = {"temp_sensor": {"offset": 1.0, "multiplier": 1.1}}
        calib = get_entity_calibration("missing_sensor", calibrations)
        assert calib.offset == 0.0
        assert calib.multiplier == 1.0

    def test_apply_calibration_to_value(self):
        """Test applying calibration to value via helper."""
        calibrations = {
            "temp_sensor": {"offset": 2.0, "multiplier": 1.5},
        }
        result = apply_calibration_to_value(20.0, "temp_sensor", calibrations)
        assert result == 32.0  # (20 * 1.5) + 2


class TestAlertRules:
    """Test alert rule and evaluator functionality."""

    def test_alert_rule_init(self):
        """Test alert rule initialization."""
        rule = AlertRule(
            rule_id="temp_alert",
            entity_key="temperature",
            condition_type="threshold",
            condition_value=50.0,
            severity=AlertSeverity.WARNING,
            message_template="Temperature is {temperature}°C",
        )
        assert rule.rule_id == "temp_alert"
        assert rule.entity_key == "temperature"
        assert rule.condition_type == "threshold"
        assert rule.condition_value == 50.0
        assert rule.severity == AlertSeverity.WARNING
        assert rule.enabled

    def test_alert_rule_to_dict(self):
        """Test serializing alert rule to dict."""
        rule = AlertRule(
            rule_id="temp_alert",
            entity_key="temperature",
            condition_type="threshold",
            condition_value=50.0,
            severity=AlertSeverity.ERROR,
            message_template="High temperature",
            enabled=False,
        )
        result = rule.to_dict()
        assert result["rule_id"] == "temp_alert"
        assert result["severity"] == "error"
        assert result["enabled"] is False

    def test_alert_rule_from_dict(self):
        """Test deserializing alert rule from dict."""
        data = {
            "rule_id": "error_alert",
            "entity_key": "error_code",
            "condition_type": "error_code",
            "condition_value": "E001",
            "severity": "critical",
            "message_template": "Error detected",
            "enabled": True,
        }
        rule = AlertRule.from_dict(data)
        assert rule.rule_id == "error_alert"
        assert rule.severity == AlertSeverity.CRITICAL
        assert rule.condition_type == "error_code"

    @pytest.mark.asyncio
    async def test_alert_evaluator_threshold(self):
        """Test alert evaluator with threshold condition."""
        hass = SimpleNamespace()
        evaluator = AlertEvaluator(hass)
        rule = AlertRule(
            rule_id="temp_alert",
            entity_key="temperature",
            condition_type="threshold",
            condition_value=50.0,
            severity=AlertSeverity.WARNING,
            message_template="Temperature is {temperature}°C",
        )

        # Below threshold - should not trigger
        data_low = {"temperature": 40.0}
        alerts = evaluator.evaluate_rules([rule], data_low)
        assert len(alerts) == 0

        # At threshold - should trigger
        data_at = {"temperature": 50.0}
        alerts = evaluator.evaluate_rules([rule], data_at)
        assert len(alerts) == 1
        assert alerts[0]["rule_id"] == "temp_alert"

        # Above threshold - should trigger
        data_high = {"temperature": 60.0}
        alerts = evaluator.evaluate_rules([rule], data_high)
        assert len(alerts) == 1

    @pytest.mark.asyncio
    async def test_alert_evaluator_error_code(self):
        """Test alert evaluator with error code condition."""
        hass = SimpleNamespace()
        evaluator = AlertEvaluator(hass)
        rule = AlertRule(
            rule_id="error_alert",
            entity_key="error_codes",
            condition_type="error_code",
            condition_value="E001",
            severity=AlertSeverity.CRITICAL,
            message_template="Error E001 detected",
        )

        # No error - should not trigger
        data_no_error = {"error_codes": []}
        alerts = evaluator.evaluate_rules([rule], data_no_error)
        assert len(alerts) == 0

        # Error present - should trigger
        data_with_error = {"error_codes": ["E001", "E002"]}
        alerts = evaluator.evaluate_rules([rule], data_with_error)
        assert len(alerts) == 1

    @pytest.mark.asyncio
    async def test_alert_evaluator_state_change(self):
        """Test alert evaluator with state change condition."""
        hass = SimpleNamespace()
        evaluator = AlertEvaluator(hass)
        rule = AlertRule(
            rule_id="mode_alert",
            entity_key="mode",
            condition_type="state_change",
            condition_value="Error",
            severity=AlertSeverity.ERROR,
            message_template="Mode changed to Error",
        )

        previous_data = {"mode": "Normal"}
        current_data = {"mode": "Error"}

        alerts = evaluator.evaluate_rules([rule], current_data, previous_data)
        assert len(alerts) == 1

    @pytest.mark.asyncio
    async def test_alert_evaluator_disabled_rule(self):
        """Test that disabled rules don't trigger."""
        hass = SimpleNamespace()
        evaluator = AlertEvaluator(hass)
        rule = AlertRule(
            rule_id="temp_alert",
            entity_key="temperature",
            condition_type="threshold",
            condition_value=50.0,
            severity=AlertSeverity.WARNING,
            message_template="Temperature alert",
            enabled=False,
        )

        data = {"temperature": 60.0}
        alerts = evaluator.evaluate_rules([rule], data)
        assert len(alerts) == 0

    @pytest.mark.asyncio
    async def test_alert_evaluator_multiple_rules(self):
        """Test evaluating multiple rules."""
        hass = SimpleNamespace()
        evaluator = AlertEvaluator(hass)
        rule1 = AlertRule(
            rule_id="alert1",
            entity_key="temp",
            condition_type="threshold",
            condition_value=50.0,
            severity=AlertSeverity.WARNING,
            message_template="Temp high",
        )
        rule2 = AlertRule(
            rule_id="alert2",
            entity_key="humidity",
            condition_type="threshold",
            condition_value=80.0,
            severity=AlertSeverity.WARNING,
            message_template="Humidity high",
        )

        data = {"temp": 55.0, "humidity": 85.0}
        alerts = evaluator.evaluate_rules([rule1, rule2], data)
        assert len(alerts) == 2
        assert {a["rule_id"] for a in alerts} == {"alert1", "alert2"}


class TestMQTTClient:
    """Test MQTT client functionality."""

    @pytest.mark.asyncio
    async def test_mqtt_client_init(self):
        """Test MQTT client initialization."""
        from custom_components.thingwala_geyserwala.mqtt import (
            GeyserwalaClientMQTT,
        )

        hass = SimpleNamespace()
        client = GeyserwalaClientMQTT(hass, "device123", "geyserwala")
        assert client.device_id == "device123"
        assert client.id == "device123"
        assert client.base_topic == "geyserwala"
        assert client.device_topic == "geyserwala/device123"

    @pytest.mark.asyncio
    async def test_mqtt_client_state_update(self):
        """Test MQTT client state update handling."""
        from custom_components.thingwala_geyserwala.mqtt import (
            GeyserwalaClientMQTT,
        )

        hass = SimpleNamespace()
        client = GeyserwalaClientMQTT(hass, "device123")

        # Simulate a message object
        msg = MagicMock()
        msg.payload = json.dumps({"temperature": 45.5, "humidity": 60.0}).encode()

        client._handle_state_update(msg)
        assert client._data["temperature"] == 45.5
        assert client._data["humidity"] == 60.0

    @pytest.mark.asyncio
    async def test_mqtt_client_getattr(self):
        """Test MQTT client attribute access."""
        from custom_components.thingwala_geyserwala.mqtt import (
            GeyserwalaClientMQTT,
        )

        hass = SimpleNamespace()
        client = GeyserwalaClientMQTT(hass, "device123")
        client._data = {"temperature": 45.5, "status": "on"}

        assert client.temperature == 45.5
        assert client.status == "on"
        assert client.missing_field is None
