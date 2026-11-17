"""Nornir lifecycle adapters for scrapli v2 CLI and NETCONF connections."""

import asyncio
from typing import Any, Dict, FrozenSet, Optional, Union

from scrapli import Cli, Netconf
from scrapli.exceptions import OptionsException

from nornir.core.configuration import Config
from nornir.core.plugins.connections import ConnectionCapability
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
CAPABILITIES: FrozenSet[ConnectionCapability] = frozenset({"sync", "asyncio"})

Driver = Union[Cli, Netconf]


async def _release_partial_open(connection: Driver) -> None:
    """Release a driver whose asynchronous open failed or was cancelled.

    Scrapli frees the driver itself only when the native open call raises. A failed,
    timed out or cancelled wait for the open result leaves it allocated. Cleanup runs
    shielded so that a repeated cancellation cannot leak the driver, and its own errors
    are suppressed so that the original exception propagates.

    Args:
        connection: Native driver that did not finish opening.
    """
    if connection.ptr is None:
        return
    cleanup = asyncio.ensure_future(connection.close_async(force=True))
    while not cleanup.done():
        try:
            await asyncio.shield(cleanup)
        except asyncio.CancelledError:  # noqa: PERF203
            continue
        except Exception:
            break
    if not cleanup.cancelled():
        cleanup.exception()


class _ScrapliConnection:
    """Shared sync and asyncio lifecycle for the scrapli v2 drivers.

    One scrapli v2 driver object supports both modes, so both modes build the same
    driver and differ only in calling ``open``/``close`` or ``open_async``/``close_async``.
    Nornir binds an open connection to the mode that opened it.
    """

    connection: Any

    def __init__(self) -> None:
        self.connection = None

    def get_capabilities(self) -> FrozenSet[ConnectionCapability]:
        """Declare that the connection can be opened in sync or asyncio mode.

        Returns:
            Both Nornir connection capabilities.
        """
        return CAPABILITIES

    def _build(
        self,
        hostname: Optional[str],
        username: Optional[str],
        password: Optional[str],
        port: Optional[int],
        platform: Optional[str],
        extras: Optional[Dict[str, Any]],
        configuration: Optional[Config],
    ) -> Driver:
        raise NotImplementedError

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
        """Open the connection in sync mode.

        Args:
            hostname: Nornir connection hostname.
            username: Nornir username fallback.
            password: Nornir password fallback.
            port: Explicit port, or the driver default.
            platform: Scrapli definition or NAPALM alias.
            extras: Native option sections.
            configuration: Nornir configuration.
        """
        connection = self._build(
            hostname, username, password, port, platform, extras, configuration
        )
        connection.open()
        self.connection = connection

    async def aopen(
        self,
        hostname: Optional[str],
        username: Optional[str],
        password: Optional[str],
        port: Optional[int],
        platform: Optional[str],
        extras: Optional[Dict[str, Any]] = None,
        configuration: Optional[Config] = None,
    ) -> None:
        """Open the connection in asyncio mode.

        A failed or cancelled open closes the partly opened driver before the exception
        propagates, and leaves ``connection`` unset.

        Args:
            hostname: Nornir connection hostname.
            username: Nornir username fallback.
            password: Nornir password fallback.
            port: Explicit port, or the driver default.
            platform: Scrapli definition or NAPALM alias.
            extras: Native option sections.
            configuration: Nornir configuration.
        """
        connection = self._build(
            hostname, username, password, port, platform, extras, configuration
        )
        try:
            await connection.open_async()
        except BaseException:
            await _release_partial_open(connection)
            raise
        self.connection = connection

    def close(self) -> None:
        """Close a connection opened in sync mode; safe to call more than once."""
        if self.connection is None:
            return
        self.connection.close()
        self.connection = None

    async def aclose(self) -> None:
        """Close a connection opened in asyncio mode; safe to call more than once.

        The connection stays set when closing fails, so the close can be retried.
        """
        if self.connection is None:
            return
        await self.connection.close_async()
        self.connection = None


class ScrapliCore(_ScrapliConnection):
    """Scrapli CLI connection plugin for Nornir."""

    connection: Cli

    def _build(
        self,
        hostname: Optional[str],
        username: Optional[str],
        password: Optional[str],
        port: Optional[int],
        platform: Optional[str],
        extras: Optional[Dict[str, Any]],
        configuration: Optional[Config],
    ) -> Cli:
        """Build a CLI driver from nested inventory options.

        Args:
            hostname: Nornir connection hostname.
            username: Nornir username fallback.
            password: Nornir password fallback.
            port: Explicit port, or scrapli's transport default.
            platform: Scrapli definition or NAPALM alias.
            extras: Native option sections and optional definition override.
            configuration: Nornir configuration.

        Returns:
            The unopened CLI driver.

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
            return Cli(host=hostname, port=port, definition_file_or_name=definition, **options)
        except OptionsException as exc:
            raise NornirScrapliInvalidPlatform(
                f"Invalid platform/definition `{definition}` for host `{hostname}`"
            ) from exc


class ScrapliNetconf(_ScrapliConnection):
    """Scrapli NETCONF connection plugin for Nornir."""

    connection: Netconf

    def _build(
        self,
        hostname: Optional[str],
        username: Optional[str],
        password: Optional[str],
        port: Optional[int],
        platform: Optional[str],
        extras: Optional[Dict[str, Any]],
        configuration: Optional[Config],
    ) -> Netconf:
        """Build a NETCONF driver from nested inventory options.

        Args:
            hostname: Nornir connection hostname.
            username: Nornir username fallback.
            password: Nornir password fallback.
            port: Explicit port, otherwise 830.
            platform: Unused for NETCONF.
            extras: Native option sections.
            configuration: Nornir configuration.

        Returns:
            The unopened NETCONF driver.

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
        return Netconf(host=hostname, port=830 if port is None else port, **options)
