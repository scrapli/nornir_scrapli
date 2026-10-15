"""nornir_scrapli.exceptions"""


class NornirScrapliException(Exception):
    """nornir_scrapli base exception"""


class NornirScrapliInvalidPlatform(NornirScrapliException):
    """nornir_scrapli base exception"""


class NornirScrapliNoConfigModeGenericDriver(NornirScrapliException):
    """nornir_scrapli exception for attempting config mode on generic platform"""
