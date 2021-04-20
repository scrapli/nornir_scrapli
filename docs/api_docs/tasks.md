<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module nornir_scrapli.tasks

nornir_scrapli.tasks

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""nornir_scrapli.tasks"""
from nornir_scrapli.tasks.cfg.abort_config import cfg_abort_config
from nornir_scrapli.tasks.cfg.commit_config import cfg_commit_config
from nornir_scrapli.tasks.cfg.diff_config import cfg_diff_config
from nornir_scrapli.tasks.cfg.get_config import cfg_get_config
from nornir_scrapli.tasks.cfg.get_version import cfg_get_version
from nornir_scrapli.tasks.cfg.load_config import cfg_load_config
from nornir_scrapli.tasks.get_prompt import get_prompt
from nornir_scrapli.tasks.netconf.capabilities import netconf_capabilities
from nornir_scrapli.tasks.netconf.commit import netconf_commit
from nornir_scrapli.tasks.netconf.delete_config import netconf_delete_config
from nornir_scrapli.tasks.netconf.discard import netconf_discard
from nornir_scrapli.tasks.netconf.edit_config import netconf_edit_config
from nornir_scrapli.tasks.netconf.get import netconf_get
from nornir_scrapli.tasks.netconf.get_config import netconf_get_config
from nornir_scrapli.tasks.netconf.lock import netconf_lock
from nornir_scrapli.tasks.netconf.rpc import netconf_rpc
from nornir_scrapli.tasks.netconf.unlock import netconf_unlock
from nornir_scrapli.tasks.netconf.validate import netconf_validate
from nornir_scrapli.tasks.send_command import send_command
from nornir_scrapli.tasks.send_commands import send_commands
from nornir_scrapli.tasks.send_commands_from_file import send_commands_from_file
from nornir_scrapli.tasks.send_config import send_config
from nornir_scrapli.tasks.send_configs import send_configs
from nornir_scrapli.tasks.send_configs_from_file import send_configs_from_file
from nornir_scrapli.tasks.send_interactive import send_interactive

__all__ = (
    "cfg_abort_config",
    "cfg_commit_config",
    "cfg_diff_config",
    "cfg_get_config",
    "cfg_get_version",
    "cfg_load_config",
    "get_prompt",
    "netconf_capabilities",
    "netconf_commit",
    "netconf_delete_config",
    "netconf_discard",
    "netconf_edit_config",
    "netconf_get",
    "netconf_get_config",
    "netconf_lock",
    "netconf_rpc",
    "netconf_unlock",
    "netconf_validate",
    "send_command",
    "send_commands",
    "send_commands_from_file",
    "send_config",
    "send_configs",
    "send_configs_from_file",
    "send_interactive",
)
        </code>
    </pre>
</details>



## Functions

    

#### cfg_abort_config
`cfg_abort_config(task: nornir.core.task.Task) ‑> nornir.core.task.Result`

```text
Abort a device candidate config with scrapli-cfg

Args:
    task: nornir task object

Returns:
    Result: nornir result object with Result.result value set the string result of the
        load_config operation

Raises:
    N/A
```




    

#### cfg_commit_config
`cfg_commit_config(task: nornir.core.task.Task, source: str = 'running') ‑> nornir.core.task.Result`

```text
Commit a device candidate config with scrapli-cfg

Args:
    task: nornir task object
    source: name of the config source to commit against, generally running|startup

Returns:
    Result: nornir result object with Result.result value set the string result of the
        load_config operation

Raises:
    N/A
```




    

#### cfg_diff_config
`cfg_diff_config(task: nornir.core.task.Task, source: str = 'running') ‑> nornir.core.task.Result`

```text
Diff a device candidate config vs a source config with scrapli-cfg

The "device diff" is stored as the result. You can access the side by side or unified scrapli
cfg diffs via the "scrapli_response" object stored in the result!

Args:
    task: nornir task object
    source: name of the config source to commit against, generally running|startup

Returns:
    Result: nornir result object with Result.result value set the string result of the
        load_config operation

Raises:
    N/A
```




    

#### cfg_get_config
`cfg_get_config(task: nornir.core.task.Task, source: str = 'running') ‑> nornir.core.task.Result`

```text
Get device config with scrapli-cfg

Args:
    task: nornir task object
    source: config source to get

Returns:
    Result: nornir result object with Result.result value set to current prompt

Raises:
    N/A
```




    

#### cfg_get_version
`cfg_get_version(task: nornir.core.task.Task) ‑> nornir.core.task.Result`

```text
Get device version with scrapli-cfg

Args:
    task: nornir task object

Returns:
    Result: nornir result object with Result.result value set to current version of device

Raises:
    N/A
```




    

#### cfg_load_config
`cfg_load_config(task: nornir.core.task.Task, config: str, replace: bool = False, **kwargs: Any) ‑> nornir.core.task.Result`

```text
Load device config with scrapli-cfg

Note that `changed` will still be `False` because this is just loading a candidate config!

Args:
    task: nornir task object
    config: string of the configuration to load
    replace: replace the configuration or not, if false configuration will be loaded as a
        merge operation
    kwargs: additional kwargs that the implementing classes may need for their platform,
        see your specific platform for details

Returns:
    Result: nornir result object with Result.result value set the string result of the
        load_config operation

Raises:
    N/A
```




    

#### get_prompt
`get_prompt(task: nornir.core.task.Task) ‑> nornir.core.task.Result`

```text
Get current prompt from device using scrapli

Args:
    task: nornir task object

Returns:
    Result: nornir result object with Result.result value set to current prompt

Raises:
    N/A
```




    

#### netconf_capabilities
`netconf_capabilities(task: nornir.core.task.Task) ‑> nornir.core.task.Result`

```text
Retrieve the device config with scrapli_netconf

Args:
    task: nornir task object

Returns:
    Result: nornir result object with Result.result value set to a list of strings representing
        the device capabilities

Raises:
    N/A
```




    

#### netconf_commit
`netconf_commit(task: nornir.core.task.Task) ‑> nornir.core.task.Result`

```text
Commit the device config with scrapli_netconf

Args:
    task: nornir task object

Returns:
    Result: nornir result object with Result.result value set the string result of the
        get operation

Raises:
    N/A
```




    

#### netconf_delete_config
`netconf_delete_config(task: nornir.core.task.Task, target: str = 'candidate') ‑> nornir.core.task.Result`

```text
Send a "delete-config" rcp to the device with scrapli_netconf

Args:
    task: nornir task object
    target: configuration source to target; startup|candidate

Returns:
    Result: nornir result object with Result.result value set the string result of the
        delete operation

Raises:
    N/A
```




    

#### netconf_discard
`netconf_discard(task: nornir.core.task.Task) ‑> nornir.core.task.Result`

```text
Discard the device config with scrapli_netconf

Args:
    task: nornir task object

Returns:
    Result: nornir result object with Result.result value set the string result of the
        get operation

Raises:
    N/A
```




    

#### netconf_edit_config
`netconf_edit_config(task: nornir.core.task.Task, config: str, dry_run: Optional[bool] = None, diff: bool = False, target: str = 'running') ‑> nornir.core.task.Result`

```text
Edit config from the device with scrapli_netconf

Args:
    task: nornir task object
    config: configuration to send to device
    dry_run: if True config will be pushed and then discarded; will discard anything already
        pushed that has *not* been committed already, so be careful! :D; also note that this
        will only work if there is a candidate datastore -- meaning that, for example, with
        IOSXE with a target of "running" there is no way to discard the configuration as it will
        already have been written to the running datastore
    diff: capture/set diff of target datastore xml text of before/after edit config operation
    target: configuration source to target; running|startup|candidate

Returns:
    Result: nornir result object with Result.result value set the string result of the
        get_config operation

Raises:
    N/A
```




    

#### netconf_get
`netconf_get(task: nornir.core.task.Task, filter_: str, filter_type: str = 'subtree') ‑> nornir.core.task.Result`

```text
Get from the device with scrapli_netconf

Args:
    task: nornir task object
    filter_: string filter to apply to the get
    filter_type: type of filter; subtree|xpath

Returns:
    Result: nornir result object with Result.result value set the string result of the
        get operation

Raises:
    N/A
```




    

#### netconf_get_config
`netconf_get_config(task: nornir.core.task.Task, source: str = 'running', filters: Union[str, List[str], NoneType] = None, filter_type: str = 'subtree') ‑> nornir.core.task.Result`

```text
Get config from the device with scrapli_netconf

Args:
    task: nornir task object
    source: configuration source to get; typically one of running|startup|candidate
    filters: string or list of strings of filters to apply to configuration
    filter_type: type of filter; subtree|xpath

Returns:
    Result: nornir result object with Result.result value set the string result of the
        get_config operation

Raises:
    N/A
```




    

#### netconf_lock
`netconf_lock(task: nornir.core.task.Task, target: str) ‑> nornir.core.task.Result`

```text
Lock the device with scrapli_netconf

Args:
    task: nornir task object
    target: configuration source to target; running|startup|candidate

Returns:
    Result: nornir result object with Result.result value set the string result of the
        get operation

Raises:
    N/A
```




    

#### netconf_rpc
`netconf_rpc(task: nornir.core.task.Task, filter_: str) ‑> nornir.core.task.Result`

```text
Send a "bare" rcp to the device with scrapli_netconf

Args:
    task: nornir task object
    filter_: filter/rpc to execute

Returns:
    Result: nornir result object with Result.result value set the string result of the
        rpc operation

Raises:
    N/A
```




    

#### netconf_unlock
`netconf_unlock(task: nornir.core.task.Task, target: str) ‑> nornir.core.task.Result`

```text
Unlock the device with scrapli_netconf

Args:
    task: nornir task object
    target: configuration source to target; running|startup|candidate

Returns:
    Result: nornir result object with Result.result value set the string result of the
        get operation

Raises:
    N/A
```




    

#### netconf_validate
`netconf_validate(task: nornir.core.task.Task, source: str) ‑> nornir.core.task.Result`

```text
Send a "validate" rcp to the device with scrapli_netconf

Args:
    task: nornir task object
    source: configuration source to validate; typically one of running|startup|candidate

Returns:
    Result: nornir result object with Result.result value set the string result of the
        get operation

Raises:
    N/A
```




    

#### send_command
`send_command(task: nornir.core.task.Task, command: str, strip_prompt: bool = True, failed_when_contains: Union[str, List[str], NoneType] = None, timeout_ops: Optional[float] = None) ‑> nornir.core.task.Result`

```text
Send a single command to device using scrapli

Args:
    task: nornir task object
    command: string to send to device in privilege exec mode
    strip_prompt: True/False strip prompt from returned output
    failed_when_contains: string or list of strings indicating failure if found in response
    timeout_ops: timeout ops value for this operation; only sets the timeout_ops value for
        the duration of the operation, value is reset to initial value after operation is
        completed

Returns:
    Result: scrapli nornir result object; almost identical to a "normal" nornir result object,
        but contains an additional attribute "scrapli_response" that contains the original
        response from scrapli

Raises:
    N/A
```




    

#### send_commands
`send_commands(task: nornir.core.task.Task, commands: List[str], strip_prompt: bool = True, failed_when_contains: Union[str, List[str], NoneType] = None, stop_on_failed: bool = False, eager: bool = False, timeout_ops: Optional[float] = None) ‑> nornir.core.task.Result`

```text
Send a list of commands to device using scrapli

Args:
    task: nornir task object
    commands: list of strings to send to device in privilege exec mode
    strip_prompt: True/False strip prompt from returned output
    failed_when_contains: string or list of strings indicating failure if found in response
    stop_on_failed: True/False stop executing commands if a command fails, returns results as of
        current execution
    eager: if eager is True we do not read until prompt is seen at each command sent to the
        channel. Do *not* use this unless you know what you are doing as it is possible that
        it can make scrapli less reliable!
    timeout_ops: timeout ops value for this operation; only sets the timeout_ops value for
        the duration of the operation, value is reset to initial value after operation is
        completed. Note that this is the timeout value PER COMMAND sent, not for the total
        of the commands being sent!

Returns:
    Result: nornir result object with Result.result value set to returned scrapli Response
        object

Raises:
    N/A
```




    

#### send_commands_from_file
`send_commands_from_file(task: nornir.core.task.Task, file: str, strip_prompt: bool = True, failed_when_contains: Union[str, List[str], NoneType] = None, stop_on_failed: bool = False, eager: bool = False, timeout_ops: Optional[float] = None) ‑> nornir.core.task.Result`

```text
Send a list of commands from a file to device using scrapli

Args:
    task: nornir task object
    file: string path to file
    strip_prompt: True/False strip prompt from returned output
    failed_when_contains: string or list of strings indicating failure if found in response
    stop_on_failed: True/False stop executing commands if a command fails, returns results as of
        current execution
    eager: if eager is True we do not read until prompt is seen at each command sent to the
        channel. Do *not* use this unless you know what you are doing as it is possible that
        it can make scrapli less reliable!
    timeout_ops: timeout ops value for this operation; only sets the timeout_ops value for
        the duration of the operation, value is reset to initial value after operation is
        completed

Returns:
    Result: nornir result object with Result.result value set to returned scrapli Response
        object

Raises:
    N/A
```




    

#### send_config
`send_config(task: nornir.core.task.Task, config: str, dry_run: Optional[bool] = None, strip_prompt: bool = True, failed_when_contains: Union[str, List[str], NoneType] = None, stop_on_failed: bool = False, privilege_level: str = '', eager: bool = False, timeout_ops: Optional[float] = None) ‑> nornir.core.task.Result`

```text
Send a config to device using scrapli

Args:
    task: nornir task object
    config: string configuration to send to the device, supports sending multi-line strings
    dry_run: Whether to apply changes or not; if dry run, will ensure that it is possible to
        enter config mode, but will NOT send any configs
    strip_prompt: True/False strip prompt from returned output
    failed_when_contains: string or list of strings indicating failure if found in response
    stop_on_failed: True/False stop executing commands if a command fails, returns results as of
        current execution
    privilege_level: name of configuration privilege level/type to acquire; this is platform
        dependent, so check the device driver for specifics. Examples of privilege_name
        would be "configuration_exclusive" for IOSXRDriver, or "configuration_private" for
        JunosDriver. You can also pass in a name of a configuration session such as
        "my-config-session" if you have registered a session using the
        "register_config_session" method of the EOSDriver or NXOSDriver.
    eager: if eager is True we do not read until prompt is seen at each command sent to the
         channel. Do *not* use this unless you know what you are doing as it is possible that
         it can make scrapli less reliable!
    timeout_ops: timeout ops value for this operation; only sets the timeout_ops value for
        the duration of the operation, value is reset to initial value after operation is
        completed. Note that this is the timeout value PER CONFIG sent, not for the total
        of the configs being sent!

Returns:
    Result: nornir result object with Result.result value set to returned scrapli Response
        object

Raises:
    NornirScrapliNoConfigModeGenericDriver: If attempting to use this task function against a
        host that is using the "generic" platform type
```




    

#### send_configs
`send_configs(task: nornir.core.task.Task, configs: List[str], dry_run: Optional[bool] = None, strip_prompt: bool = True, failed_when_contains: Union[str, List[str], NoneType] = None, stop_on_failed: bool = False, privilege_level: str = '', eager: bool = False, timeout_ops: Optional[float] = None) ‑> nornir.core.task.Result`

```text
Send configs to device using scrapli

Args:
    task: nornir task object
    configs: list of strings to send to device in config mode
    dry_run: Whether to apply changes or not; if dry run, will ensure that it is possible to
        enter config mode, but will NOT send any configs
    strip_prompt: True/False strip prompt from returned output
    failed_when_contains: string or list of strings indicating failure if found in response
    stop_on_failed: True/False stop executing commands if a command fails, returns results as of
        current execution
    privilege_level: name of configuration privilege level/type to acquire; this is platform
        dependent, so check the device driver for specifics. Examples of privilege_name
        would be "configuration_exclusive" for IOSXRDriver, or "configuration_private" for
        JunosDriver. You can also pass in a name of a configuration session such as
        "my-config-session" if you have registered a session using the
        "register_config_session" method of the EOSDriver or NXOSDriver.
    eager: if eager is True we do not read until prompt is seen at each command sent to the
        channel. Do *not* use this unless you know what you are doing as it is possible that
        it can make scrapli less reliable!
    timeout_ops: timeout ops value for this operation; only sets the timeout_ops value for
        the duration of the operation, value is reset to initial value after operation is
        completed. Note that this is the timeout value PER CONFIG sent, not for the total
        of the configs being sent!

Returns:
    Result: nornir result object with Result.result value set to returned scrapli Response
        object

Raises:
    NornirScrapliNoConfigModeGenericDriver: If attempting to use this task function against a
        host that is using the "generic" platform type
```




    

#### send_configs_from_file
`send_configs_from_file(task: nornir.core.task.Task, file: str, dry_run: Optional[bool] = None, strip_prompt: bool = True, failed_when_contains: Union[str, List[str], NoneType] = None, stop_on_failed: bool = False, privilege_level: str = '', eager: bool = False, timeout_ops: Optional[float] = None) ‑> nornir.core.task.Result`

```text
Send configs from a file to device using scrapli

Args:
    task: nornir task object
    file: string path to file
    dry_run: Whether to apply changes or not; if dry run, will ensure that it is possible to
        enter config mode, but will NOT send any configs
    strip_prompt: True/False strip prompt from returned output
    failed_when_contains: string or list of strings indicating failure if found in response
    stop_on_failed: True/False stop executing commands if a command fails, returns results as of
        current execution
    privilege_level: name of configuration privilege level/type to acquire; this is platform
        dependent, so check the device driver for specifics. Examples of privilege_name
        would be "configuration_exclusive" for IOSXRDriver, or "configuration_private" for
        JunosDriver. You can also pass in a name of a configuration session such as
        "my-config-session" if you have registered a session using the
        "register_config_session" method of the EOSDriver or NXOSDriver.
    eager: if eager is True we do not read until prompt is seen at each command sent to the
        channel. Do *not* use this unless you know what you are doing as it is possible that
        it can make scrapli less reliable!
    timeout_ops: timeout ops value for this operation; only sets the timeout_ops value for
        the duration of the operation, value is reset to initial value after operation is
        completed. Note that this is the timeout value PER CONFIG sent, not for the total
        of the configs being sent!

Returns:
    Result: nornir result object with Result.result value set to returned scrapli Response
        object

Raises:
    NornirScrapliNoConfigModeGenericDriver: If attempting to use this task function against a
        host that is using the "generic" platform type
```




    

#### send_interactive
`send_interactive(task: nornir.core.task.Task, interact_events: List[Tuple[str, str, Optional[bool]]], failed_when_contains: Union[str, List[str], NoneType] = None, privilege_level: str = '', timeout_ops: Optional[float] = None) ‑> nornir.core.task.Result`

```text
Send inputs in an interactive fashion using scrapli; usually used to handle prompts

Used to interact with devices where prompts change per input, and where inputs may be hidden
such as in the case of a password input. This can be used to respond to challenges from
devices such as the confirmation for the command "clear logging" on IOSXE devices for
example. You may have as many elements in the "interact_events" list as needed, and each
element of that list should be a tuple of two or three elements. The first element is always
the input to send as a string, the second should be the expected response as a string, and
the optional third a bool for whether or not the input is "hidden" (i.e. password input)
An example where we need this sort of capability:

```
3560CX#copy flash: scp:
Source filename []? test1.txt
Address or name of remote host []? 172.31.254.100
Destination username [carl]?
Writing test1.txt
Password:
Password:
 Sink: C0644 639 test1.txt
!
639 bytes copied in 12.066 secs (53 bytes/sec)
3560CX#
```

To accomplish this we can use the following (in "native" scrapli):

```
interact = conn.channel.send_inputs_interact(
    [
        ("copy flash: scp:", "Source filename []?", False),
        ("test1.txt", "Address or name of remote host []?", False),
        ("172.31.254.100", "Destination username [carl]?", False),
        ("carl", "Password:", False),
        ("super_secure_password", prompt, True),
    ]
)
```

If we needed to deal with more prompts we could simply continue adding tuples to the list of
interact "events".

Args:
    task: nornir task object
    interact_events: list of tuples containing the "interactions" with the device
        each list element must have an input and an expected response, and may have an
        optional bool for the third and final element -- the optional bool specifies if the
        input that is sent to the device is "hidden" (ex: password), if the hidden param is
        not provided it is assumed the input is "normal" (not hidden)
    failed_when_contains: list of strings that, if present in final output, represent a
        failed command/interaction
    privilege_level: name of the privilege level to operate in
    timeout_ops: timeout ops value for this operation; only sets the timeout_ops value for
        the duration of the operation, value is reset to initial value after operation is
        completed

Returns:
    Result: nornir result object with Result.result value set to returned scrapli Response
        object

Raises:
    N/A
```