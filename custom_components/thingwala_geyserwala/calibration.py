####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Sensor calibration and offset handling for Geyserwala integration."""

from __future__ import annotations

from typing import Any


class SensorCalibration:
    """Manages offset and multiplier calibration for sensors."""

    def __init__(
        self,
        offset: float | None = None,
        multiplier: float | None = None,
    ) -> None:
        """Initialize calibration with offset and multiplier."""
        self.offset = float(offset) if offset is not None else 0.0
        self.multiplier = float(multiplier) if multiplier is not None else 1.0

    def apply(self, value: float | int | None) -> float | None:
        """Apply calibration (offset and multiplier) to a sensor value."""
        if value is None:
            return None
        numeric_value = float(value)
        return (numeric_value * self.multiplier) + self.offset

    def is_default(self) -> bool:
        """Check if calibration is at default (no offset, multiplier=1)."""
        return self.offset == 0.0 and self.multiplier == 1.0

    def to_dict(self) -> dict[str, float]:
        """Serialize calibration to dict."""
        return {
            "offset": self.offset,
            "multiplier": self.multiplier,
        }

    @staticmethod
    def from_dict(data: dict[str, Any] | None) -> SensorCalibration:
        """Deserialize calibration from dict."""
        if data is None:
            return SensorCalibration()
        return SensorCalibration(
            offset=data.get("offset", 0.0),
            multiplier=data.get("multiplier", 1.0),
        )


def get_entity_calibration(
    entity_key: str, calibrations: dict[str, dict[str, Any]] | None
) -> SensorCalibration:
    """Get calibration for a specific entity."""
    if calibrations is None or entity_key not in calibrations:
        return SensorCalibration()
    return SensorCalibration.from_dict(calibrations[entity_key])


def apply_calibration_to_value(
    value: float | int | None,
    entity_key: str,
    calibrations: dict[str, dict[str, Any]] | None,
) -> float | None:
    """Apply calibration to a value for a specific entity."""
    calibration = get_entity_calibration(entity_key, calibrations)
    return calibration.apply(value)
