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
from typing import TYPE_CHECKING, Any, Dict, Optional

from scrapli import Scrapli
from scrapli.driver import GenericDriver
from scrapli.exceptions import ScrapliModuleNotFound
from scrapli_cfg import ScrapliCfg
from scrapli_cfg.platform.base.sync_platform import ScrapliCfgPlatform
from scrapli_netconf.driver import NetconfDriver

from nornir.core.configuration import Config
from nornir.core.task import Task
from nornir_scrapli.exceptions import NornirScrapliInvalidPlatform

if TYPE_CHECKING:
    from nornir.core.plugins.connections import ConnectionPlugin  # pylint: disable=C0412

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
            None

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
        self.connection = connection  # pylint: disable=W0201

    def close(self) -> None:
        """
        Close a scrapli connection to a device

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self.connection.close()


class ScrapliConfig:
    """Scrapli connection plugin for nornir"""

    connection: ScrapliCfgPlatform

    @staticmethod
    def get_connection(task: Task) -> ScrapliCfgPlatform:
        """
        Try to fetch scrapli-cfg conn, create it if it doesnt exist

        This is a little different than "normal" in that we dont have a connection and we dont
        create them in the "normal" nornir way -- we actually just steal the scrapli connection and
        wrap the scrapli_cfg bits around it.

        Args:
            task: nornir Task object

        Returns:
            ScrapliCfg

        Raises:
            N/A

        """
        connection: ScrapliCfgPlatform

        try:
            connection = task.host.get_connection("scrapli_cfg", task.nornir.config)
        except AttributeError:
            task.host.connections["scrapli_cfg"] = ScrapliConfig.spawn(task=task)
            connection = task.host.get_connection("scrapli_cfg", task.nornir.config)

        return connection

    @staticmethod
    def spawn(task: Task) -> "ConnectionPlugin":
        """
        Spawn a ScrapliConfig object for a nornir host

        This is a little different than "normal" in that we dont have a connection and we dont
        create them in the "normal" nornir way -- we actually just steal the scrapli connection and
        wrap the scrapli_cfg bits around it.

        Args:
            task: nornir Task object

        Returns:
            ScrapliConfig

        Raises:
            N/A

        """
        scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)
        scrapli_cfg_parameters = task.host.get_connection_parameters(connection="scrapli_cfg")

        # should always be a dict afaik, but typing doesnt appreciate the possibility it is None
        extras = scrapli_cfg_parameters.extras or {}
        # always overwrite `dedicated_connection` as we are *not* having a dedicated connection
        # since we are wrapping the "normal" scrapli connection!
        extras["dedicated_connection"] = False

        final_scrapli_cfg_parameters: Dict[str, Any] = {
            "conn": scrapli_conn,
            **extras,
        }
        connection = ScrapliCfg(**final_scrapli_cfg_parameters)
        scrapli_config_connection_obj = ScrapliConfig()
        scrapli_config_connection_obj.connection = connection
        scrapli_config_connection_obj.open()
        return scrapli_config_connection_obj

    def open(self, *args: Any, **kwargs: Any) -> None:
        """
        Override open method of normal nornir connection so we can coopt an existing conn

        Args:
            args: args for not dealing w/ overridden hings
            kwargs: kwargs for not dealing w/ overridden hings

        Returns:
            None

        Raises:
            N/A

        """
        _, _ = args, kwargs
        self.connection.prepare()

    def close(self) -> None:
        """
        Override close method of normal nornir connection so we never close things

        Never closing allows us to not accidentally step on the underlying "normal" scrapli conn

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """


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
            None

        Raises:
            N/A

        """
        self.connection.close()
        </code>
    </pre>
</details>




## Classes

### ScrapliConfig


