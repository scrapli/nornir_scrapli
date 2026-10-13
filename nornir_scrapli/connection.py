"""nornir_scrapli.connection"""

import asyncio
from typing import Any, Dict, Optional

from scrapli import AsyncScrapli, Scrapli
from scrapli.driver import AsyncGenericDriver, GenericDriver
from scrapli.exceptions import ScrapliModuleNotFound
from scrapli_cfg import AsyncScrapliCfg, ScrapliCfg
from scrapli_netconf.driver import NetconfDriver

from nornir.core.configuration import Config
from nornir.core.task import Task
from nornir_scrapli.connection_mode import ModeBoundConnection
from nornir_scrapli.exceptions import NornirScrapliException, NornirScrapliInvalidPlatform

CONNECTION_NAME = "scrapli"

PLATFORM_MAP = {
    "ios": "cisco_iosxe",
    "nxos": "cisco_nxos",
    "iosxr": "cisco_iosxr",
    "eos": "arista_eos",
    "junos": "juniper_junos",
}


class ScrapliCore(ModeBoundConnection):
    """Scrapli connection plugin for nornir"""

    connection_name = CONNECTION_NAME

    @staticmethod
    def get_connection(task: Task) -> Any:
        """Acquire the raw synchronous driver with a cache-hit mode guard.

        Args:
            task: nornir Task object

        Returns:
            The established synchronous Scrapli driver

        """
        connection = task.host.get_connection(CONNECTION_NAME, task.nornir.config)
        plugin = task.host.connections[CONNECTION_NAME]
        if isinstance(plugin, ModeBoundConnection):
            plugin.require_mode("sync")
        return connection

    @staticmethod
    async def aget_connection(task: Task) -> Any:
        """Acquire the raw asyncio driver with a cache-hit mode guard.

        Args:
            task: nornir Task object

        Returns:
            The established asynchronous Scrapli driver

        """
        connection = await task.host.aget_connection(CONNECTION_NAME, task.nornir.config)
        plugin = task.host.connections[CONNECTION_NAME]
        if isinstance(plugin, ModeBoundConnection):
            plugin.require_mode("asyncio")
        return connection

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
            None

        Raises:
            NornirScrapliInvalidPlatform: if no platform or an invalid scrapli/napalm platform
                string is provided

        """
        self.require_unopened("sync")
        extras = extras or {}
        # 99.9% configuration will always be passed here... but to be consistent w/ the other
        # plugins we'll leave the function signature same/same as the others
        global_config = configuration.dict() if configuration else {}

        parameters: Dict[str, Any] = {
            "host": hostname,
            "auth_username": username or "",
            "auth_password": password or "",
            "port": port or 22,
            "ssh_config_file": global_config.get("ssh", {}).get("config_file", False),
        }

        # will override any of the configs from global nornir config (such as ssh config file) with
        # options from "extras" (connection options)
        parameters.update(extras)

        if extras.get("channel_log", False) is True:
            # if channel_log value is just "True" we append the hostname so that we don't have a
            # single file for potentially hundreds (or more!) of devices which obviously won't
            # work very well. don't update the extras dict directly as that is probably coming from
            # group/default vars, so just push this right onto the new parameters' dict.
            parameters.update({"channel_log": f"scrapli_channel_{hostname}.log"})

        if not platform:
            raise NornirScrapliInvalidPlatform(
                f"'platform' not provided in inventory for host `{hostname}`"
            )

        final_platform: str = PLATFORM_MAP.get(platform, platform)

        if final_platform == "generic":
            connection = GenericDriver(**parameters)
        else:
            try:
                connection = Scrapli(**parameters, platform=final_platform)
            except ScrapliModuleNotFound as exc:
                raise NornirScrapliInvalidPlatform(
                    f"Provided platform `{final_platform}` is not a valid scrapli or napalm "
                    "platform, or is not a valid scrapli-community platform."
                ) from exc

        connection.open()
        self.connection = connection
        self.mode = "sync"

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
        """Open a native asynchronous Scrapli driver.

        Args:
            hostname: device hostname
            username: authentication username
            password: authentication password
            port: device port, defaulting to 22
            platform: Scrapli platform or supported alias
            extras: additional Scrapli options, defaulting transport to asyncssh
            configuration: global Nornir configuration

        Raises:
            NornirScrapliInvalidPlatform: if no platform or an invalid platform is supplied

        """
        self.require_unopened("asyncio")
        extras = extras or {}
        global_config = configuration.dict() if configuration else {}
        parameters: Dict[str, Any] = {
            "host": hostname,
            "auth_username": username or "",
            "auth_password": password or "",
            "port": port or 22,
            "ssh_config_file": global_config.get("ssh", {}).get("config_file", False),
            "transport": "asyncssh",
            **extras,
        }
        if extras.get("channel_log") is True:
            parameters["channel_log"] = f"scrapli_channel_{hostname}.log"
        if not platform:
            raise NornirScrapliInvalidPlatform(
                f"'platform' not provided in inventory for host `{hostname}`"
            )
        final_platform = PLATFORM_MAP.get(platform, platform)
        try:
            connection = (
                AsyncGenericDriver(**parameters)
                if final_platform == "generic"
                else AsyncScrapli(**parameters, platform=final_platform)
            )
        except ScrapliModuleNotFound as exc:
            raise NornirScrapliInvalidPlatform(
                f"Provided platform `{final_platform}` is not a valid scrapli or napalm "
                "platform, or is not a valid scrapli-community platform."
            ) from exc
        try:
            await connection.open()
        except BaseException:
            # Nornir cannot cache a failed open, so this plugin owns partial cleanup.
            connection.on_close = None
            cleanup = asyncio.create_task(connection.close())
            while not cleanup.done():
                try:
                    await asyncio.shield(cleanup)
                except asyncio.CancelledError:  # noqa: PERF203 - Drain cleanup after cancellation.
                    continue
                except Exception:
                    break
            if not cleanup.cancelled():
                cleanup.exception()
            raise
        self.connection = connection
        self.mode = "asyncio"

    def close(self) -> None:
        """
        Close a scrapli connection to a device

        Returns:
            None

        """
        self.require_mode("sync")
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            self.mode = None

    async def aclose(self) -> None:
        """Close an asyncio driver, retaining its state if closing fails."""
        self.require_mode("asyncio")
        if self.connection is not None:
            connection = self.connection
            if isinstance(connection, AsyncGenericDriver) and not connection.isalive():
                # Scrapli timeouts can close the transport before plugin cleanup.
                # Device logout hooks cannot run then, but channel logs still need closing.
                on_close = connection.on_close
                connection.on_close = None
                try:
                    await connection.close()
                finally:
                    connection.on_close = on_close
            else:
                await connection.close()
            self.connection = None
            self.mode = None


class ScrapliConfig(ModeBoundConnection):
    """Scrapli connection plugin for nornir"""

    connection_name = "scrapli_cfg"

    @staticmethod
    def get_connection(task: Task) -> Any:
        """
        Try to fetch scrapli-cfg conn, create it if it doesnt exist

        This is a little different than "normal" in that we dont have a connection and we dont
        create them in the "normal" nornir way -- we actually just steal the scrapli connection and
        wrap the scrapli_cfg bits around it.

        Args:
            task: nornir Task object

        Returns:
            ScrapliCfg

        """
        if "scrapli_cfg" not in task.host.connections:
            cli = ScrapliCore.get_connection(task)
            options = task.host.get_connection_parameters("scrapli_cfg")
            task.host.open_connection(
                "scrapli_cfg", task.nornir.config, extras={**(options.extras or {}), "conn": cli}
            )
        connection = task.host.get_connection("scrapli_cfg", task.nornir.config)
        plugin = task.host.connections["scrapli_cfg"]
        if isinstance(plugin, ModeBoundConnection):
            plugin.require_mode("sync")
        ScrapliConfig._require_current_cli(task, connection)
        return connection

    @staticmethod
    async def aget_connection(task: Task) -> Any:
        """Acquire a configuration wrapper around the shared async CLI driver.

        Args:
            task: nornir Task object

        Returns:
            The prepared asynchronous Scrapli-Cfg wrapper

        """
        if "scrapli_cfg" not in task.host.connections:
            cli = await ScrapliCore.aget_connection(task)
            options = task.host.get_connection_parameters("scrapli_cfg")
            await task.host.aopen_connection(
                "scrapli_cfg", task.nornir.config, extras={**(options.extras or {}), "conn": cli}
            )
        connection = await task.host.aget_connection("scrapli_cfg", task.nornir.config)
        plugin = task.host.connections["scrapli_cfg"]
        if isinstance(plugin, ModeBoundConnection):
            plugin.require_mode("asyncio")
        ScrapliConfig._require_current_cli(task, connection)
        return connection

    @staticmethod
    def _require_current_cli(task: Task, connection: Any) -> None:
        cli_plugin = task.host.connections.get(CONNECTION_NAME)
        if cli_plugin is None or connection.conn is not cli_plugin.connection:
            raise NornirScrapliException(
                "Connection 'scrapli_cfg' wraps a closed or replaced 'scrapli' driver. "
                "Close the configuration wrapper using its matching lifecycle method "
                "before reopening it on the current CLI connection."
            )

    @staticmethod
    def spawn(task: Task) -> "ScrapliConfig":
        """
        Spawn a ScrapliConfig object for a nornir host

        This is a little different than "normal" in that we dont have a connection and we dont
        create them in the "normal" nornir way -- we actually just steal the scrapli connection and
        wrap the scrapli_cfg bits around it.

        Args:
            task: nornir Task object

        Returns:
            ScrapliConfig

        """
        scrapli_conn = ScrapliCore.get_connection(task)
        scrapli_cfg_parameters = task.host.get_connection_parameters(connection="scrapli_cfg")

        # should always be a dict afaik, but typing doesnt appreciate the possibility it is None
        extras = dict(scrapli_cfg_parameters.extras or {})
        # always overwrite `dedicated_connection` as we are *not* having a dedicated connection
        # since we are wrapping the "normal" scrapli connection!
        extras["dedicated_connection"] = False

        final_scrapli_cfg_parameters: Dict[str, Any] = {
            "conn": scrapli_conn,
            **extras,
        }
        scrapli_config_connection_obj = ScrapliConfig()
        scrapli_config_connection_obj.open(
            None, None, None, None, None, extras=final_scrapli_cfg_parameters
        )
        return scrapli_config_connection_obj

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
        Override open method of normal nornir connection so we can coopt an existing conn

        Args:
            hostname: unused; supplied by Nornir
            username: unused; supplied by Nornir
            password: unused; supplied by Nornir
            port: unused; supplied by Nornir
            platform: unused; supplied by Nornir
            extras: configuration options including the shared driver under conn
            configuration: unused; supplied by Nornir

        Returns:
            None

        """
        self.require_unopened("sync")
        parameters = self._parameters(extras)
        connection = ScrapliCfg(**parameters)
        connection.prepare()
        self.connection = connection
        self.mode = "sync"

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
        """Prepare an async wrapper without taking ownership of its CLI transport.

        Args:
            hostname: unused; supplied by Nornir
            username: unused; supplied by Nornir
            password: unused; supplied by Nornir
            port: unused; supplied by Nornir
            platform: unused; supplied by Nornir
            extras: configuration options including the shared driver under conn
            configuration: unused; supplied by Nornir

        """
        self.require_unopened("asyncio")
        parameters = self._parameters(extras)
        connection = AsyncScrapliCfg(**parameters)
        await connection.prepare()
        self.connection = connection
        self.mode = "asyncio"

    @staticmethod
    def _parameters(extras: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        parameters = {**(extras or {}), "dedicated_connection": False}
        if "conn" not in parameters:
            raise NornirScrapliException(
                "scrapli_cfg requires a shared CLI driver. Use ScrapliConfig.get_connection(task) "
                "or await ScrapliConfig.aget_connection(task)."
            )
        return parameters

    def close(self) -> None:
        """Release the sync wrapper without closing its shared CLI driver."""
        self.require_mode("sync")
        self.connection = None
        self.mode = None

    async def aclose(self) -> None:
        """Release the async wrapper without closing its shared CLI driver."""
        self.require_mode("asyncio")
        self.connection = None
        self.mode = None


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
            None

        """
        # platform is irrelevant for scrapli netconf for now
        _ = platform
        extras = extras or {}
        # 99.9% configuration will always be passed here... but to be consistent w/ the other
        # plugins we'll leave the function signature same/same as the others
        global_config = configuration.dict() if configuration else {}

        parameters: Dict[str, Any] = {
            "host": hostname,
            "auth_username": username or "",
            "auth_password": password or "",
            "port": port or 830,
            "ssh_config_file": global_config.get("ssh", {}).get("config_file", False),
        }

        # will override any of the configs from global nornir config (such as ssh config file) with
        # options from "extras" (connection options)
        parameters.update(extras)

        connection = NetconfDriver(**parameters)
        connection.open()
        self.connection = connection

    def close(self) -> None:
        """
        Close a scrapli netconf connection to a device

        Returns:
            None

        """
        self.connection.close()
