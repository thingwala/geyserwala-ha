####################################################################################
# Copyright (c) 2023 Thingwala                                                     #
####################################################################################
"""Geyserwala constants."""

import logging

DOMAIN = "thingwala_geyserwala"
DEFAULT_PORT = 80
DEFAULT_USERNAME = "admin"
DEFAULT_UPDATE_INTERVAL_SECONDS = 10
MIN_UPDATE_INTERVAL_SECONDS = 5

_LOGGER = logging.getLogger(__package__)

__all__ = [
    "DOMAIN",
    "DEFAULT_PORT",
    "DEFAULT_USERNAME",
    "DEFAULT_UPDATE_INTERVAL_SECONDS",
    "MIN_UPDATE_INTERVAL_SECONDS",
    "_LOGGER",
]
