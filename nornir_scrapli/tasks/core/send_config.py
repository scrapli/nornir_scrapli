"""Send multiline CLI configuration with scrapli v2."""

from typing import Optional

from scrapli.cli import InputHandling
from scrapli.ffi_types import Cancel

from nornir.core.task import Result, Task
from nornir_scrapli.tasks.core.send_configs import send_configs


def send_config(
    task: Task,
    config: str,
    dry_run: Optional[bool] = None,
    *,
    requested_mode: str = "configuration",
    input_handling: InputHandling = InputHandling.FUZZY,
    retain_trailing_prompt: bool = False,
    stop_on_indicated_failure: bool = True,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Send each configuration line through the batch configuration task.

    Args:
        task: Nornir task.
        config: Multiline configuration text.
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
    return send_configs(
        task,
        config.splitlines(),
        dry_run,
        requested_mode=requested_mode,
        input_handling=input_handling,
        retain_trailing_prompt=retain_trailing_prompt,
        stop_on_indicated_failure=stop_on_indicated_failure,
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
