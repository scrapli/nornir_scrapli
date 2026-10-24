"""Send CLI configuration from a file with scrapli v2."""

from typing import Optional

from scrapli.cli import InputHandling
from scrapli.ffi_types import Cancel

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult, process_config_result
from nornir_scrapli.tasks.core.mode import check_config_mode


def send_configs_from_file(
    task: Task,
    file: str,
    dry_run: Optional[bool] = None,
    *,
    requested_mode: str = "configuration",
    input_handling: InputHandling = InputHandling.FUZZY,
    retain_trailing_prompt: bool = False,
    stop_on_indicated_failure: bool = True,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Send a configuration file or test mode transitions without reading the file.

    Args:
        task: Nornir task.
        file: Configuration file path.
        dry_run: Override the global dry-run setting.
        requested_mode: Configuration mode to use.
        input_handling: Native input matching strategy.
        retain_trailing_prompt: Retain trailing prompts in output.
        stop_on_indicated_failure: Stop at a definition failure indicator.
        operation_timeout_ns: Per-operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Formatted configuration result, or an unchanged dry-run result.
    """
    connection = task.host.get_connection("scrapli", task.nornir.config)
    if task.global_dry_run if dry_run is None else dry_run:
        check_config_mode(connection, requested_mode, operation_timeout_ns, cancel)
        return ScrapliResult(task.host, None)
    response = connection.send_inputs_from_file(
        f=file,
        requested_mode=requested_mode,
        input_handling=input_handling,
        retain_input=False,
        retain_trailing_prompt=retain_trailing_prompt,
        stop_on_indicated_failure=stop_on_indicated_failure,
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return ScrapliResult(task.host, process_config_result(response), response, changed=True)
