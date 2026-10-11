"""Answer a single CLI prompt with scrapli v2."""

from typing import Optional

from scrapli.cli import InputHandling
from scrapli.ffi_types import Cancel

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult


def send_prompted_input(
    task: Task,
    input_: str,
    prompt: str,
    prompt_pattern: str,
    response: str,
    *,
    requested_mode: str = "",
    abort_input: str = "",
    input_handling: InputHandling = InputHandling.FUZZY,
    hidden_response: bool = False,
    retain_trailing_prompt: bool = False,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Send an input and answer its single confirmation or authentication prompt.

    Args:
        task: Nornir task.
        input_: Initial input.
        prompt: Exact expected prompt, or empty when using a pattern.
        prompt_pattern: Expected prompt pattern, or empty when using exact text.
        response: Response to the prompt.
        requested_mode: Mode in which to start the operation.
        abort_input: Input to abort a failed prompted operation.
        input_handling: Native input matching strategy.
        hidden_response: Response is hidden, such as a password.
        retain_trailing_prompt: Retain the trailing prompt.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result with native prompted-operation output.
    """
    connection = task.host.get_connection("scrapli", task.nornir.config)
    native = connection.send_prompted_input(
        input_=input_,
        prompt=prompt,
        prompt_pattern=prompt_pattern,
        response=response,
        requested_mode=requested_mode,
        abort_input=abort_input,
        input_handling=input_handling,
        hidden_response=hidden_response,
        retain_trailing_prompt=retain_trailing_prompt,
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return ScrapliResult(task.host, native.result, native, changed=True)
