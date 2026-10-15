"""CLI task counterparts using native asynchronous Scrapli operations."""

import asyncio
from typing import Any, List, Optional, Tuple, Union

from nornir.core.task import Result, Task
from nornir_scrapli.exceptions import NornirScrapliNoConfigModeGenericDriver
from nornir_scrapli.result import ScrapliResult, process_command_result, process_config_result


async def get_prompt(task: Task) -> Result:
    """Get the current device prompt.

    Args:
        task: nornir task object

    Returns:
        The prompt in a Nornir result

    """
    conn = await task.host.aget_connection("scrapli", task.nornir.config)
    prompt = await conn.get_prompt()
    return Result(host=task.host, result=prompt, failed=False, changed=False)


async def send_command(
    task: Task,
    command: str,
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    timeout_ops: Optional[float] = None,
) -> Result:
    """Send a single command through an asynchronous connection.

    Args:
        task: nornir task object
        command: command to send
        strip_prompt: remove the prompt from output
        failed_when_contains: output strings indicating failure
        timeout_ops: operation timeout override

    Returns:
        Command output and the original Scrapli response

    """
    conn = await task.host.aget_connection("scrapli", task.nornir.config)
    response = await conn.send_command(
        command=command,
        strip_prompt=strip_prompt,
        failed_when_contains=failed_when_contains,
        timeout_ops=timeout_ops,
    )
    return ScrapliResult(
        host=task.host, result=process_command_result(response), scrapli_response=response
    )


async def send_commands(
    task: Task,
    commands: List[str],
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    stop_on_failed: bool = False,
    eager: bool = False,
    timeout_ops: Optional[float] = None,
) -> Result:
    """Send multiple commands through an asynchronous connection.

    Args:
        task: nornir task object
        commands: commands to send
        strip_prompt: remove prompts from output
        failed_when_contains: output strings indicating failure
        stop_on_failed: stop sending after a failed command
        eager: do not read a prompt after each command
        timeout_ops: per-command timeout override

    Returns:
        Combined output and the original Scrapli responses

    """
    conn = await task.host.aget_connection("scrapli", task.nornir.config)
    response = await conn.send_commands(
        commands=commands,
        strip_prompt=strip_prompt,
        failed_when_contains=failed_when_contains,
        stop_on_failed=stop_on_failed,
        eager=eager,
        timeout_ops=timeout_ops,
    )
    return ScrapliResult(
        host=task.host, result=process_command_result(response), scrapli_response=response
    )


async def send_commands_from_file(
    task: Task,
    file: str,
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    stop_on_failed: bool = False,
    eager: bool = False,
    timeout_ops: Optional[float] = None,
) -> Result:
    """Load a command file off the event loop, then send its commands natively.

    Args:
        task: nornir task object
        file: path to the command file
        strip_prompt: remove prompts from output
        failed_when_contains: output strings indicating failure
        stop_on_failed: stop sending after a failed command
        eager: do not read a prompt after each command
        timeout_ops: per-command timeout override

    Returns:
        Combined output and the original Scrapli responses

    """
    conn = await task.host.aget_connection("scrapli", task.nornir.config)
    commands = await asyncio.to_thread(
        conn._pre_send_from_file, file=file, caller="send_commands_from_file"
    )
    return await send_commands(
        task, commands, strip_prompt, failed_when_contains, stop_on_failed, eager, timeout_ops
    )


async def send_interactive(
    task: Task,
    interact_events: List[Tuple[str, str, Optional[bool]]],
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    privilege_level: str = "",
    timeout_ops: Optional[float] = None,
) -> Result:
    """Send an interactive sequence through an asynchronous connection.

    Args:
        task: nornir task object
        interact_events: input, expected response, and optional hidden flag tuples
        failed_when_contains: output strings indicating failure
        privilege_level: requested privilege level
        timeout_ops: operation timeout override

    Returns:
        A Nornir result containing the original response, matching the sync task

    """
    conn = await task.host.aget_connection("scrapli", task.nornir.config)
    response = await conn.send_interactive(
        interact_events=interact_events,
        failed_when_contains=failed_when_contains,
        privilege_level=privilege_level,
        timeout_ops=timeout_ops,
    )
    result = Result(host=task.host, result=response, failed=response.failed, changed=True)
    setattr(result, "scrapli_response", response)
    return result