```text
Scrapli connection plugin for nornir
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class ScrapliConfig:
    """Scrapli connection plugin for nornir"""

    connection: ScrapliCfgPlatform

    @staticmethod
    def get_connection(task: Task) -> ScrapliCfgPlatform:
        """
        Try to fetch scrapli-cfg conn, create it if it doesnt exist

        This is a little different than "normal" in that we dont have a connection and we dont
        create them in the "normal" nornir way -- we actually just steal the scrapli connection and
        wrap the scrapli_cfg bits around it.

        Args:
            task: nornir Task object

        Returns:
            ScrapliCfg

        Raises:
            N/A

        """
        connection: ScrapliCfgPlatform

        try:
            connection = task.host.get_connection("scrapli_cfg", task.nornir.config)
        except AttributeError:
            task.host.connections["scrapli_cfg"] = ScrapliConfig.spawn(task=task)
            connection = task.host.get_connection("scrapli_cfg", task.nornir.config)

        return connection

    @staticmethod
    def spawn(task: Task) -> "ConnectionPlugin":
        """
        Spawn a ScrapliConfig object for a nornir host

        This is a little different than "normal" in that we dont have a connection and we dont
        create them in the "normal" nornir way -- we actually just steal the scrapli connection and
        wrap the scrapli_cfg bits around it.

        Args:
            task: nornir Task object

        Returns:
            ScrapliConfig

        Raises:
            N/A

        """
        scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)
        scrapli_cfg_parameters = task.host.get_connection_parameters(connection="scrapli_cfg")

        # should always be a dict afaik, but typing doesnt appreciate the possibility it is None
        extras = scrapli_cfg_parameters.extras or {}
        # always overwrite `dedicated_connection` as we are *not* having a dedicated connection
        # since we are wrapping the "normal" scrapli connection!
        extras["dedicated_connection"] = False

        final_scrapli_cfg_parameters: Dict[str, Any] = {
            "conn": scrapli_conn,
            **extras,
        }
        connection = ScrapliCfg(**final_scrapli_cfg_parameters)
        scrapli_config_connection_obj = ScrapliConfig()
        scrapli_config_connection_obj.connection = connection
        scrapli_config_connection_obj.open()
        return scrapli_config_connection_obj

    def open(self, *args: Any, **kwargs: Any) -> None:
        """
        Override open method of normal nornir connection so we can coopt an existing conn

        Args:
            args: args for not dealing w/ overridden hings
            kwargs: kwargs for not dealing w/ overridden hings

        Returns:
            None

        Raises:
            N/A

        """
        _, _ = args, kwargs
        self.connection.prepare()

    def close(self) -> None:
        """
        Override close method of normal nornir connection so we never close things

        Never closing allows us to not accidentally step on the underlying "normal" scrapli conn

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        </code>
    </pre>
</details>


#### Class variables

    
`connection: scrapli_cfg.platform.base.sync_platform.ScrapliCfgPlatform`



#### Static methods

    

#### get_connection
`get_connection(task: nornir.core.task.Task) ‑> scrapli_cfg.platform.base.sync_platform.ScrapliCfgPlatform`

```text
Try to fetch scrapli-cfg conn, create it if it doesnt exist

This is a little different than "normal" in that we dont have a connection and we dont
create them in the "normal" nornir way -- we actually just steal the scrapli connection and
wrap the scrapli_cfg bits around it.

Args:
    task: nornir Task object

Returns:
    ScrapliCfg

Raises:
    N/A
```



    

#### spawn
`spawn(task: nornir.core.task.Task) ‑> ConnectionPlugin`

```text
Spawn a ScrapliConfig object for a nornir host

This is a little different than "normal" in that we dont have a connection and we dont
create them in the "normal" nornir way -- we actually just steal the scrapli connection and
wrap the scrapli_cfg bits around it.

Args:
    task: nornir Task object

Returns:
    ScrapliConfig

Raises:
    N/A
```


#### Methods

    

##### close
`close(self) ‑> NoneType`

```text
Override close method of normal nornir connection so we never close things

Never closing allows us to not accidentally step on the underlying "normal" scrapli conn

Args:
    N/A

Returns:
    None

Raises:
    N/A
```



    

##### open
`open(self, *args: Any, **kwargs: Any) ‑> NoneType`

```text
Override open method of normal nornir connection so we can coopt an existing conn

Args:
    args: args for not dealing w/ overridden hings
    kwargs: kwargs for not dealing w/ overridden hings

Returns:
    None

Raises:
    N/A
```





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
            None

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
        self.connection = connection  # pylint: disable=W0201

    def close(self) -> None:
        """
        Close a scrapli connection to a device

        Args:
            N/A

        Returns:
            None

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
    None

Raises:
    N/A
```



    

##### open
`open(self, hostname: Optional[str], username: Optional[str], password: Optional[str], port: Optional[int], platform: Optional[str], extras: Optional[Dict[str, Any]] = None, configuration: Optional[nornir.core.configuration.Config] = None) ‑> NoneType`

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
    None

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
            None

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
            None

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
    None

Raises:
    N/A
```



    

##### open
`open(self, hostname: Optional[str], username: Optional[str], password: Optional[str], port: Optional[int], platform: Optional[str], extras: Optional[Dict[str, Any]] = None, configuration: Optional[nornir.core.configuration.Config] = None) ‑> NoneType`

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
    None

Raises:
    N/A
```