<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module nornir_scrapli.connection

nornir_scrapli.connection

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""nornir_scrapli.connection"""
from typing import Any, Dict, Optional

from scrapli import Scrapli
from scrapli.driver import GenericDriver
from scrapli.exceptions import ScrapliModuleNotFound
from scrapli_netconf.driver import NetconfDriver

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
            except ScrapliModuleNotFound as exc:
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
        </code>
    </pre>
</details>




## Classes

### ScrapliCore


```text
Scrapli connection plugin for nornir
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
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
            except ScrapliModuleNotFound as exc:
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
        </code>
    </pre>
</details>


#### Methods

    

##### close
`close(self) ‑> NoneType`

```text
Close a scrapli connection to a device

Args:
    N/A

Returns:
    N/A  # noqa: DAR202

Raises:
    N/A
```



    

##### open
`open(self, hostname: Union[str, NoneType], username: Union[str, NoneType], password: Union[str, NoneType], port: Union[int, NoneType], platform: Union[str, NoneType], extras: Union[Dict[str, Any], NoneType] = None, configuration: Union[nornir.core.configuration.Config, NoneType] = None) ‑> NoneType`

```text
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
```





### ScrapliNetconf


```text
Scrapli NETCONF connection plugin for nornir
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
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
        </code>
    </pre>
</details>


#### Methods

    

##### close
`close(self) ‑> NoneType`

```text
Close a scrapli netconf connection to a device

Args:
    N/A

Returns:
    N/A  # noqa: DAR202

Raises:
    N/A
```



    

##### open
`open(self, hostname: Union[str, NoneType], username: Union[str, NoneType], password: Union[str, NoneType], port: Union[int, NoneType], platform: Union[str, NoneType], extras: Union[Dict[str, Any], NoneType] = None, configuration: Union[nornir.core.configuration.Config, NoneType] = None) ‑> NoneType`

```text
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
```