async def _config_connection(task: Task, dry_run: Optional[bool]) -> Tuple[Any, bool]:
    if task.host.platform == "generic":
        raise NornirScrapliNoConfigModeGenericDriver("No config mode for 'generic' platform type")
    conn = await task.host.aget_connection("scrapli", task.nornir.config)
    is_dry_run = dry_run if dry_run is not None else task.global_dry_run
    if is_dry_run:
        await conn.acquire_priv("configuration")
        await conn.acquire_priv(conn.default_desired_privilege_level)
    return conn, is_dry_run


async def send_config(
    task: Task,
    config: str,
    dry_run: Optional[bool] = None,
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    stop_on_failed: bool = False,
    privilege_level: str = "",
    eager: bool = False,
    timeout_ops: Optional[float] = None,
) -> Result:
    """Send a configuration string, or verify config-mode access during dry run.

    Args:
        task: nornir task object
        config: configuration string, possibly multiline
        dry_run: override Nornir's global dry-run setting
        strip_prompt: remove prompts from output
        failed_when_contains: output strings indicating failure
        stop_on_failed: stop sending after a failed configuration
        privilege_level: requested configuration privilege level
        eager: do not read a prompt after each configuration
        timeout_ops: per-configuration timeout override

    Returns:
        Configuration output and the original Scrapli response

    """
    conn, is_dry_run = await _config_connection(task, dry_run)
    if is_dry_run:
        return ScrapliResult(host=task.host, result=None)
    response = await conn.send_config(
        config=config,
        strip_prompt=strip_prompt,
        failed_when_contains=failed_when_contains,
        stop_on_failed=stop_on_failed,
        privilege_level=privilege_level,
        eager=eager,
        timeout_ops=timeout_ops,
    )
    return ScrapliResult(
        host=task.host,
        result=process_config_result(response),
        scrapli_response=response,
        changed=True,
    )


async def send_configs(
    task: Task,
    configs: List[str],
    dry_run: Optional[bool] = None,
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    stop_on_failed: bool = False,
    privilege_level: str = "",
    eager: bool = False,
    timeout_ops: Optional[float] = None,
) -> Result:
    """Send configuration lines, or verify config-mode access during dry run.

    Args:
        task: nornir task object
        configs: configuration lines to send
        dry_run: override Nornir's global dry-run setting
        strip_prompt: remove prompts from output
        failed_when_contains: output strings indicating failure
        stop_on_failed: stop sending after a failed configuration
        privilege_level: requested configuration privilege level
        eager: do not read a prompt after each configuration
        timeout_ops: per-configuration timeout override

    Returns:
        Combined output and the original Scrapli responses

    """
    conn, is_dry_run = await _config_connection(task, dry_run)
    if is_dry_run:
        return ScrapliResult(host=task.host, result=None)
    response = await conn.send_configs(
        configs=configs,
        strip_prompt=strip_prompt,
        failed_when_contains=failed_when_contains,
        stop_on_failed=stop_on_failed,
        privilege_level=privilege_level,
        eager=eager,
        timeout_ops=timeout_ops,
    )
    return ScrapliResult(
        host=task.host,
        result=process_config_result(response),
        scrapli_response=response,
        changed=True,
    )


async def send_configs_from_file(
    task: Task,
    file: str,
    dry_run: Optional[bool] = None,
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    stop_on_failed: bool = False,
    privilege_level: str = "",
    eager: bool = False,
    timeout_ops: Optional[float] = None,
) -> Result:
    """Load a configuration file off the loop, then send its lines natively.

    A dry run verifies config-mode access without reading the file or sending it.

    Args:
        task: nornir task object
        file: path to the configuration file
        dry_run: override Nornir's global dry-run setting
        strip_prompt: remove prompts from output
        failed_when_contains: output strings indicating failure
        stop_on_failed: stop sending after a failed configuration
        privilege_level: requested configuration privilege level
        eager: do not read a prompt after each configuration
        timeout_ops: per-configuration timeout override

    Returns:
        Combined output and the original Scrapli responses

    """
    conn, is_dry_run = await _config_connection(task, dry_run)
    if is_dry_run:
        return ScrapliResult(host=task.host, result=None)
    configs = await asyncio.to_thread(
        conn._pre_send_from_file, file=file, caller="send_configs_from_file"
    )
    return await send_configs(
        task,
        configs,
        False,
        strip_prompt,
        failed_when_contains,
        stop_on_failed,
        privilege_level,
        eager,
        timeout_ops,
    )
