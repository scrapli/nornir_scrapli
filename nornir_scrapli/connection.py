"""Nornir lifecycle adapters for scrapli v2 CLI and NETCONF connections."""

from typing import Any, Dict, Optional

from scrapli import Cli, Netconf
from scrapli.exceptions import OptionsException

from nornir.core.configuration import Config
from nornir_scrapli.connection_options import build_connection_options
from nornir_scrapli.exceptions import NornirScrapliInvalidOptions, NornirScrapliInvalidPlatform

CONNECTION_NAME = "scrapli"
PLATFORM_MAP = {
    "ios": "cisco_iosxe",
    "nxos": "cisco_nxos",
    "iosxr": "cisco_iosxr",
    "eos": "arista_eos",
    "junos": "juniper_junos",
}


class ScrapliCore:
    """Scrapli CLI connection plugin for Nornir."""

    connection: Cli

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
        """Open a CLI connection using nested inventory options.

        Args:
            hostname: Nornir connection hostname.
            username: Nornir username fallback.
            password: Nornir password fallback.
            port: Explicit port, or scrapli's transport default.
            platform: Scrapli definition or NAPALM alias.
            extras: Native option sections and optional definition override.
            configuration: Nornir configuration.

        Raises:
            NornirScrapliInvalidOptions: If the hostname is absent.
            NornirScrapliInvalidPlatform: If the definition cannot be loaded.
        """
        if hostname is None:
            raise NornirScrapliInvalidOptions("Connection hostname is required")
        options = build_connection_options(
            hostname=hostname,
            username=username,
            password=password,
            extras=extras,
            configuration=configuration,
            netconf=False,
        )
        definition = (extras or {}).get("definition")
        if definition is None:
            definition = (
                "default"
                if not platform or platform == "generic"
                else PLATFORM_MAP.get(platform, platform)
            )
        try:
            connection = Cli(
                host=hostname, port=port, definition_file_or_name=definition, **options
            )
        except OptionsException as exc:
            raise NornirScrapliInvalidPlatform(
                f"Invalid platform/definition `{definition}` for host `{hostname}`"
            ) from exc
        connection.open()
        self.connection = connection

    def close(self) -> None:
        """Close the CLI connection."""
        self.connection.close()


class ScrapliNetconf:
    """Scrapli NETCONF connection plugin for Nornir."""

    connection: Netconf

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
        """Open a NETCONF connection using nested inventory options.

        Args:
            hostname: Nornir connection hostname.
            username: Nornir username fallback.
            password: Nornir password fallback.
            port: Explicit port, otherwise 830.
            platform: Unused for NETCONF.
            extras: Native option sections.
            configuration: Nornir configuration.

        Raises:
            NornirScrapliInvalidOptions: If the hostname is absent.
        """
        _ = platform
        if hostname is None:
            raise NornirScrapliInvalidOptions("Connection hostname is required")
        options = build_connection_options(
            hostname=hostname,
            username=username,
            password=password,
            extras=extras,
            configuration=configuration,
            netconf=True,
        )
        connection = Netconf(host=hostname, port=830 if port is None else port, **options)
        connection.open()
        self.connection = connection

    def close(self) -> None:
        """Close the NETCONF connection."""
        self.connection.close()
