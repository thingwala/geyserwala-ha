####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala constants."""

import logging

DOMAIN = "thingwala_geyserwala"
DEFAULT_PORT = 80
DEFAULT_USERNAME = "admin"

_LOGGER = logging.getLogger(__package__)

__all__ = ["DOMAIN", "DEFAULT_PORT", "DEFAULT_USERNAME", "_LOGGER"]
