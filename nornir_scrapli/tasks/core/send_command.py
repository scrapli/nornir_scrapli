"""Send a CLI command with scrapli v2."""

from typing import Optional

from scrapli.cli import InputHandling
from scrapli.ffi_types import Cancel

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult, process_command_result


def send_command(
    task: Task,
    command: str,
    *,
    requested_mode: str = "",
    input_handling: InputHandling = InputHandling.FUZZY,
    retain_input: bool = False,
    retain_trailing_prompt: bool = False,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Send one command and retain its native result.

    Args:
        task: Nornir task.
        command: Command to send.
        requested_mode: Mode in which to send the command.
        input_handling: Native input matching strategy.
        retain_input: Retain echoed input in output.
        retain_trailing_prompt: Retain the trailing prompt.
        operation_timeout_ns: Per-operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing command output.
    """
    connection = task.host.get_connection("scrapli", task.nornir.config)
    response = connection.send_input(
        input_=command,
        requested_mode=requested_mode,
        input_handling=input_handling,
        retain_input=retain_input,
        retain_trailing_prompt=retain_trailing_prompt,
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return ScrapliResult(task.host, process_command_result(response), response)
