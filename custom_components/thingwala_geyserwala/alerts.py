####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Alert/Notification rules for Geyserwala integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from homeassistant.core import HomeAssistant, callback

from .const import _LOGGER, DOMAIN


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AlertRule:
    """Represents a single alert rule."""

    rule_id: str
    entity_key: str
    condition_type: str  # "threshold", "error_code", "state_change"
    condition_value: Any
    severity: AlertSeverity
    message_template: str
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize rule to dict."""
        return {
            "rule_id": self.rule_id,
            "entity_key": self.entity_key,
            "condition_type": self.condition_type,
            "condition_value": self.condition_value,
            "severity": self.severity.value,
            "message_template": self.message_template,
            "enabled": self.enabled,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> AlertRule:
        """Deserialize rule from dict."""
        severity_str = data.get("severity", "warning")
        try:
            severity = AlertSeverity(severity_str)
        except ValueError:
            severity = AlertSeverity.WARNING
        return AlertRule(
            rule_id=data.get("rule_id", ""),
            entity_key=data.get("entity_key", ""),
            condition_type=data.get("condition_type", "threshold"),
            condition_value=data.get("condition_value"),
            severity=severity,
            message_template=data.get("message_template", ""),
            enabled=data.get("enabled", True),
        )


class AlertEvaluator:
    """Evaluates alert rules against sensor data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize alert evaluator."""
        self.hass = hass
        self.triggered_alerts: set[str] = set()

    def evaluate_rules(
        self,
        rules: list[AlertRule],
        current_data: dict[str, Any],
        previous_data: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Evaluate all rules and return triggered alerts."""
        alerts = []
        if previous_data is None:
            previous_data = {}

        for rule in rules:
            if not rule.enabled:
                continue

            if self._should_trigger(rule, current_data, previous_data):
                alert = self._create_alert(rule, current_data)
                if alert:
                    alerts.append(alert)

        return alerts

    def _should_trigger(
        self,
        rule: AlertRule,
        current_data: dict[str, Any],
        previous_data: dict[str, Any],
    ) -> bool:
        """Check if a rule should trigger."""
        try:
            if rule.condition_type == "threshold":
                return self._check_threshold(rule, current_data)
            elif rule.condition_type == "error_code":
                return self._check_error_code(rule, current_data)
            elif rule.condition_type == "state_change":
                return self._check_state_change(rule, current_data, previous_data)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("[Geyserwala] Error evaluating rule %s: %s", rule.rule_id, err)
        return False

    def _check_threshold(self, rule: AlertRule, data: dict[str, Any]) -> bool:
        """Check if a threshold condition is met."""
        if rule.entity_key not in data:
            return False

        current_value = data[rule.entity_key]
        if current_value is None:
            return False

        try:
            current_float = float(current_value)
            threshold = float(rule.condition_value)
            # Trigger if value is above threshold (can be extended for above/below logic)
            return current_float >= threshold
        except (TypeError, ValueError):
            return False

    def _check_error_code(self, rule: AlertRule, data: dict[str, Any]) -> bool:
        """Check if specific error codes are present."""
        if rule.entity_key not in data:
            return False

        current_value = data[rule.entity_key]
        if current_value is None:
            return False

        if isinstance(current_value, list):
            # Check if any error code in list matches the condition
            return rule.condition_value in current_value
        return current_value == rule.condition_value

    def _check_state_change(
        self,
        rule: AlertRule,
        current_data: dict[str, Any],
        previous_data: dict[str, Any],
    ) -> bool:
        """Check if entity state changed to a specific value."""
        if rule.entity_key not in current_data:
            return False

        current_value = current_data[rule.entity_key]
        previous_value = previous_data.get(rule.entity_key)

        # Trigger if state changed to the target value
        return previous_value != rule.condition_value and current_value == rule.condition_value

    def _create_alert(self, rule: AlertRule, data: dict[str, Any]) -> dict[str, Any] | None:
        """Create alert dict from rule."""
        try:
            message = rule.message_template.format(**data)
        except (KeyError, ValueError):
            message = rule.message_template

        return {
            "rule_id": rule.rule_id,
            "severity": rule.severity.value,
            "message": message,
            "entity_key": rule.entity_key,
            "timestamp": None,  # Set by caller if needed
        }

    @callback
    def async_handle_alert(self, alert: dict[str, Any]) -> None:
        """Handle a triggered alert by firing an event."""
        event_data = {
            "rule_id": alert["rule_id"],
            "severity": alert["severity"],
            "message": alert["message"],
            "entity_key": alert["entity_key"],
        }

        self.hass.bus.async_fire(f"{DOMAIN}_alert", event_data)
        _LOGGER.warning(
            "[Geyserwala] Alert %s (%s): %s",
            alert["rule_id"],
            alert["severity"],
            alert["message"],
        )
