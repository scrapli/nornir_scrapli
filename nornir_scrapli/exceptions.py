"""nornir_scrapli.exceptions"""


class NornirScrapliInvalidOptions(ValueError):
    """Inventory options cannot be converted into native scrapli options."""


class NornirScrapliException(Exception):
    """nornir_scrapli base exception"""


class NornirScrapliInvalidPlatform(NornirScrapliException):
    """nornir_scrapli base exception"""
