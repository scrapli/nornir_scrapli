"""nornir_scrapli.connection"""
from typing import Any, Dict, Optional

from scrapli.driver import GenericDriver
from scrapli.driver.core import EOSDriver, IOSXEDriver, IOSXRDriver, JunosDriver, NXOSDriver

from nornir.core.configuration import Config
from nornir_scrapli.exceptions import NornirScrapliInvalidPlatform

CONNECTION_NAME = "scrapli"
PLATFORM_MAP = {
    "cisco_iosxe": IOSXEDriver,
    "cisco_nxos": NXOSDriver,
    "cisco_iosxr": IOSXRDriver,
    "arista_eos": EOSDriver,
    "juniper_junos": JunosDriver,
    "generic": GenericDriver,
}
NAPALM_PLATFORM_MAP = {
    "ios": IOSXEDriver,
    "nxos": NXOSDriver,
    "iosxr": IOSXRDriver,
    "eos": EOSDriver,
    "junos": JunosDriver,
}


class Scrapli:
    """Scrapli connection plugin for nornir"""

    def open(
        self,
        hostname: Optional[str],
        username: Optional[str],
        password: Optional[str],
        port: Optional[int],
        platform: Optional[str],
        extras: Optional[Dict[str, Any]] = None,
        configuration: Optional[Config] = None,
    ) -> None:
        """
        Open a scrapli connection to a device

        Args:
            hostname: hostname from nornir inventory
            username: username from nornir inventory/connection_options for scrapli
            password: password from nornir inventory/connection_options for scrapli
            port: port from nornir inventory/connection_options for scrapli
            platform: platform from nornir inventory/connection_options for scrapli
            extras: extras dict from connection_options for scrapli -- pass all other scrapli
                arguments here
            configuration: nornir configuration

        Returns:
            N/A  # noqa: DAR202

        Raises:
            NornirScrapliInvalidPlatform: if no platform or an invalid scrapli/napalm platform
                string is provided

        """
        # for now not trying to get ssh config out of configuration, but should in the future...
        _ = configuration
        extras = extras or {}

        parameters: Dict[str, Any] = {
            "host": hostname,
            "auth_username": username or "",
            "auth_password": password or "",
            "port": port or 22,
        }

        parameters.update(extras)

        scrapli_driver = None
        if platform is not None:
            scrapli_driver = PLATFORM_MAP.get(platform, NAPALM_PLATFORM_MAP.get(platform, None))
        if scrapli_driver is None:
            raise NornirScrapliInvalidPlatform(
                f"Provided platform `{platform}` is not a valid scrapli or napalm platform."
            )

        connection = scrapli_driver(**parameters)
        connection.open()
        self.connection = connection  # pylint: disable=W0201

    def close(self) -> None:
        """
        Close a scrapli connection to a device

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        self.connection.close()
