"""nornir_scrapli.connection"""
from typing import Any, Dict, Optional

from scrapli import Scrapli
from scrapli.driver import GenericDriver
from scrapli_netconf.driver import NetconfScrape

from nornir.core.configuration import Config
from nornir_scrapli.exceptions import NornirScrapliInvalidPlatform

CONNECTION_NAME = "scrapli"

PLATFORM_MAP = {
    "ios": "cisco_iosxe",
    "nxos": "cisco_nxos",
    "iosxr": "cisco_iosxr",
    "eos": "arista_eos",
    "junos": "juniper_junos",
}


class ScrapliCore:
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

        if not platform:
            raise NornirScrapliInvalidPlatform(
                f"No `platform` provided in inventory for host `{hostname}`"
            )

        if platform in PLATFORM_MAP:
            platform = PLATFORM_MAP.get(platform)

        if platform == "generic":
            connection = GenericDriver(**parameters)
        else:
            try:
                connection = Scrapli(**parameters, platform=platform)  # type: ignore
            except ModuleNotFoundError as exc:
                raise NornirScrapliInvalidPlatform(
                    f"Provided platform `{platform}` is not a valid scrapli or napalm platform, "
                    "or is not a valid scrapli-community platform."
                ) from exc

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


class ScrapliNetconf:
    """Scrapli NETCONF connection plugin for nornir"""

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
            platform: platform from nornir inventory/connection_options for scrapli; ignored with
                scrapli netconf
            extras: extras dict from connection_options for scrapli -- pass all other scrapli
                arguments here
            configuration: nornir configuration

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        # for now not trying to get ssh config out of configuration, but should in the future...
        # platform is irrelevant for scrapli netconf for now
        _, _ = configuration, platform
        extras = extras or {}

        parameters: Dict[str, Any] = {
            "host": hostname,
            "auth_username": username or "",
            "auth_password": password or "",
            "port": port or 22,
        }

        parameters.update(extras)

        connection = NetconfScrape(**parameters)
        connection.open()
        self.connection = connection  # pylint: disable=W0201

    def close(self) -> None:
        """
        Close a scrapli netconf connection to a device

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        self.connection.close()
