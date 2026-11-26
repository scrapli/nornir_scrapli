"""Get a CLI prompt with scrapli v2."""

from typing import Optional

from scrapli.ffi_types import Cancel

from nornir.core.task import Task
from nornir_scrapli.result import ScrapliResult


async def get_prompt(
    task: Task,
    *,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> ScrapliResult:
    """Read the prompt and expose the native operation result.

    Args:
        task: Nornir task.
        operation_timeout_ns: Per-operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing the prompt string.
    """
    connection = await task.host.aget_connection("scrapli", task.nornir.config)
    response = await connection.get_prompt_async(
        operation_timeout_ns=operation_timeout_ns, cancel=cancel
    )
    return ScrapliResult(task.host, response.result, response)
