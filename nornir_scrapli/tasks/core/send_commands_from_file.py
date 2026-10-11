"""Send CLI commands from a file with scrapli v2."""

from typing import Optional

from scrapli.cli import InputHandling
from scrapli.ffi_types import Cancel

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult, process_command_result


def send_commands_from_file(
    task: Task,
    file: str,
    *,
    requested_mode: str = "",
    input_handling: InputHandling = InputHandling.FUZZY,
    retain_input: bool = False,
    retain_trailing_prompt: bool = False,
    stop_on_indicated_failure: bool = True,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Send file contents using the native file operation.

    Args:
        task: Nornir task.
        file: Path to the command file.
        requested_mode: Mode in which to send commands.
        input_handling: Native input matching strategy.
        retain_input: Retain echoed input in output.
        retain_trailing_prompt: Retain the trailing prompt.
        stop_on_indicated_failure: Stop at a definition failure indicator.
        operation_timeout_ns: Per-operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing joined command outputs.
    """
    connection = task.host.get_connection("scrapli", task.nornir.config)
    response = connection.send_inputs_from_file(
        f=file,
        requested_mode=requested_mode,
        input_handling=input_handling,
        retain_input=retain_input,
        retain_trailing_prompt=retain_trailing_prompt,
        stop_on_indicated_failure=stop_on_indicated_failure,
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return ScrapliResult(task.host, process_command_result(response), response)
