from typing import Any, Dict, Optional

from nornir.core.configuration import Config
from nornir.core.connections import ConnectionPlugin, Connections

from scrapli.driver.core import IOSXEDriver, NXOSDriver, IOSXRDriver, EOSDriver, JunosDriver

CONNECTION_NAME = "scrapli"
PLATFORM_MAP = {"": IOSXEDriver, "": NXOSDriver, "": IOSXRDriver, "": EOSDriver, "": JunosDriver}


class Scrapli(ConnectionPlugin):
    """
    This plugin connects to the device using scrapli and sets the relevant connection.

    Inventory:
        extras: passed as it is to the napalm driver

    """

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
        extras = extras or {}

        parameters: Dict[str, Any] = {
            "hostname": hostname,
            "username": username,
            "password": password,
            "optional_args": {},
        }

        try:
            parameters["optional_args"][
                "ssh_config_file"
            ] = configuration.ssh.config_file  # type: ignore
        except AttributeError:
            pass

        parameters.update(extras)

        if port and "port" not in parameters["optional_args"]:
            parameters["optional_args"]["port"] = port

        network_driver = get_network_driver(platform)
        connection = network_driver(**parameters)
        connection.open()
        self.connection = connection

    def close(self) -> None:
        self.connection.close()


if CONNECTION_NAME not in Connections.available:
    Connections.register(CONNECTION_NAME, Scrapli)
